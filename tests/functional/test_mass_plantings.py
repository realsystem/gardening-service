"""
Mass Plantings Stress Tests

Tests dense planting scenarios:
- Many plantings in single garden
- Mixed plant types (vegetables, herbs, trees, bushes)
- Planting list performance
- Complex garden compositions
"""
import pytest
import httpx
import time
from typing import List


class TestDensePlantings:
    """Test gardens with many plantings"""

    def test_garden_with_50_plantings(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Single garden with 50 different plantings"""
        # Create garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Dense Garden", "garden_type": "outdoor"}
        )
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        # Get plant varieties
        varieties_response = authenticated_client.get("/plant-varieties")
        varieties = varieties_response.json()

        assert len(varieties) >= 50, "Need at least 50 plant varieties for this test"

        # Create 50 planting events
        planting_ids = []
        for i in range(50):
            variety = varieties[i % len(varieties)]

            planting_data = {
                "garden_id": garden_id,
                "plant_variety_id": variety["id"],
                "quantity": 1 + (i % 10),  # 1-10 plants
                "planting_date": f"2026-0{(i % 5) + 1}-01"  # Spread across months
            }

            response = authenticated_client.post("/planting-events", json=planting_data)
            if response.status_code == 201:
                planting_ids.append(response.json()["id"])

        # Should have created most plantings
        assert len(planting_ids) >= 45, \
            f"Only created {len(planting_ids)}/50 plantings"

        # Test list performance
        start = time.time()
        list_response = authenticated_client.get("/planting-events")
        elapsed = time.time() - start

        assert list_response.status_code == 200
        plantings = list_response.json()

        assert len(plantings) >= 45
        assert elapsed < 2.0, \
            f"Listing {len(plantings)} plantings took {elapsed:.2f}s (should be <2s)"


class TestMixedPlantTypes:
    """Test gardens with diverse plant types"""

    def test_vegetable_herb_tree_mix(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Garden with vegetables, herbs, trees, and bushes"""
        # Create garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Mixed Garden", "garden_type": "outdoor"}
        )
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        # Get varieties by category
        varieties_response = authenticated_client.get("/plant-varieties")
        all_varieties = varieties_response.json()

        vegetables = [v for v in all_varieties if "vegetable" in (v.get("tags") or "")]
        herbs = [v for v in all_varieties if "herb" in (v.get("tags") or "")]
        trees = [v for v in all_varieties if "tree" in (v.get("tags") or "")]
        bushes = [v for v in all_varieties if "bush" in (v.get("tags") or "")]

        # Plant mix
        plantings_created = []

        # 10 vegetables
        for i in range(min(10, len(vegetables))):
            response = authenticated_client.post(
                "/planting-events",
                json={
                    "garden_id": garden_id,
                    "plant_variety_id": vegetables[i]["id"],
                    "quantity": 5
                }
            )
            if response.status_code == 201:
                plantings_created.append(response.json())

        # 5 herbs
        for i in range(min(5, len(herbs))):
            response = authenticated_client.post(
                "/planting-events",
                json={
                    "garden_id": garden_id,
                    "plant_variety_id": herbs[i]["id"],
                    "quantity": 3
                }
            )
            if response.status_code == 201:
                plantings_created.append(response.json())

        # 3 trees
        for i in range(min(3, len(trees))):
            response = authenticated_client.post(
                "/planting-events",
                json={
                    "garden_id": garden_id,
                    "plant_variety_id": trees[i]["id"],
                    "quantity": 1
                }
            )
            if response.status_code == 201:
                plantings_created.append(response.json())

        # 4 bushes
        for i in range(min(4, len(bushes))):
            response = authenticated_client.post(
                "/planting-events",
                json={
                    "garden_id": garden_id,
                    "plant_variety_id": bushes[i]["id"],
                    "quantity": 2
                }
            )
            if response.status_code == 201:
                plantings_created.append(response.json())

        # Verify diversity
        assert len(plantings_created) >= 18, \
            f"Only created {len(plantings_created)} plantings (expected 22)"

        # List and verify variety
        list_response = authenticated_client.get("/planting-events")
        plantings = list_response.json()

        # Extract plant variety info
        variety_ids = [p["plant_variety_id"] for p in plantings if p.get("garden_id") == garden_id]
        unique_varieties = len(set(variety_ids))

        assert unique_varieties >= 18, \
            f"Expected diverse plantings, only found {unique_varieties} unique varieties"


class TestPlantingPerformance:
    """Test performance with many plantings"""

    def test_create_30_plantings_quickly(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Creating 30 plantings should be reasonably fast"""
        # Create garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Performance Garden", "garden_type": "outdoor"}
        )
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        # Get varieties
        varieties = authenticated_client.get("/plant-varieties").json()

        # Time the creation of 30 plantings
        start = time.time()
        created_count = 0

        for i in range(30):
            variety = varieties[i % len(varieties)]
            response = authenticated_client.post(
                "/planting-events",
                json={
                    "garden_id": garden_id,
                    "plant_variety_id": variety["id"],
                    "quantity": 1
                }
            )
            if response.status_code == 201:
                created_count += 1

        elapsed = time.time() - start

        assert created_count >= 28, \
            f"Only created {created_count}/30 plantings"

        # Average time per planting should be reasonable
        avg_time = elapsed / created_count
        assert avg_time < 0.5, \
            f"Average planting creation took {avg_time:.2f}s (should be <0.5s)"


class TestMultipleGardensWithPlantings:
    """Test multiple gardens each with many plantings"""

    def test_5_gardens_10_plantings_each(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """5 gardens, each with 10 plantings"""
        varieties = authenticated_client.get("/plant-varieties").json()

        gardens_created = []
        total_plantings = 0

        for g_idx in range(5):
            # Create garden
            garden_response = authenticated_client.post(
                "/gardens",
                json={"name": f"Multi Garden {g_idx}", "garden_type": "outdoor"}
            )
            garden_id = garden_response.json()["id"]
            cleanup_gardens.append(garden_id)
            gardens_created.append(garden_id)

            # Add 10 plantings
            for p_idx in range(10):
                variety = varieties[(g_idx * 10 + p_idx) % len(varieties)]
                response = authenticated_client.post(
                    "/planting-events",
                    json={
                        "garden_id": garden_id,
                        "plant_variety_id": variety["id"],
                        "quantity": 2
                    }
                )
                if response.status_code == 201:
                    total_plantings += 1

        assert total_plantings >= 45, \
            f"Only created {total_plantings}/50 plantings across 5 gardens"

        # Verify data integrity
        all_plantings = authenticated_client.get("/planting-events").json()

        # Group by garden
        plantings_by_garden = {}
        for p in all_plantings:
            gid = p["garden_id"]
            plantings_by_garden[gid] = plantings_by_garden.get(gid, 0) + 1

        # Each of our gardens should have plantings
        for garden_id in gardens_created:
            assert garden_id in plantings_by_garden, \
                f"Garden {garden_id} has no plantings"
            assert plantings_by_garden[garden_id] >= 8, \
                f"Garden {garden_id} only has {plantings_by_garden[garden_id]} plantings"


class TestComplexScenarios:
    """Test complex real-world scenarios"""

    def test_permaculture_garden(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Permaculture design: mix of trees, bushes, and ground cover"""
        # Create garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={
                "name": "Permaculture Garden",
                "garden_type": "outdoor",
                "description": "Three-layer food forest"
            }
        )
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        varieties = authenticated_client.get("/plant-varieties").json()

        # Layer 1: Canopy trees
        trees = [v for v in varieties if "tree" in (v.get("tags") or "")]
        for i in range(min(3, len(trees))):
            authenticated_client.post(
                "/planting-events",
                json={
                    "garden_id": garden_id,
                    "plant_variety_id": trees[i]["id"],
                    "quantity": 1
                }
            )

        # Layer 2: Shrubs/bushes
        bushes = [v for v in varieties if "bush" in (v.get("tags") or "")]
        for i in range(min(5, len(bushes))):
            authenticated_client.post(
                "/planting-events",
                json={
                    "garden_id": garden_id,
                    "plant_variety_id": bushes[i]["id"],
                    "quantity": 2
                }
            )

        # Layer 3: Ground cover (herbs and low vegetables)
        herbs = [v for v in varieties if "herb" in (v.get("tags") or "")]
        for i in range(min(8, len(herbs))):
            authenticated_client.post(
                "/planting-events",
                json={
                    "garden_id": garden_id,
                    "plant_variety_id": herbs[i]["id"],
                    "quantity": 5
                }
            )

        # Verify layered structure
        plantings = authenticated_client.get("/planting-events").json()
        garden_plantings = [p for p in plantings if p["garden_id"] == garden_id]

        assert len(garden_plantings) >= 12, \
            "Permaculture garden should have multiple layers"


    def test_succession_planting(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Simulate succession planting: same variety multiple times"""
        # Create garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Succession Garden", "garden_type": "outdoor"}
        )
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        # Get a fast-growing variety (lettuce, radish, etc.)
        varieties = authenticated_client.get("/plant-varieties").json()
        fast_growers = [v for v in varieties if v.get("days_to_harvest") and v["days_to_harvest"] < 50]

        if len(fast_growers) == 0:
            pytest.skip("No fast-growing varieties available")

        variety = fast_growers[0]

        # Plant same variety 4 times (simulating succession)
        succession_dates = ["2026-04-01", "2026-04-15", "2026-05-01", "2026-05-15"]
        created = 0

        for date in succession_dates:
            response = authenticated_client.post(
                "/planting-events",
                json={
                    "garden_id": garden_id,
                    "plant_variety_id": variety["id"],
                    "quantity": 10,
                    "planting_date": date
                }
            )
            if response.status_code == 201:
                created += 1

        assert created == 4, \
            "Should allow succession planting of same variety"
