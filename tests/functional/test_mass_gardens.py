"""
Mass Gardens Stress Tests

Tests system with large numbers of gardens:
- Single user with 15 gardens
- Multiple garden types
- Listing performance
- Update/delete at scale
"""
import pytest
import httpx
import time


class TestMassGardenCreation:
    """Test creating many gardens"""

    def test_single_user_15_gardens(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Single user creates 15 gardens of various types"""
        garden_types = ["outdoor", "indoor", "indoor"]  # Cycle through types
        gardens_created = []

        for i in range(15):
            garden_data = {
                "name": f"Mass Test Garden {i+1}",
                "garden_type": garden_types[i % len(garden_types)],
                "description": f"Stress test garden number {i+1}"
            }

            if garden_types[i % len(garden_types)] == "indoor":
                garden_data["light_hours_per_day"] = 12 + (i % 5)

            response = authenticated_client.post("/gardens", json=garden_data)
            assert response.status_code == 201, \
                f"Failed to create garden {i+1}: {response.text}"

            garden = response.json()
            gardens_created.append(garden["id"])
            cleanup_gardens.append(garden["id"])

        # Verify all gardens are listable
        list_response = authenticated_client.get("/gardens")
        assert list_response.status_code == 200

        gardens = list_response.json()
        assert len(gardens) >= 15, \
            f"Expected at least 15 gardens, found {len(gardens)}"


    def test_garden_list_performance_with_many_gardens(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Verify garden listing is fast even with many gardens"""
        # Create 12 gardens quickly
        for i in range(12):
            response = authenticated_client.post(
                "/gardens",
                json={"name": f"Perf Garden {i}", "garden_type": "outdoor"}
            )
            cleanup_gardens.append(response.json()["id"])

        # Measure list performance
        start = time.time()
        response = authenticated_client.get("/gardens")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert len(response.json()) >= 12

        # Should list in under 1 second even with many gardens
        assert elapsed < 1.0, \
            f"Listing {len(response.json())} gardens took {elapsed:.2f}s (should be <1s)"


class TestMixedGardenTypes:
    """Test handling of mixed garden types"""

    def test_outdoor_indoor_hydro_mix(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Create mix of outdoor, indoor, and hydroponic gardens"""
        configs = [
            {
                "name": "Outdoor Veggie Patch",
                "garden_type": "outdoor",
                "description": "Traditional outdoor garden"
            },
            {
                "name": "Indoor Herb Garden",
                "garden_type": "indoor",
                "light_source_type": "led",
                "light_hours_per_day": 16.0
            },
            {
                "name": "Hydroponic Lettuce",
                "garden_type": "indoor",
                "is_hydroponic": True,
                "hydro_system_type": "nft",
                "ph_min": 5.5,
                "ph_max": 6.5
            },
            {
                "name": "Outdoor Fruit Garden",
                "garden_type": "outdoor"
            },
            {
                "name": "Indoor Microgreens",
                "garden_type": "indoor",
                "light_hours_per_day": 18.0
            }
        ]

        created_ids = []
        for config in configs:
            response = authenticated_client.post("/gardens", json=config)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])
            cleanup_gardens.append(response.json()["id"])

        # Verify all types are present
        list_response = authenticated_client.get("/gardens")
        gardens = list_response.json()

        outdoor_count = sum(1 for g in gardens if g["garden_type"] == "outdoor")
        indoor_count = sum(1 for g in gardens if g["garden_type"] == "indoor")
        hydro_count = sum(1 for g in gardens if g.get("is_hydroponic"))

        assert outdoor_count >= 2, f"Expected 2+ outdoor gardens, got {outdoor_count}"
        assert indoor_count >= 3, f"Expected 3+ indoor gardens, got {indoor_count}"
        assert hydro_count >= 1, f"Expected 1+ hydroponic garden, got {hydro_count}"


class TestGardenUpdatesAtScale:
    """Test updating many gardens"""

    def test_bulk_garden_updates(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Create 10 gardens and update all of them"""
        # Create 10 gardens
        garden_ids = []
        for i in range(10):
            response = authenticated_client.post(
                "/gardens",
                json={"name": f"Update Test {i}", "garden_type": "outdoor"}
            )
            garden_id = response.json()["id"]
            garden_ids.append(garden_id)
            cleanup_gardens.append(garden_id)

        # Update all gardens
        update_count = 0
        for i, garden_id in enumerate(garden_ids):
            response = authenticated_client.patch(
                f"/gardens/{garden_id}",
                json={"description": f"Updated description {i}"}
            )
            if response.status_code == 200:
                update_count += 1

        assert update_count == 10, \
            f"Only {update_count}/10 gardens updated successfully"

        # Verify updates
        for i, garden_id in enumerate(garden_ids):
            response = authenticated_client.get(f"/gardens/{garden_id}")
            garden = response.json()
            assert garden["description"] == f"Updated description {i}"


class TestGardenDeletionAtScale:
    """Test deleting many gardens"""

    def test_sequential_deletion(
        self,
        authenticated_client: httpx.Client
    ):
        """Create and delete 8 gardens sequentially"""
        for i in range(8):
            # Create
            create_response = authenticated_client.post(
                "/gardens",
                json={"name": f"Delete Test {i}", "garden_type": "outdoor"}
            )
            assert create_response.status_code == 201
            garden_id = create_response.json()["id"]

            # Immediately delete
            delete_response = authenticated_client.delete(f"/gardens/{garden_id}")
            assert delete_response.status_code == 204

            # Verify deleted
            get_response = authenticated_client.get(f"/gardens/{garden_id}")
            assert get_response.status_code == 404


class TestEdgeCases:
    """Test edge cases with many gardens"""

    def test_gardens_with_very_long_names(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Create gardens with long names"""
        long_name = "A" * 95  # Near typical varchar limit

        response = authenticated_client.post(
            "/gardens",
            json={"name": long_name, "garden_type": "outdoor"}
        )

        assert response.status_code == 201
        cleanup_gardens.append(response.json()["id"])

        # Verify name is preserved
        garden = response.json()
        assert garden["name"] == long_name


    def test_many_gardens_same_name(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """System should allow multiple gardens with same name"""
        name = "My Garden"

        for i in range(5):
            response = authenticated_client.post(
                "/gardens",
                json={"name": name, "garden_type": "outdoor"}
            )
            assert response.status_code == 201
            cleanup_gardens.append(response.json()["id"])

        # All should exist
        list_response = authenticated_client.get("/gardens")
        gardens_with_name = [g for g in list_response.json() if g["name"] == name]
        assert len(gardens_with_name) >= 5
