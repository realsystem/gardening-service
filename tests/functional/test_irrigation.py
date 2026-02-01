"""Functional tests for irrigation system endpoints

These tests verify irrigation sources, zones, events, and garden assignments.
"""
from datetime import datetime, timedelta
import pytest
import httpx


@pytest.fixture
def test_garden(authenticated_client: httpx.Client, cleanup_gardens: list) -> dict:
    """Create a test garden for irrigation tests"""
    response = authenticated_client.post(
        "/gardens",
        json={"name": "Irrigation Test Garden", "garden_type": "outdoor"}
    )
    garden = response.json()
    cleanup_gardens.append(garden["id"])
    return garden


class TestIrrigationSources:
    """Test irrigation source endpoints"""

    def test_create_water_source_success(
        self,
        authenticated_client: httpx.Client,
        cleanup_irrigation_sources: list
    ):
        """Successfully create a water source"""
        source_data = {
            "name": "City Water",
            "source_type": "city",
            "flow_capacity_lpm": 50.0,
            "notes": "Main water line"
        }

        response = authenticated_client.post(
            "/irrigation-system/sources",
            json=source_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "City Water"
        assert data["source_type"] == "city"
        assert data["flow_capacity_lpm"] == 50.0
        assert "id" in data

        cleanup_irrigation_sources.append(data["id"])

    def test_list_water_sources(
        self,
        authenticated_client: httpx.Client,
        cleanup_irrigation_sources: list
    ):
        """List all water sources for user"""
        # Create 2 sources
        source1 = authenticated_client.post(
            "/irrigation-system/sources",
            json={"name": "City Water", "source_type": "city", "flow_capacity_lpm": 50.0}
        ).json()
        source2 = authenticated_client.post(
            "/irrigation-system/sources",
            json={"name": "Well", "source_type": "well", "flow_capacity_lpm": 30.0}
        ).json()

        cleanup_irrigation_sources.extend([source1["id"], source2["id"]])

        # List sources
        response = authenticated_client.get("/irrigation-system/sources")

        assert response.status_code == 200
        sources = response.json()
        assert len(sources) == 2
        assert any(s["name"] == "City Water" for s in sources)
        assert any(s["name"] == "Well" for s in sources)

    def test_delete_water_source(
        self,
        authenticated_client: httpx.Client
    ):
        """Successfully delete a water source"""
        source = authenticated_client.post(
            "/irrigation-system/sources",
            json={"name": "Temp Source", "source_type": "city", "flow_capacity_lpm": 40.0}
        ).json()

        response = authenticated_client.delete(
            f"/irrigation-system/sources/{source['id']}"
        )

        assert response.status_code == 204


class TestIrrigationZones:
    """Test irrigation zone endpoints"""

    def test_create_irrigation_zone_success(
        self,
        authenticated_client: httpx.Client,
        cleanup_irrigation_zones: list,
        cleanup_irrigation_sources: list
    ):
        """Successfully create an irrigation zone"""
        # Create water source first
        source = authenticated_client.post(
            "/irrigation-system/sources",
            json={"name": "City Water", "source_type": "city", "flow_capacity_lpm": 50.0}
        ).json()
        cleanup_irrigation_sources.append(source["id"])

        zone_data = {
            "name": "Vegetable Zone",
            "delivery_type": "drip",
            "water_source_id": source["id"],
            "schedule": {
                "frequency_days": 3,
                "duration_minutes": 30
            },
            "notes": "Drip irrigation for vegetables"
        }

        response = authenticated_client.post(
            "/irrigation-system/zones",
            json=zone_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Vegetable Zone"
        assert data["delivery_type"] == "drip"
        assert data["water_source_id"] == source["id"]
        assert data["schedule"]["frequency_days"] == 3

        cleanup_irrigation_zones.append(data["id"])

    def test_create_zone_without_source(
        self,
        authenticated_client: httpx.Client,
        cleanup_irrigation_zones: list
    ):
        """Can create irrigation zone without water source"""
        zone_data = {
            "name": "Manual Zone",
            "delivery_type": "soaker_hose",
            "schedule": {
                "frequency_days": 2,
                "duration_minutes": 20
            }
        }

        response = authenticated_client.post(
            "/irrigation-system/zones",
            json=zone_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["water_source_id"] is None

        cleanup_irrigation_zones.append(data["id"])

    def test_list_irrigation_zones(
        self,
        authenticated_client: httpx.Client,
        cleanup_irrigation_zones: list
    ):
        """List all irrigation zones"""
        # Create zones
        zone1 = authenticated_client.post(
            "/irrigation-system/zones",
            json={
                "name": "Zone 1",
                "delivery_type": "drip",
                "schedule": {"frequency_days": 3, "duration_minutes": 30}
            }
        ).json()
        zone2 = authenticated_client.post(
            "/irrigation-system/zones",
            json={
                "name": "Zone 2",
                "delivery_type": "sprinkler",
                "schedule": {"frequency_days": 2, "duration_minutes": 15}
            }
        ).json()

        cleanup_irrigation_zones.extend([zone1["id"], zone2["id"]])

        # List zones
        response = authenticated_client.get("/irrigation-system/zones")

        assert response.status_code == 200
        zones = response.json()
        assert len(zones) == 2

    def test_update_irrigation_zone(
        self,
        authenticated_client: httpx.Client,
        cleanup_irrigation_zones: list
    ):
        """Successfully update irrigation zone"""
        zone = authenticated_client.post(
            "/irrigation-system/zones",
            json={
                "name": "Test Zone",
                "delivery_type": "drip",
                "schedule": {"frequency_days": 3, "duration_minutes": 30}
            }
        ).json()
        cleanup_irrigation_zones.append(zone["id"])

        # Update zone
        update_data = {
            "schedule": {
                "frequency_days": 4,
                "duration_minutes": 45
            }
        }
        response = authenticated_client.patch(
            f"/irrigation-system/zones/{zone['id']}",
            json=update_data
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["schedule"]["frequency_days"] == 4
        assert updated["schedule"]["duration_minutes"] == 45

    def test_delete_irrigation_zone(
        self,
        authenticated_client: httpx.Client
    ):
        """Successfully delete irrigation zone"""
        zone = authenticated_client.post(
            "/irrigation-system/zones",
            json={
                "name": "Zone to Delete",
                "delivery_type": "drip",
                "schedule": {"frequency_days": 3, "duration_minutes": 30}
            }
        ).json()

        response = authenticated_client.delete(
            f"/irrigation-system/zones/{zone['id']}"
        )

        assert response.status_code == 204


class TestGardenZoneAssignment:
    """Test assigning gardens to irrigation zones"""

    def test_assign_garden_to_zone_success(
        self,
        authenticated_client: httpx.Client,
        test_garden: dict,
        cleanup_irrigation_zones: list
    ):
        """Successfully assign garden to irrigation zone"""
        # Create zone
        zone = authenticated_client.post(
            "/irrigation-system/zones",
            json={
                "name": "Test Zone",
                "delivery_type": "drip",
                "schedule": {"frequency_days": 3, "duration_minutes": 30}
            }
        ).json()
        cleanup_irrigation_zones.append(zone["id"])

        # Assign garden to zone
        response = authenticated_client.post(
            f"/irrigation-system/gardens/{test_garden['id']}/assign-zone",
            params={"zone_id": zone["id"]}
        )

        assert response.status_code == 200

        # Verify assignment
        garden_response = authenticated_client.get(f"/gardens/{test_garden['id']}")
        garden_data = garden_response.json()
        assert garden_data["garden"]["irrigation_zone_id"] == zone["id"]

    def test_unassign_garden_from_zone(
        self,
        authenticated_client: httpx.Client,
        test_garden: dict,
        cleanup_irrigation_zones: list
    ):
        """Successfully unassign garden from zone"""
        # Create and assign zone
        zone = authenticated_client.post(
            "/irrigation-system/zones",
            json={
                "name": "Test Zone",
                "delivery_type": "drip",
                "schedule": {"frequency_days": 3, "duration_minutes": 30}
            }
        ).json()
        cleanup_irrigation_zones.append(zone["id"])

        authenticated_client.post(
            f"/irrigation-system/gardens/{test_garden['id']}/assign-zone",
            params={"zone_id": zone["id"]}
        )

        # Unassign
        response = authenticated_client.delete(
            f"/irrigation-system/gardens/{test_garden['id']}/unassign-zone"
        )

        assert response.status_code == 200

        # Verify unassignment
        garden_response = authenticated_client.get(f"/gardens/{test_garden['id']}")
        garden_data = garden_response.json()
        assert garden_data["garden"]["irrigation_zone_id"] is None


class TestWateringEvents:
    """Test watering event recording"""

    def test_record_watering_event_for_zone(
        self,
        authenticated_client: httpx.Client,
        cleanup_irrigation_zones: list
    ):
        """Successfully record watering event for zone"""
        # Create zone
        zone = authenticated_client.post(
            "/irrigation-system/zones",
            json={
                "name": "Test Zone",
                "delivery_type": "drip",
                "schedule": {"frequency_days": 3, "duration_minutes": 30}
            }
        ).json()
        cleanup_irrigation_zones.append(zone["id"])

        # Record watering event
        event_data = {
            "irrigation_zone_id": zone["id"],
            "watered_at": datetime.utcnow().isoformat() + "Z",
            "duration_minutes": 30,
            "is_manual": False
        }

        response = authenticated_client.post(
            "/irrigation-system/events",
            json=event_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["irrigation_zone_id"] == zone["id"]
        assert data["duration_minutes"] == 30
        assert data["is_manual"] is False

    def test_record_manual_watering_for_garden(
        self,
        authenticated_client: httpx.Client,
        test_garden: dict
    ):
        """Record manual watering event for specific garden"""
        event_data = {
            "garden_id": test_garden["id"],
            "watered_at": datetime.utcnow().isoformat() + "Z",
            "duration_minutes": 15,
            "is_manual": True,
            "notes": "Hand watered with hose"
        }

        response = authenticated_client.post(
            "/irrigation-system/events",
            json=event_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["garden_id"] == test_garden["id"]
        assert data["is_manual"] is True

    def test_list_watering_events_for_zone(
        self,
        authenticated_client: httpx.Client,
        cleanup_irrigation_zones: list
    ):
        """List watering events for a zone"""
        # Create zone
        zone = authenticated_client.post(
            "/irrigation-system/zones",
            json={
                "name": "Test Zone",
                "delivery_type": "drip",
                "schedule": {"frequency_days": 3, "duration_minutes": 30}
            }
        ).json()
        cleanup_irrigation_zones.append(zone["id"])

        # Create multiple events
        for i in range(3):
            watered_at = (datetime.utcnow() - timedelta(days=i)).isoformat() + "Z"
            authenticated_client.post(
                "/irrigation-system/events",
                json={
                    "irrigation_zone_id": zone["id"],
                    "watered_at": watered_at,
                    "duration_minutes": 30,
                    "is_manual": False
                }
            )

        # List events
        response = authenticated_client.get(
            "/irrigation-system/events",
            params={"zone_id": zone["id"], "days": 7}
        )

        assert response.status_code == 200
        events = response.json()
        assert len(events) == 3


class TestIrrigationOverview:
    """Test irrigation overview endpoint"""

    def test_get_irrigation_overview(
        self,
        authenticated_client: httpx.Client,
        cleanup_irrigation_zones: list,
        cleanup_irrigation_sources: list
    ):
        """Get comprehensive irrigation overview"""
        # Create source
        source = authenticated_client.post(
            "/irrigation-system/sources",
            json={"name": "City Water", "source_type": "city", "flow_capacity_lpm": 50.0}
        ).json()
        cleanup_irrigation_sources.append(source["id"])

        # Create zone
        zone = authenticated_client.post(
            "/irrigation-system/zones",
            json={
                "name": "Test Zone",
                "delivery_type": "drip",
                "water_source_id": source["id"],
                "schedule": {"frequency_days": 3, "duration_minutes": 30}
            }
        ).json()
        cleanup_irrigation_zones.append(zone["id"])

        # Get overview
        response = authenticated_client.get("/irrigation-system/overview")

        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert "zones" in data
        assert len(data["sources"]) == 1
        assert len(data["zones"]) == 1


class TestIrrigationInsights:
    """Test irrigation insights and rule engine"""

    def test_get_irrigation_insights(
        self,
        authenticated_client: httpx.Client,
        test_garden: dict,
        cleanup_irrigation_zones: list
    ):
        """Get irrigation insights with rule-based recommendations"""
        # Create zone
        zone = authenticated_client.post(
            "/irrigation-system/zones",
            json={
                "name": "Test Zone",
                "delivery_type": "drip",
                "schedule": {"frequency_days": 3, "duration_minutes": 30}
            }
        ).json()
        cleanup_irrigation_zones.append(zone["id"])

        # Assign garden to zone
        authenticated_client.post(
            f"/irrigation-system/gardens/{test_garden['id']}/assign-zone",
            params={"zone_id": zone["id"]}
        )

        # Create watering events (trigger rules)
        for i in range(7):
            watered_at = (datetime.utcnow() - timedelta(days=i)).isoformat() + "Z"
            authenticated_client.post(
                "/irrigation-system/events",
                json={
                    "irrigation_zone_id": zone["id"],
                    "watered_at": watered_at,
                    "duration_minutes": 8,  # Short duration
                    "is_manual": False
                }
            )

        # Get insights
        response = authenticated_client.get("/irrigation-system/insights")

        assert response.status_code == 200
        data = response.json()
        assert "zones" in data
        assert isinstance(data["zones"], list)
        # Should have rule triggers due to short duration and high frequency
