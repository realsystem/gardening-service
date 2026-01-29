"""Tests for database models and relationships"""
import pytest
from datetime import date, timedelta

from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.plant_variety import PlantVariety, WaterRequirement, SunRequirement
from app.models.seed_batch import SeedBatch
from app.models.garden import Garden, GardenType, LightSourceType, HydroSystemType
from app.models.planting_event import PlantingEvent, PlantingMethod, PlantHealth
from app.models.sensor_reading import SensorReading
from app.models.care_task import CareTask, TaskType, TaskPriority, TaskStatus, TaskSource


class TestUserModel:
    """Test User model"""

    def test_create_user(self, test_db, sample_user):
        """Test creating a user"""
        assert sample_user.id is not None
        assert sample_user.email == "test@example.com"
        assert sample_user.full_name == "Test User"
        assert sample_user.hashed_password is not None

    def test_user_relationships(self, test_db, sample_user, outdoor_garden, sample_care_task):
        """Test user relationships with gardens and tasks"""
        user = test_db.query(User).filter(User.id == sample_user.id).first()

        assert len(user.gardens) == 1
        assert user.gardens[0].name == "Main Garden"

        assert len(user.care_tasks) >= 1


class TestUserProfileModel:
    """Test UserProfile model"""

    def test_create_user_profile(self, test_db, sample_user_profile):
        """Test creating a user profile"""
        assert sample_user_profile.id is not None
        assert sample_user_profile.bio == "Enthusiastic home gardener"
        assert sample_user_profile.location == "Portland, OR"

    def test_user_profile_relationship(self, test_db, sample_user, sample_user_profile):
        """Test user profile relationship"""
        user = test_db.query(User).filter(User.id == sample_user.id).first()
        assert user.profile is not None
        assert user.profile.bio == "Enthusiastic home gardener"


class TestPlantVarietyModel:
    """Test PlantVariety model"""

    def test_create_plant_variety(self, test_db, sample_plant_variety):
        """Test creating a plant variety"""
        assert sample_plant_variety.id is not None
        assert sample_plant_variety.common_name == "Tomato"
        assert sample_plant_variety.days_to_harvest == 80
        assert sample_plant_variety.water_requirement == WaterRequirement.HIGH

    def test_plant_variety_enums(self, test_db):
        """Test enum values in plant variety"""
        variety = PlantVariety(
            common_name="Shade Plant",
            sun_requirement=SunRequirement.FULL_SHADE,
            water_requirement=WaterRequirement.LOW
        )
        test_db.add(variety)
        test_db.commit()

        assert variety.sun_requirement == SunRequirement.FULL_SHADE
        assert variety.water_requirement == WaterRequirement.LOW


class TestSeedBatchModel:
    """Test SeedBatch model"""

    def test_create_seed_batch(self, test_db, sample_seed_batch):
        """Test creating a seed batch"""
        assert sample_seed_batch.id is not None
        assert sample_seed_batch.source == "Local Nursery"
        assert sample_seed_batch.quantity == 50

    def test_seed_batch_relationships(self, test_db, sample_seed_batch, sample_user, sample_plant_variety):
        """Test seed batch relationships"""
        batch = test_db.query(SeedBatch).filter(SeedBatch.id == sample_seed_batch.id).first()

        assert batch.user.email == sample_user.email
        assert batch.plant_variety.common_name == sample_plant_variety.common_name


class TestGardenModel:
    """Test Garden model"""

    def test_create_outdoor_garden(self, test_db, outdoor_garden):
        """Test creating an outdoor garden"""
        assert outdoor_garden.id is not None
        assert outdoor_garden.name == "Main Garden"
        assert outdoor_garden.garden_type == GardenType.OUTDOOR
        assert outdoor_garden.is_hydroponic == 0

    def test_create_indoor_garden(self, test_db, indoor_garden):
        """Test creating an indoor garden"""
        assert indoor_garden.id is not None
        assert indoor_garden.garden_type == GardenType.INDOOR
        assert indoor_garden.light_source_type == LightSourceType.LED
        assert indoor_garden.light_hours_per_day == 16.0
        assert indoor_garden.is_hydroponic == 0

    def test_create_hydroponic_garden(self, test_db, hydroponic_garden):
        """Test creating a hydroponic garden"""
        assert hydroponic_garden.id is not None
        assert hydroponic_garden.is_hydroponic == 1
        assert hydroponic_garden.hydro_system_type == HydroSystemType.NFT
        assert hydroponic_garden.reservoir_size_liters == 100.0
        assert hydroponic_garden.ph_min == 5.5
        assert hydroponic_garden.ph_max == 6.5
        assert hydroponic_garden.ec_min == 1.2
        assert hydroponic_garden.ec_max == 2.0

    def test_garden_relationships(self, test_db, outdoor_garden, outdoor_planting_event):
        """Test garden relationships"""
        garden = test_db.query(Garden).filter(Garden.id == outdoor_garden.id).first()

        assert len(garden.planting_events) >= 1
        assert garden.planting_events[0].location_in_garden == "Bed 1, Row 2"


class TestPlantingEventModel:
    """Test PlantingEvent model"""

    def test_create_planting_event(self, test_db, outdoor_planting_event):
        """Test creating a planting event"""
        assert outdoor_planting_event.id is not None
        assert outdoor_planting_event.planting_method == PlantingMethod.DIRECT_SOW
        assert outdoor_planting_event.plant_count == 6
        assert outdoor_planting_event.health_status == PlantHealth.HEALTHY

    def test_planting_event_relationships(self, test_db, outdoor_planting_event):
        """Test planting event relationships"""
        event = test_db.query(PlantingEvent).filter(
            PlantingEvent.id == outdoor_planting_event.id
        ).first()

        assert event.garden.name == "Main Garden"
        assert event.plant_variety.common_name == "Tomato"
        assert event.user.email == "test@example.com"


class TestSensorReadingModel:
    """Test SensorReading model"""

    def test_create_indoor_sensor_reading(self, test_db, indoor_sensor_reading):
        """Test creating an indoor sensor reading"""
        assert indoor_sensor_reading.id is not None
        assert indoor_sensor_reading.temperature_f == 70.0
        assert indoor_sensor_reading.humidity_percent == 55.0
        assert indoor_sensor_reading.light_hours == 16.0
        assert indoor_sensor_reading.ph_level is None

    def test_create_hydroponic_sensor_reading(self, test_db, hydroponic_sensor_reading):
        """Test creating a hydroponic sensor reading"""
        assert hydroponic_sensor_reading.id is not None
        assert hydroponic_sensor_reading.temperature_f == 72.0
        assert hydroponic_sensor_reading.ph_level == 6.0
        assert hydroponic_sensor_reading.ec_ms_cm == 1.5
        assert hydroponic_sensor_reading.ppm == 1050
        assert hydroponic_sensor_reading.water_temp_f == 68.0

    def test_sensor_reading_relationships(self, test_db, indoor_sensor_reading):
        """Test sensor reading relationships"""
        reading = test_db.query(SensorReading).filter(
            SensorReading.id == indoor_sensor_reading.id
        ).first()

        assert reading.garden.name == "Indoor Grow Room"
        assert reading.user.email == "test@example.com"


class TestCareTaskModel:
    """Test CareTask model"""

    def test_create_care_task(self, test_db, sample_care_task):
        """Test creating a care task"""
        assert sample_care_task.id is not None
        assert sample_care_task.task_type == TaskType.WATER
        assert sample_care_task.priority == TaskPriority.MEDIUM
        assert sample_care_task.status == TaskStatus.PENDING
        assert sample_care_task.is_recurring is False

    def test_completed_task(self, test_db, completed_task):
        """Test completed task"""
        assert completed_task.status == TaskStatus.COMPLETED
        assert completed_task.completed_date is not None

    def test_high_priority_task(self, test_db, high_priority_task):
        """Test high priority task"""
        assert high_priority_task.priority == TaskPriority.HIGH
        assert high_priority_task.task_type == TaskType.ADJUST_PH

    def test_care_task_relationships(self, test_db, sample_care_task):
        """Test care task relationships"""
        task = test_db.query(CareTask).filter(CareTask.id == sample_care_task.id).first()

        assert task.user.email == "test@example.com"
        assert task.planting_event.plant_variety.common_name == "Tomato"


class TestModelCascadeDeletes:
    """Test cascade delete behavior"""

    def test_delete_garden_cascades_to_planting_events(self, test_db, outdoor_garden, outdoor_planting_event):
        """Test that deleting a garden deletes associated planting events"""
        garden_id = outdoor_garden.id
        planting_event_id = outdoor_planting_event.id

        # Delete garden
        test_db.delete(outdoor_garden)
        test_db.commit()

        # Verify planting event was deleted
        event = test_db.query(PlantingEvent).filter(PlantingEvent.id == planting_event_id).first()
        assert event is None

    def test_delete_planting_event_cascades_to_tasks(self, test_db, outdoor_planting_event, sample_care_task):
        """Test that deleting a planting event deletes associated tasks"""
        planting_event_id = outdoor_planting_event.id
        task_id = sample_care_task.id

        # Delete planting event
        test_db.delete(outdoor_planting_event)
        test_db.commit()

        # Verify task was deleted
        task = test_db.query(CareTask).filter(CareTask.id == task_id).first()
        assert task is None
