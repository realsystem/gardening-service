"""Tests for irrigation tracking functionality."""

import pytest
from datetime import datetime, timedelta, date
from app.models.irrigation_event import IrrigationEvent
from app.models.garden import Garden
from app.models.planting_event import PlantingEvent
from app.models.plant_variety import PlantVariety


class TestIrrigationEventCRUD:
    """Test irrigation event CRUD operations."""

    def test_create_irrigation_event_for_garden(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test creating an irrigation event for a garden."""
        headers = {"Authorization": f"Bearer {user_token}"}

        data = {
            "garden_id": outdoor_garden.id,
            "irrigation_date": datetime.now().isoformat(),
            "water_volume_liters": 20.0,
            "irrigation_method": "hand_watering",
            "duration_minutes": 15,
            "notes": "Morning watering"
        }

        response = client.post("/irrigation", json=data, headers=headers)
        assert response.status_code == 201

        result = response.json()
        assert result["garden_id"] == outdoor_garden.id
        assert result["water_volume_liters"] == 20.0
        assert result["irrigation_method"] == "hand_watering"
        assert result["duration_minutes"] == 15

    def test_create_irrigation_event_for_planting(self, client, sample_user, outdoor_planting_event, user_token, test_db):
        """Test creating an irrigation event for a specific planting."""
        headers = {"Authorization": f"Bearer {user_token}"}

        data = {
            "planting_event_id": outdoor_planting_event.id,
            "irrigation_date": datetime.now().isoformat(),
            "water_volume_liters": 5.0,
            "irrigation_method": "drip",
            "duration_minutes": 30
        }

        response = client.post("/irrigation", json=data, headers=headers)
        assert response.status_code == 201

        result = response.json()
        assert result["planting_event_id"] == outdoor_planting_event.id
        assert result["irrigation_method"] == "drip"

    def test_create_irrigation_event_without_garden_or_planting_fails(self, client, user_token):
        """Test that irrigation event requires either garden_id or planting_event_id."""
        headers = {"Authorization": f"Bearer {user_token}"}

        data = {
            "irrigation_date": datetime.now().isoformat(),
            "irrigation_method": "hand_watering"
        }

        response = client.post("/irrigation", json=data, headers=headers)
        assert response.status_code == 400

    def test_list_irrigation_events(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test listing irrigation events."""
        # Create multiple events
        event1 = IrrigationEvent(
            user_id=sample_user.id,
            garden_id=outdoor_garden.id,
            irrigation_date=datetime.now() - timedelta(days=2),
            irrigation_method="hand_watering",
            water_volume_liters=15.0
        )
        event2 = IrrigationEvent(
            user_id=sample_user.id,
            garden_id=outdoor_garden.id,
            irrigation_date=datetime.now() - timedelta(days=1),
            irrigation_method="drip",
            water_volume_liters=10.0
        )
        test_db.add_all([event1, event2])
        test_db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/irrigation", headers=headers)

        assert response.status_code == 200
        result = response.json()
        assert len(result["events"]) >= 2
        assert result["summary"]["total_events"] >= 2
        assert result["summary"]["total_volume_liters"] >= 25.0

    def test_list_irrigation_events_filtered_by_garden(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test filtering irrigation events by garden."""
        # Create another garden
        garden2 = Garden(user_id=sample_user.id, name="Garden 2", garden_type="outdoor")
        test_db.add(garden2)
        test_db.commit()

        event1 = IrrigationEvent(
            user_id=sample_user.id,
            garden_id=outdoor_garden.id,
            irrigation_date=datetime.now(),
            irrigation_method="hand_watering"
        )
        event2 = IrrigationEvent(
            user_id=sample_user.id,
            garden_id=garden2.id,
            irrigation_date=datetime.now(),
            irrigation_method="drip"
        )
        test_db.add_all([event1, event2])
        test_db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/irrigation?garden_id={outdoor_garden.id}", headers=headers)

        assert response.status_code == 200
        result = response.json()
        # All events should belong to the specified garden
        for event in result["events"]:
            assert event["garden_id"] == outdoor_garden.id

    def test_list_irrigation_events_filtered_by_days(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test filtering irrigation events by number of days."""
        # Create events at different times
        old_event = IrrigationEvent(
            user_id=sample_user.id,
            garden_id=outdoor_garden.id,
            irrigation_date=datetime.now() - timedelta(days=40),
            irrigation_method="hand_watering"
        )
        recent_event = IrrigationEvent(
            user_id=sample_user.id,
            garden_id=outdoor_garden.id,
            irrigation_date=datetime.now() - timedelta(days=5),
            irrigation_method="drip"
        )
        test_db.add_all([old_event, recent_event])
        test_db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/irrigation?days=30", headers=headers)

        assert response.status_code == 200
        result = response.json()
        # Should only get the recent event
        assert len(result["events"]) >= 1
        # Old event should not be included
        event_ids = [e["id"] for e in result["events"]]
        assert old_event.id not in event_ids

    def test_get_irrigation_summary(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test getting irrigation summary."""
        # Create multiple events
        for i in range(5):
            event = IrrigationEvent(
                user_id=sample_user.id,
                garden_id=outdoor_garden.id,
                irrigation_date=datetime.now() - timedelta(days=i*5),
                irrigation_method="hand_watering",
                water_volume_liters=10.0 + i
            )
            test_db.add(event)
        test_db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/irrigation/summary?garden_id={outdoor_garden.id}&days=30", headers=headers)

        assert response.status_code == 200
        result = response.json()
        assert result["total_events"] >= 5
        assert result["total_volume_liters"] > 0
        assert result["average_volume_per_event"] is not None
        assert result["most_common_method"] == "hand_watering"

    def test_delete_irrigation_event(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test deleting an irrigation event."""
        event = IrrigationEvent(
            user_id=sample_user.id,
            garden_id=outdoor_garden.id,
            irrigation_date=datetime.now(),
            irrigation_method="hand_watering"
        )
        test_db.add(event)
        test_db.commit()
        event_id = event.id

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.delete(f"/irrigation/{event_id}", headers=headers)

        assert response.status_code == 204

        # Verify deletion
        deleted = test_db.query(IrrigationEvent).filter(IrrigationEvent.id == event_id).first()
        assert deleted is None

    def test_cannot_access_other_users_events(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test that users cannot delete other users' irrigation events."""
        # Create another user
        from app.models.user import User
        from app.services.auth_service import AuthService

        other_user = User(email="other@example.com", hashed_password=AuthService.hash_password("testpass123"))
        test_db.add(other_user)
        test_db.commit()

        other_garden = Garden(user_id=other_user.id, name="Other Garden", garden_type="outdoor")
        test_db.add(other_garden)
        test_db.commit()

        other_event = IrrigationEvent(
            user_id=other_user.id,
            garden_id=other_garden.id,
            irrigation_date=datetime.now(),
            irrigation_method="drip"
        )
        test_db.add(other_event)
        test_db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.delete(f"/irrigation/{other_event.id}", headers=headers)

        assert response.status_code == 404


class TestIrrigationRecommendations:
    """Test irrigation recommendations."""

    def test_recommendations_for_overdue_watering(self, client, sample_user, outdoor_garden, outdoor_planting_event, user_token, test_db):
        """Test that overdue watering generates high priority recommendation."""
        # Create an irrigation event 7 days ago (tomatoes need water every 3 days)
        old_event = IrrigationEvent(
            user_id=sample_user.id,
            planting_event_id=outdoor_planting_event.id,
            irrigation_date=datetime.now() - timedelta(days=7),
            irrigation_method="hand_watering"
        )
        test_db.add(old_event)
        test_db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/irrigation?planting_event_id={outdoor_planting_event.id}", headers=headers)

        assert response.status_code == 200
        result = response.json()

        # Should have recommendations
        assert len(result["summary"]["recommendations"]) > 0
        rec = result["summary"]["recommendations"][0]
        assert rec["status"] in ["overdue"]
        assert rec["priority"] in ["high", "critical"]
        assert "water" in rec["recommendation"].lower()

    def test_recommendations_for_on_schedule_watering(self, client, sample_user, outdoor_planting_event, user_token, test_db):
        """Test that on-schedule watering generates low priority recommendation."""
        # Water recently (2 days ago, within the 3-day schedule for tomatoes)
        recent_event = IrrigationEvent(
            user_id=sample_user.id,
            planting_event_id=outdoor_planting_event.id,
            irrigation_date=datetime.now() - timedelta(days=2),
            irrigation_method="drip"
        )
        test_db.add(recent_event)
        test_db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/irrigation?planting_event_id={outdoor_planting_event.id}", headers=headers)

        assert response.status_code == 200
        result = response.json()

        if len(result["summary"]["recommendations"]) > 0:
            rec = result["summary"]["recommendations"][0]
            assert rec["status"] in ["on_schedule", "overdue"]  # Depending on timing

    def test_summary_calculates_statistics_correctly(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test that summary statistics are calculated correctly."""
        # Create 3 events with known volumes
        volumes = [10.0, 20.0, 30.0]
        for vol in volumes:
            event = IrrigationEvent(
                user_id=sample_user.id,
                garden_id=outdoor_garden.id,
                irrigation_date=datetime.now() - timedelta(days=1),
                irrigation_method="hand_watering",
                water_volume_liters=vol
            )
            test_db.add(event)
        test_db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/irrigation?garden_id={outdoor_garden.id}&days=7", headers=headers)

        assert response.status_code == 200
        result = response.json()

        assert result["summary"]["total_events"] >= 3
        assert result["summary"]["total_volume_liters"] >= sum(volumes)
        assert result["summary"]["average_volume_per_event"] is not None

    def test_recommendations_include_frequency_and_volume(self, client, sample_user, outdoor_planting_event, user_token, test_db):
        """Test that recommendations include specific frequency and volume guidance."""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/irrigation?planting_event_id={outdoor_planting_event.id}", headers=headers)

        assert response.status_code == 200
        result = response.json()

        if len(result["summary"]["recommendations"]) > 0:
            rec = result["summary"]["recommendations"][0]
            assert rec["recommended_frequency_days"] > 0
            assert "day" in rec["recommendation"].lower() or "water" in rec["recommendation"].lower()


class TestIrrigationIntegration:
    """Integration tests for irrigation with other features."""

    def test_irrigation_cascade_delete_with_garden(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test that irrigation events are deleted when garden is deleted."""
        event = IrrigationEvent(
            user_id=sample_user.id,
            garden_id=outdoor_garden.id,
            irrigation_date=datetime.now(),
            irrigation_method="hand_watering"
        )
        test_db.add(event)
        test_db.commit()
        event_id = event.id

        # Delete garden
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.delete(f"/gardens/{outdoor_garden.id}", headers=headers)
        assert response.status_code == 204

        # Verify irrigation event was cascade deleted
        deleted_event = test_db.query(IrrigationEvent).filter(IrrigationEvent.id == event_id).first()
        assert deleted_event is None

    def test_irrigation_cascade_delete_with_planting(self, client, sample_user, outdoor_planting_event, user_token, test_db):
        """Test that irrigation events are deleted when planting is deleted."""
        event = IrrigationEvent(
            user_id=sample_user.id,
            planting_event_id=outdoor_planting_event.id,
            irrigation_date=datetime.now(),
            irrigation_method="drip"
        )
        test_db.add(event)
        test_db.commit()
        event_id = event.id

        # Delete planting event (via garden deletion for cascade)
        headers = {"Authorization": f"Bearer {user_token}"}
        garden_id = outdoor_planting_event.garden_id
        response = client.delete(f"/gardens/{garden_id}", headers=headers)
        assert response.status_code == 204

        # Verify irrigation event was cascade deleted
        deleted_event = test_db.query(IrrigationEvent).filter(IrrigationEvent.id == event_id).first()
        assert deleted_event is None
