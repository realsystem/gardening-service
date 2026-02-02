"""Tests for zone-based irrigation system."""

import pytest
from datetime import datetime, timedelta
from app.models.irrigation_source import IrrigationSource
from app.models.irrigation_zone import IrrigationZone
from app.models.watering_event import WateringEvent
from app.models.garden import Garden, GardenType
from app.models.soil_sample import SoilSample
from app.services.irrigation_service import IrrigationService
from app.services.irrigation_rule_engine import IrrigationRuleEngine
from app.schemas.irrigation_source import IrrigationSourceCreate
from app.schemas.irrigation_zone import IrrigationZoneCreate
from app.schemas.watering_event import WateringEventCreate


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def irrigation_source(test_db, sample_user):
    """Create a test irrigation source."""
    source = IrrigationSource(
        user_id=sample_user.id,
        name="Test City Water",
        source_type="city",
        flow_capacity_lpm=50.0,
        notes="Main water line"
    )
    test_db.add(source)
    test_db.commit()
    test_db.refresh(source)
    return source


@pytest.fixture
def irrigation_zone(test_db, sample_user, irrigation_source):
    """Create a test irrigation zone."""
    zone = IrrigationZone(
        user_id=sample_user.id,
        name="Test Vegetable Zone",
        irrigation_source_id=irrigation_source.id,
        delivery_type="drip",
        schedule={"frequency_days": 3, "duration_minutes": 30},
        notes="Main vegetable beds"
    )
    test_db.add(zone)
    test_db.commit()
    test_db.refresh(zone)
    return zone


@pytest.fixture
def garden_in_zone(test_db, sample_user, irrigation_zone):
    """Create a garden assigned to the test zone."""
    garden = Garden(
        user_id=sample_user.id,
        name="Test Garden in Zone",
        garden_type=GardenType.OUTDOOR,
        location="backyard",
        irrigation_zone_id=irrigation_zone.id
    )
    test_db.add(garden)
    test_db.commit()
    test_db.refresh(garden)
    return garden


@pytest.fixture
def watering_event(test_db, sample_user, irrigation_zone):
    """Create a test watering event."""
    event = WateringEvent(
        user_id=sample_user.id,
        irrigation_zone_id=irrigation_zone.id,
        watered_at=datetime.utcnow(),
        duration_minutes=30,
        is_manual=True,
        notes="Test watering"
    )
    test_db.add(event)
    test_db.commit()
    test_db.refresh(event)
    return event


# ============================================
# Rule Engine Tests
# ============================================

class TestIrrigationRuleEngine:
    """Test irrigation rule engine."""

    def test_freq_001_watering_too_frequently(self, test_db, sample_user, irrigation_zone):
        """Test FREQ_001 rule: Watering too frequently."""
        # Create events every day for the past week (average < 2 days)
        events = []
        for i in range(7):
            event = WateringEvent(
                user_id=sample_user.id,
                irrigation_zone_id=irrigation_zone.id,
                watered_at=datetime.utcnow() - timedelta(days=i),
                duration_minutes=30,
                is_manual=True
            )
            test_db.add(event)
            events.append(event)
        test_db.commit()

        insights = IrrigationRuleEngine.evaluate_zone_watering_frequency(
            irrigation_zone,
            events,
            days_to_analyze=14
        )

        assert len(insights) == 1
        assert insights[0].rule_id == "FREQ_001"
        assert insights[0].severity == "warning"
        assert "frequent" in insights[0].explanation.lower()

    def test_freq_002_infrequent_watering(self, test_db, sample_user, irrigation_zone):
        """Test FREQ_002 rule: Infrequent watering."""
        # Create 2 events with 12-day gap (average > 10 days)
        events = []
        for days_ago in [24, 12]:
            event = WateringEvent(
                user_id=sample_user.id,
                irrigation_zone_id=irrigation_zone.id,
                watered_at=datetime.utcnow() - timedelta(days=days_ago),
                duration_minutes=30,
                is_manual=True
            )
            test_db.add(event)
            events.append(event)
        test_db.commit()

        insights = IrrigationRuleEngine.evaluate_zone_watering_frequency(
            irrigation_zone,
            events,
            days_to_analyze=30
        )

        assert len(insights) == 1
        assert insights[0].rule_id == "FREQ_002"
        assert insights[0].severity == "info"
        assert "interval" in insights[0].explanation.lower()

    def test_dur_001_frequent_shallow_watering(self, test_db, sample_user, irrigation_zone):
        """Test DUR_001 rule: Frequent shallow watering."""
        # Create 10 events, 6 with short duration (< 10 min)
        events = []
        for i in range(6):
            event = WateringEvent(
                user_id=sample_user.id,
                irrigation_zone_id=irrigation_zone.id,
                watered_at=datetime.utcnow() - timedelta(days=i),
                duration_minutes=5,  # Short duration
                is_manual=True
            )
            test_db.add(event)
            events.append(event)

        for i in range(6, 10):
            event = WateringEvent(
                user_id=sample_user.id,
                irrigation_zone_id=irrigation_zone.id,
                watered_at=datetime.utcnow() - timedelta(days=i),
                duration_minutes=30,  # Proper duration
                is_manual=True
            )
            test_db.add(event)
            events.append(event)

        test_db.commit()

        insights = IrrigationRuleEngine.evaluate_watering_duration(
            irrigation_zone,
            events
        )

        assert len(insights) == 1
        assert insights[0].rule_id == "DUR_001"
        assert insights[0].severity == "warning"
        assert "shallow" in insights[0].explanation.lower()

    def test_conflict_001_mixed_soil_types(self, test_db, sample_user, irrigation_zone):
        """Test CONFLICT_001 rule: Mixed soil types in same zone."""
        # Create gardens with different soil textures
        sandy_garden = Garden(
            user_id=sample_user.id,
            name="Sandy Garden",
            garden_type=GardenType.OUTDOOR,
            location="zone1",
            irrigation_zone_id=irrigation_zone.id,
            soil_texture_override="sandy"
        )

        clay_garden = Garden(
            user_id=sample_user.id,
            name="Clay Garden",
            garden_type=GardenType.OUTDOOR,
            location="zone1",
            irrigation_zone_id=irrigation_zone.id,
            soil_texture_override="clay"
        )

        test_db.add_all([sandy_garden, clay_garden])
        test_db.commit()

        gardens_in_zone = [sandy_garden, clay_garden]

        insights = IrrigationRuleEngine.evaluate_zone_plant_conflicts(
            irrigation_zone,
            gardens_in_zone,
            []  # No planting events needed for this test
        )

        assert len(insights) == 1
        assert insights[0].rule_id == "CONFLICT_001"
        assert insights[0].severity == "warning"

    def test_response_001_low_moisture_despite_watering(self, test_db, sample_user, irrigation_zone, garden_in_zone):
        """Test RESPONSE_001 rule: Low soil moisture despite recent watering."""
        # Create recent watering event
        event = WateringEvent(
            user_id=sample_user.id,
            irrigation_zone_id=irrigation_zone.id,
            watered_at=datetime.utcnow() - timedelta(days=1),
            duration_minutes=30,
            is_manual=True
        )
        test_db.add(event)

        # Create 3 low moisture soil samples (rule requires >= 3 samples, >= 2 low)
        soil_samples = []
        for i in range(3):
            sample = SoilSample(
                user_id=sample_user.id,
                garden_id=garden_in_zone.id,
                ph=7.0,  # Required field
                moisture_percent=15.0,  # Low moisture (< 20%)
                date_collected=(datetime.utcnow() - timedelta(days=i)).date()
            )
            test_db.add(sample)
            soil_samples.append(sample)
        test_db.commit()

        insights = IrrigationRuleEngine.evaluate_soil_moisture_response(
            irrigation_zone,
            [garden_in_zone],
            [event],
            {garden_in_zone.id: soil_samples}
        )

        assert len(insights) == 1
        assert insights[0].rule_id == "RESPONSE_001"
        assert insights[0].severity == "warning"
        assert "moisture" in insights[0].explanation.lower()


# ============================================
# Service Layer Tests
# ============================================

class TestIrrigationService:
    """Test irrigation service layer."""

    def test_get_irrigation_overview(self, test_db, sample_user, irrigation_zone, irrigation_source, watering_event):
        """Test getting irrigation system overview."""
        overview = IrrigationService.get_irrigation_overview(test_db, sample_user.id)

        assert "zones" in overview
        assert "sources" in overview
        assert "recent_events" in overview
        assert "upcoming_waterings" in overview

        assert len(overview["zones"]) >= 1
        assert len(overview["sources"]) >= 1

    def test_calculate_upcoming_waterings(self, test_db, sample_user, irrigation_zone):
        """Test calculating upcoming waterings based on schedule."""
        # Set zone schedule
        irrigation_zone.schedule = {"frequency_days": 3, "duration_minutes": 30}
        test_db.commit()

        # Create last watering 2 days ago
        event = WateringEvent(
            user_id=sample_user.id,
            irrigation_zone_id=irrigation_zone.id,
            watered_at=datetime.utcnow() - timedelta(days=2),
            duration_minutes=30,
            is_manual=True
        )
        test_db.add(event)
        test_db.commit()

        overview = IrrigationService.get_irrigation_overview(test_db, sample_user.id)

        assert len(overview["upcoming_waterings"]) > 0
        upcoming = overview["upcoming_waterings"][0]
        assert upcoming["zone_id"] == irrigation_zone.id
        assert upcoming["status"] in ["upcoming", "today", "overdue"]

    def test_get_zone_details(self, test_db, sample_user, irrigation_zone, watering_event, garden_in_zone):
        """Test getting detailed zone information."""
        details = IrrigationService.get_zone_details(test_db, irrigation_zone.id, sample_user.id)

        assert details["zone"].id == irrigation_zone.id
        assert details["zone"].name == irrigation_zone.name
        assert "statistics" in details
        assert "recent_events" in details
        assert "gardens" in details

        assert len(details["gardens"]) >= 1

    def test_get_irrigation_insights(self, test_db, sample_user, irrigation_zone):
        """Test getting irrigation insights from rule engine."""
        # Create frequent watering to trigger rule
        for i in range(7):
            event = WateringEvent(
                user_id=sample_user.id,
                irrigation_zone_id=irrigation_zone.id,
                watered_at=datetime.utcnow() - timedelta(days=i),
                duration_minutes=30,
                is_manual=True
            )
            test_db.add(event)
        test_db.commit()

        insights = IrrigationService.get_irrigation_insights(test_db, sample_user.id)

        # Service returns a list of IrrigationRule objects
        assert isinstance(insights, list)
        assert len(insights) > 0
        assert any(rule.rule_id == "FREQ_001" for rule in insights)


# ============================================
# API Endpoint Tests
# ============================================

class TestIrrigationSystemAPI:
    """Test irrigation system API endpoints."""

    def test_create_irrigation_source(self, client, user_token):
        """Test creating an irrigation source via API."""
        headers = {"Authorization": f"Bearer {user_token}"}

        data = {
            "name": "Test Rain Barrel",
            "source_type": "rain",
            "flow_capacity_lpm": 20.0,
            "notes": "Rainwater collection"
        }

        response = client.post("/irrigation-system/sources", json=data, headers=headers)

        assert response.status_code == 201
        result = response.json()
        assert result["name"] == "Test Rain Barrel"
        assert result["source_type"] == "rain"

    def test_create_irrigation_zone(self, client, user_token, irrigation_source):
        """Test creating an irrigation zone via API."""
        headers = {"Authorization": f"Bearer {user_token}"}

        data = {
            "name": "API Test Zone",
            "delivery_type": "drip",
            "irrigation_source_id": irrigation_source.id,
            "schedule": {
                "frequency_days": 3,
                "duration_minutes": 30
            },
            "notes": "Test zone"
        }

        response = client.post("/irrigation-system/zones", json=data, headers=headers)

        assert response.status_code == 201
        result = response.json()
        assert result["name"] == "API Test Zone"
        assert result["delivery_type"] == "drip"
        assert result["schedule"]["frequency_days"] == 3

    def test_create_watering_event(self, client, user_token, irrigation_zone):
        """Test recording a watering event via API."""
        headers = {"Authorization": f"Bearer {user_token}"}

        data = {
            "irrigation_zone_id": irrigation_zone.id,
            "watered_at": datetime.utcnow().isoformat(),
            "duration_minutes": 25,
            "is_manual": True,
            "notes": "API test watering"
        }

        response = client.post("/irrigation-system/events", json=data, headers=headers)

        assert response.status_code == 201
        result = response.json()
        assert result["irrigation_zone_id"] == irrigation_zone.id
        assert result["duration_minutes"] == 25

    def test_get_irrigation_overview(self, client, user_token, irrigation_zone, irrigation_source):
        """Test getting irrigation overview via API."""
        headers = {"Authorization": f"Bearer {user_token}"}

        response = client.get("/irrigation-system/overview", headers=headers)

        assert response.status_code == 200
        result = response.json()
        assert "zones" in result
        assert "sources" in result
        assert "recent_events" in result
        assert "upcoming_waterings" in result

    def test_get_irrigation_insights(self, client, user_token):
        """Test getting irrigation insights via API."""
        headers = {"Authorization": f"Bearer {user_token}"}

        response = client.get("/irrigation-system/insights", headers=headers)

        assert response.status_code == 200
        result = response.json()
        assert "insights" in result
        assert "total_count" in result
        assert "by_severity" in result

    def test_unauthorized_access(self, client):
        """Test that endpoints require authentication."""
        # Try to access without token
        response = client.get("/irrigation-system/overview")
        assert response.status_code == 403

    def test_cannot_access_other_users_zones(self, client, user_token, test_db, irrigation_zone):
        """Test that users cannot access other users' zones."""
        from app.models.user import User, UnitSystem
        from app.services.auth_service import AuthService

        # Create another user
        other_user = User(
            email="other@example.com",
            hashed_password=AuthService.hash_password("password"),
            unit_system=UnitSystem.METRIC
        )
        test_db.add(other_user)
        test_db.commit()

        # Create token for other user
        other_token = AuthService.create_access_token(other_user.id, other_user.email)
        other_headers = {"Authorization": f"Bearer {other_token}"}

        # Try to access first user's zone
        response = client.get(f"/irrigation-system/zones/{irrigation_zone.id}", headers=other_headers)

        # Should get 404 (not found, not unauthorized, to avoid info leakage)
        assert response.status_code == 404


# ============================================
# Integration Tests
# ============================================

class TestIrrigationSystemIntegration:
    """Test full workflow integration."""

    def test_complete_zone_workflow(self, client, user_token, test_db):
        """Test complete workflow: create source, zone, record event, get insights."""
        headers = {"Authorization": f"Bearer {user_token}"}

        # 1. Create water source
        source_data = {
            "name": "Integration Test Source",
            "source_type": "city",
            "flow_capacity_lpm": 40.0
        }
        source_response = client.post("/irrigation-system/sources", json=source_data, headers=headers)
        assert source_response.status_code == 201
        source_id = source_response.json()["id"]

        # 2. Create irrigation zone
        zone_data = {
            "name": "Integration Test Zone",
            "delivery_type": "drip",
            "irrigation_source_id": source_id,
            "schedule": {"frequency_days": 2, "duration_minutes": 20}
        }
        zone_response = client.post("/irrigation-system/zones", json=zone_data, headers=headers)
        assert zone_response.status_code == 201
        zone_id = zone_response.json()["id"]

        # 3. Record multiple watering events (daily) to trigger FREQ_001
        for i in range(5):
            event_data = {
                "irrigation_zone_id": zone_id,
                "watered_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                "duration_minutes": 20,
                "is_manual": True
            }
            event_response = client.post("/irrigation-system/events", json=event_data, headers=headers)
            assert event_response.status_code == 201

        # 4. Get insights - should trigger FREQ_001
        insights_response = client.get("/irrigation-system/insights", headers=headers)
        assert insights_response.status_code == 200
        insights = insights_response.json()

        assert insights["total_count"] > 0
        assert any(i["rule_id"] == "FREQ_001" for i in insights["insights"])

        # 5. Get overview
        overview_response = client.get("/irrigation-system/overview", headers=headers)
        assert overview_response.status_code == 200
        overview = overview_response.json()

        assert len(overview["zones"]) >= 1
        assert len(overview["sources"]) >= 1
        assert len(overview["recent_events"]) > 0
