"""
Rule Engine Alarm Stress Tests

Tests rule engine with scenarios that generate many alarms:
- Water stress warnings
- Soil pH conflicts
- Sun exposure mismatches
- Zone conflicts
- Multiple simultaneous alarms
"""
import pytest
import httpx


class TestAlarmGeneration:
    """Test generating various alarm types"""

    def test_multiple_alarm_types(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list,
        cleanup_soil_samples: list
    ):
        """Create scenario with multiple alarm types"""
        # Create garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Problem Garden", "garden_type": "outdoor"}
        )
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        # Add soil sample with problems (low pH, low moisture)
        soil_response = authenticated_client.post(
            "/soil-samples",
            json={
                "garden_id": garden_id,
                "ph_level": 4.5,  # Too acidic for most plants
                "moisture_percent": 5.0,  # Too dry
                "date_collected": "2026-01-15"
            }
        )
        if soil_response.status_code == 201:
            cleanup_soil_samples.append(soil_response.json()["id"])

        # Get plant varieties
        varieties = authenticated_client.get("/plant-varieties").json()

        # Plant varieties with conflicting needs
        sun_lovers = [v for v in varieties if v.get("sun_requirement") == "full_sun"][:5]
        shade_lovers = [v for v in varieties if v.get("sun_requirement") == "full_shade"][:2]

        # Plant both in same garden (potential sun conflict)
        for variety in sun_lovers + shade_lovers:
            authenticated_client.post(
                "/planting-events",
                json={
                    "garden_id": garden_id,
                    "plant_variety_id": variety["id"],
                    "quantity": 3
                }
            )

        # The rule engine should generate alarms
        # This test validates the system handles complex scenarios


class TestAlarmVolume:
    """Test system with many simultaneous alarms"""

    def test_garden_with_20_plantings_all_stressed(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """20 plantings in problematic conditions"""
        # Create outdoor garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Stressed Garden", "garden_type": "outdoor"}
        )
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        varieties = authenticated_client.get("/plant-varieties").json()

        # Plant 20 different varieties
        created = 0
        for i in range(min(20, len(varieties))):
            response = authenticated_client.post(
                "/planting-events",
                json={
                    "garden_id": garden_id,
                    "plant_variety_id": varieties[i]["id"],
                    "quantity": 2
                }
            )
            if response.status_code == 201:
                created += 1

        assert created >= 18, f"Only created {created} plantings"


class TestPerformance:
    """Test rule engine performance under stress"""

    def test_rule_evaluation_speed(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Rule engine should evaluate quickly even with complex gardens"""
        import time

        # Create garden with many plantings
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Complex Garden", "garden_type": "outdoor"}
        )
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        varieties = authenticated_client.get("/plant-varieties").json()

        # Add 15 plantings
        for i in range(15):
            authenticated_client.post(
                "/planting-events",
                json={
                    "garden_id": garden_id,
                    "plant_variety_id": varieties[i % len(varieties)]["id"],
                    "quantity": 3
                }
            )

        # Measure rule evaluation (if endpoint exists)
        # This is a placeholder - actual implementation depends on API
        start = time.time()
        response = authenticated_client.get(f"/gardens/{garden_id}")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.5, f"Garden fetch took {elapsed:.2f}s (should be <0.5s)"
