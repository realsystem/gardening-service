"""Tests for API endpoints"""
import pytest
from datetime import date, timedelta

from app.models.care_task import TaskStatus


class TestAuthEndpoints:
    """Test authentication endpoints"""

    def test_register_user(self, client):
        """Test user registration"""
        response = client.post(
            "/users",
            json={
                "email": "newuser@example.com",
                "password": "securepass123",            }
        )
        assert response.status_code == 201  # Created
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data

    def test_register_duplicate_email(self, client, sample_user):
        """Test registering with existing email fails"""
        response = client.post(
            "/users",
            json={
                "email": sample_user.email,
                "password": "password123",            }
        )
        assert response.status_code == 400

    def test_login_success(self, client, sample_user):
        """Test successful login"""
        response = client.post(
            "/users/login",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, sample_user):
        """Test login with invalid credentials"""
        response = client.post(
            "/users/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401


class TestUserProfileEndpoints:
    """Test user profile endpoints"""

    def test_get_current_user(self, client, sample_user, user_token):
        """Test getting current user"""
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user.email

    def test_update_user_profile(self, client, sample_user, user_token):
        """Test updating user profile (profile fields are in User model, not separate UserProfile)"""
        response = client.patch(
            "/users/me",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "display_name": "Updated Name",
                "city": "Seattle",
                "gardening_preferences": "Organic gardening"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Updated Name"
        assert data["city"] == "Seattle"
        assert data["gardening_preferences"] == "Organic gardening"


class TestPlantVarietyEndpoints:
    """Test plant variety endpoints"""

    def test_get_plant_varieties(self, client, sample_plant_variety):
        """Test getting list of plant varieties"""
        response = client.get("/plant-varieties/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["common_name"] == "Tomato"

    def test_get_single_plant_variety(self, client, sample_plant_variety):
        """Test getting a single plant variety"""
        response = client.get(f"/plant-varieties/{sample_plant_variety.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["common_name"] == "Tomato"
        assert data["days_to_harvest"] == 80


class TestSeedBatchEndpoints:
    """Test seed batch endpoints"""

    def test_create_seed_batch(self, client, sample_user, sample_plant_variety, user_token):
        """Test creating a seed batch"""
        response = client.post(
            "/seed-batches/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "plant_variety_id": sample_plant_variety.id,
                "source": "Online Store",
                "harvest_year": 2023,
                "quantity": 100
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["source"] == "Online Store"
        assert data["quantity"] == 100

    def test_get_user_seed_batches(self, client, sample_user, sample_seed_batch, user_token):
        """Test getting user's seed batches"""
        response = client.get(
            "/seed-batches/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["source"] == "Local Nursery"

    def test_delete_seed_batch(self, client, sample_user, sample_seed_batch, user_token):
        """Test deleting a seed batch"""
        batch_id = sample_seed_batch.id
        response = client.delete(
            f"/seed-batches/{batch_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get(
            f"/seed-batches/{batch_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 404


class TestGardenEndpoints:
    """Test garden endpoints"""

    def test_create_outdoor_garden(self, client, sample_user, user_token):
        """Test creating an outdoor garden"""
        response = client.post(
            "/gardens/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "Backyard Garden",
                "description": "Main vegetable garden",
                "garden_type": "outdoor"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Backyard Garden"
        assert data["garden_type"] == "outdoor"

    def test_create_indoor_garden(self, client, sample_user, user_token):
        """Test creating an indoor garden"""
        response = client.post(
            "/gardens/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "Indoor Setup",
                "garden_type": "indoor",
                "location": "Spare room",
                "light_source_type": "led",
                "light_hours_per_day": 16.0,
                "temp_min_f": 65.0,
                "temp_max_f": 75.0
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["garden_type"] == "indoor"
        assert data["light_source_type"] == "led"

    def test_create_hydroponic_garden(self, client, sample_user, user_token):
        """Test creating a hydroponic garden"""
        response = client.post(
            "/gardens/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "Hydro System",
                "garden_type": "indoor",
                "is_hydroponic": True,
                "hydro_system_type": "dwc",
                "reservoir_size_liters": 50.0,
                "ph_min": 5.5,
                "ph_max": 6.5,
                "ec_min": 1.0,
                "ec_max": 1.8
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["is_hydroponic"] is True
        assert data["hydro_system_type"] == "dwc"
        assert data["reservoir_size_liters"] == 50.0

    def test_get_user_gardens(self, client, sample_user, outdoor_garden, user_token):
        """Test getting user's gardens"""
        response = client.get(
            "/gardens/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_update_garden(self, client, sample_user, outdoor_garden, user_token):
        """Test updating a garden"""
        response = client.patch(
            f"/gardens/{outdoor_garden.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"description": "Updated description"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    def test_delete_garden(self, client, sample_user, outdoor_garden, user_token):
        """Test deleting a garden"""
        garden_id = outdoor_garden.id
        response = client.delete(
            f"/gardens/{garden_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 204


class TestPlantingEventEndpoints:
    """Test planting event endpoints"""

    def test_create_planting_event(self, client, sample_user, outdoor_garden, sample_plant_variety, user_token):
        """Test creating a planting event"""
        response = client.post(
            "/planting-events/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "garden_id": outdoor_garden.id,
                "plant_variety_id": sample_plant_variety.id,
                "planting_date": str(date.today()),
                "planting_method": "direct_sow",
                "plant_count": 12,
                "location_in_garden": "Bed 3"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["planting_method"] == "direct_sow"
        assert data["plant_count"] == 12

    def test_get_user_planting_events(self, client, sample_user, outdoor_planting_event, user_token):
        """Test getting user's planting events"""
        response = client.get(
            "/planting-events/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_update_planting_event(self, client, sample_user, outdoor_planting_event, user_token):
        """Test updating a planting event"""
        response = client.patch(
            f"/planting-events/{outdoor_planting_event.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"health_status": "stressed"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["health_status"] == "stressed"

    def test_planting_event_includes_plant_variety(self, client, sample_user, outdoor_planting_event, sample_plant_variety, user_token):
        """Test that planting event response includes plant_variety details"""
        response = client.get(
            f"/planting-events/{outdoor_planting_event.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "plant_variety" in data
        assert data["plant_variety"] is not None
        assert data["plant_variety"]["common_name"] == sample_plant_variety.common_name
        assert data["plant_variety"]["id"] == sample_plant_variety.id

    def test_list_planting_events_includes_plant_variety(self, client, sample_user, outdoor_planting_event, sample_plant_variety, user_token):
        """Test that list planting events includes plant_variety details"""
        response = client.get(
            "/planting-events/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        # Check first planting event has plant_variety
        assert "plant_variety" in data[0]
        assert data[0]["plant_variety"] is not None
        assert "common_name" in data[0]["plant_variety"]

    def test_filter_planting_events_by_garden(self, client, sample_user, outdoor_garden, sample_plant_variety, user_token, test_db):
        """Test filtering planting events by garden_id"""
        from app.models.garden import Garden
        from app.models.planting_event import PlantingEvent

        # Create second garden
        garden2 = Garden(
            user_id=sample_user.id,
            name="Test Garden 2",
            garden_type="outdoor",
            is_hydroponic=False
        )
        test_db.add(garden2)
        test_db.commit()
        test_db.refresh(garden2)

        # Create plantings in both gardens
        planting1 = PlantingEvent(
            user_id=sample_user.id,
            garden_id=outdoor_garden.id,
            plant_variety_id=sample_plant_variety.id,
            planting_date=date.today(),
            planting_method="direct_sow"
        )
        planting2 = PlantingEvent(
            user_id=sample_user.id,
            garden_id=garden2.id,
            plant_variety_id=sample_plant_variety.id,
            planting_date=date.today(),
            planting_method="transplant"
        )
        test_db.add_all([planting1, planting2])
        test_db.commit()

        # Get all plantings
        response = client.get(
            "/planting-events/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        all_data = response.json()
        assert len(all_data) >= 2

        # Filter by first garden
        response = client.get(
            f"/planting-events/?garden_id={outdoor_garden.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        garden1_data = response.json()
        # Check all plantings belong to garden 1
        for planting in garden1_data:
            assert planting["garden_id"] == outdoor_garden.id

        # Filter by second garden
        response = client.get(
            f"/planting-events/?garden_id={garden2.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        garden2_data = response.json()
        # Check all plantings belong to garden 2
        for planting in garden2_data:
            assert planting["garden_id"] == garden2.id

    def test_filter_planting_events_unauthorized_garden(self, client, sample_user, second_user, outdoor_garden, user_token):
        """Test that user cannot filter by another user's garden"""
        from app.services.auth_service import AuthService
        from app.models.garden import Garden

        # Create garden for second user
        second_user_garden = Garden(
            user_id=second_user.id,
            name="Second User Garden",
            garden_type="outdoor",
            is_hydroponic=False
        )
        # Get the test_db from outdoor_garden's session
        db = outdoor_garden.__dict__['_sa_instance_state'].session
        db.add(second_user_garden)
        db.commit()
        db.refresh(second_user_garden)

        # Try to filter by second user's garden using first user's token
        response = client.get(
            f"/planting-events/?garden_id={second_user_garden.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403

    def test_filter_planting_events_nonexistent_garden(self, client, user_token):
        """Test filtering by non-existent garden returns 404"""
        response = client.get(
            "/planting-events/?garden_id=99999",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 404


class TestSensorReadingEndpoints:
    """Test sensor reading endpoints"""

    def test_create_indoor_sensor_reading(self, client, sample_user, indoor_garden, user_token):
        """Test creating an indoor sensor reading"""
        response = client.post(
            "/sensor-readings/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "garden_id": indoor_garden.id,
                "reading_date": str(date.today()),
                "temperature_f": 72.0,
                "humidity_percent": 58.0,
                "light_hours": 16.0
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["temperature_f"] == 72.0
        assert data["humidity_percent"] == 58.0

    def test_create_hydroponic_sensor_reading(self, client, sample_user, hydroponic_garden, user_token):
        """Test creating a hydroponic sensor reading"""
        response = client.post(
            "/sensor-readings/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "garden_id": hydroponic_garden.id,
                "reading_date": str(date.today()),
                "temperature_f": 70.0,
                "humidity_percent": 60.0,
                "light_hours": 18.0,
                "ph_level": 6.2,
                "ec_ms_cm": 1.6,
                "ppm": 1120,
                "water_temp_f": 68.0
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["ph_level"] == 6.2
        assert data["ec_ms_cm"] == 1.6
        assert data["ppm"] == 1120

    def test_get_user_sensor_readings(self, client, sample_user, indoor_sensor_reading, user_token):
        """Test getting user's sensor readings"""
        response = client.get(
            "/sensor-readings/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_delete_sensor_reading(self, client, sample_user, indoor_sensor_reading, user_token):
        """Test deleting a sensor reading"""
        reading_id = indoor_sensor_reading.id
        response = client.delete(
            f"/sensor-readings/{reading_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 204


class TestCareTaskEndpoints:
    """Test care task endpoints"""

    def test_create_manual_task(self, client, sample_user, outdoor_planting_event, user_token):
        """Test creating a manual task"""
        response = client.post(
            "/tasks/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "planting_event_id": outdoor_planting_event.id,
                "task_type": "prune",
                "title": "Prune tomatoes",
                "description": "Remove suckers",
                "priority": "medium",
                "due_date": str(date.today() + timedelta(days=7))
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["task_type"] == "prune"
        assert data["priority"] == "medium"

    def test_get_user_tasks(self, client, sample_user, sample_care_task, user_token):
        """Test getting user's tasks"""
        response = client.get(
            "/tasks/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_complete_task(self, client, sample_user, sample_care_task, user_token):
        """Test completing a task"""
        response = client.post(
            f"/tasks/{sample_care_task.id}/complete",
            headers={"Authorization": f"Bearer {user_token}"},
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_date"] is not None

    def test_update_task(self, client, sample_user, sample_care_task, user_token):
        """Test updating a task"""
        response = client.patch(
            f"/tasks/{sample_care_task.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"priority": "high"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "high"

    def test_delete_task(self, client, sample_user, sample_care_task, user_token):
        """Test deleting a task"""
        task_id = sample_care_task.id
        response = client.delete(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 204


class TestAuthorizationAndSecurity:
    """Test authorization and security"""

    def test_unauthorized_access(self, client, outdoor_garden):
        """Test that unauthorized users cannot access protected endpoints"""
        response = client.get("/gardens/")
        assert response.status_code == 403

    def test_user_cannot_access_other_users_data(self, client, sample_user, second_user, outdoor_garden):
        """Test that users cannot access other users' data"""
        # Create token for second user
        from app.services.auth_service import AuthService
        second_user_token = AuthService.create_access_token(second_user.id, second_user.email)

        # Try to access first user's garden
        response = client.get(
            f"/gardens/{outdoor_garden.id}",
            headers={"Authorization": f"Bearer {second_user_token}"}
        )
        assert response.status_code == 403  # Forbidden - user not authorized

    def test_invalid_token(self, client):
        """Test that invalid tokens are rejected"""
        response = client.get(
            "/gardens/",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        assert response.status_code == 401


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_create_garden_with_missing_required_fields(self, client, sample_user, user_token):
        """Test creating garden with missing required fields"""
        response = client.post(
            "/gardens/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"description": "Missing name field"}
        )
        assert response.status_code == 422  # Validation error

    def test_get_nonexistent_resource(self, client, user_token):
        """Test getting non-existent resource"""
        response = client.get(
            "/gardens/99999",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 404

    def test_sensor_reading_validation(self, client, sample_user, hydroponic_garden, user_token):
        """Test sensor reading with invalid values"""
        response = client.post(
            "/sensor-readings/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "garden_id": hydroponic_garden.id,
                "reading_date": str(date.today()),
                "ph_level": 15.0,  # Invalid: pH must be 0-14
            }
        )
        assert response.status_code == 422

    def test_sensor_reading_requires_at_least_one_value(self, client, sample_user, hydroponic_garden, user_token):
        """Test that sensor reading requires at least one sensor value"""
        response = client.post(
            "/sensor-readings/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "garden_id": hydroponic_garden.id,
                "reading_date": str(date.today()),
                # No sensor values provided
            }
        )
        assert response.status_code == 422
        response_data = response.json()
        # Check if error message is in the response
        error_msg = str(response_data).lower()
        assert "at least one sensor reading must be provided" in error_msg


class TestPlantingEventDeletion:
    """Test planting event deletion functionality"""

    def test_delete_planting_event_success(self, client, sample_user, outdoor_planting_event, user_token):
        """Test successful deletion of planting event"""
        event_id = outdoor_planting_event.id
        response = client.delete(
            f"/planting-events/{event_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 204

        # Verify deletion
        response = client.get(
            f"/planting-events/{event_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 404

    def test_delete_planting_event_cascade_to_tasks(self, client, sample_user, outdoor_planting_event, sample_care_task, user_token):
        """Test that deleting planting event cascades to delete tasks"""
        event_id = outdoor_planting_event.id
        task_id = sample_care_task.id

        # Delete planting event
        response = client.delete(
            f"/planting-events/{event_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 204

        # Verify task is also deleted
        response = client.get(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 404

    def test_delete_nonexistent_planting_event(self, client, user_token):
        """Test deleting non-existent planting event"""
        response = client.delete(
            "/planting-events/99999",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 404

    def test_delete_planting_event_unauthorized(self, client, sample_user, second_user, outdoor_planting_event):
        """Test that user cannot delete another user's planting event"""
        from app.services.auth_service import AuthService
        second_token = AuthService.create_access_token(second_user.id, second_user.email)

        response = client.delete(
            f"/planting-events/{outdoor_planting_event.id}",
            headers={"Authorization": f"Bearer {second_token}"}
        )
        assert response.status_code == 403


class TestGardenSensorReadings:
    """Test garden sensor readings endpoint"""

    def test_get_garden_sensor_readings_success(self, client, sample_user, hydroponic_garden, user_token, test_db):
        """Test getting sensor readings for a specific garden"""
        # Create sensor readings
        from app.models.sensor_reading import SensorReading
        reading1 = SensorReading(
            user_id=sample_user.id,
            garden_id=hydroponic_garden.id,
            reading_date=date.today(),
            temperature_f=72.0,
            humidity_percent=60.0,
            ph_level=6.5
        )
        reading2 = SensorReading(
            user_id=sample_user.id,
            garden_id=hydroponic_garden.id,
            reading_date=date.today() - timedelta(days=1),
            temperature_f=70.0,
            humidity_percent=55.0,
            ph_level=6.3
        )
        test_db.add_all([reading1, reading2])
        test_db.commit()

        response = client.get(
            f"/gardens/{hydroponic_garden.id}/sensor-readings",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["temperature_f"] == 72.0 or data[1]["temperature_f"] == 72.0

    def test_get_garden_sensor_readings_empty(self, client, sample_user, outdoor_garden, user_token):
        """Test getting sensor readings for garden with no readings"""
        response = client.get(
            f"/gardens/{outdoor_garden.id}/sensor-readings",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_garden_sensor_readings_unauthorized(self, client, sample_user, second_user, hydroponic_garden):
        """Test that user cannot access another user's garden sensor readings"""
        from app.services.auth_service import AuthService
        second_token = AuthService.create_access_token(second_user.id, second_user.email)

        response = client.get(
            f"/gardens/{hydroponic_garden.id}/sensor-readings",
            headers={"Authorization": f"Bearer {second_token}"}
        )
        assert response.status_code == 403

    def test_get_sensor_readings_nonexistent_garden(self, client, user_token):
        """Test getting sensor readings for non-existent garden"""
        response = client.get(
            "/gardens/99999/sensor-readings",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 404


class TestGardenDeletionCascade:
    """Test garden deletion cascade behavior"""

    def test_delete_garden_cascade_to_plantings(self, client, sample_user, outdoor_garden, outdoor_planting_event, user_token):
        """Test that deleting garden cascades to delete plantings"""
        garden_id = outdoor_garden.id
        planting_id = outdoor_planting_event.id

        # Delete garden
        response = client.delete(
            f"/gardens/{garden_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 204

        # Verify planting is also deleted
        response = client.get(
            f"/planting-events/{planting_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 404

    def test_delete_garden_cascade_to_sensor_readings(self, client, sample_user, hydroponic_garden, user_token, test_db):
        """Test that deleting garden cascades to delete sensor readings"""
        from app.models.sensor_reading import SensorReading

        # Create sensor reading
        reading = SensorReading(
            user_id=sample_user.id,
            garden_id=hydroponic_garden.id,
            reading_date=date.today(),
            temperature_f=72.0
        )
        test_db.add(reading)
        test_db.commit()
        reading_id = reading.id

        # Delete garden
        response = client.delete(
            f"/gardens/{hydroponic_garden.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 204

        # Verify sensor reading is also deleted
        from app.models.sensor_reading import SensorReading
        deleted_reading = test_db.query(SensorReading).filter(SensorReading.id == reading_id).first()
        assert deleted_reading is None

    def test_delete_garden_cascade_complete(self, client, sample_user, outdoor_garden, outdoor_planting_event, sample_care_task, user_token, test_db):
        """Test complete cascade: garden -> planting -> tasks"""
        garden_id = outdoor_garden.id
        planting_id = outdoor_planting_event.id
        task_id = sample_care_task.id

        # Delete garden
        response = client.delete(
            f"/gardens/{garden_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 204

        # Verify entire cascade
        from app.models.care_task import CareTask
        deleted_task = test_db.query(CareTask).filter(CareTask.id == task_id).first()
        assert deleted_task is None

        response = client.get(
            f"/planting-events/{planting_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 404

        response = client.get(
            f"/gardens/{garden_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 404
