"""
Unit tests for database constraint enforcement.

These tests verify that the database constraints added in migrations 001-003
are properly enforced at the database level.

Test Coverage:
- Phase 1: Foreign keys, CASCADE behaviors, unique constraints
- Phase 2: ENUM types, NOT NULL, user-scoped unique names
- Phase 3: CHECK constraints for ranges, positive values, percentages

Author: Database Schema Audit
Date: 2026-02-01
"""

import pytest
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime, timedelta

from app.models import (
    User, Garden, PlantVariety, SeedBatch, PlantingEvent, CareTask,
    SensorReading, SoilSample, IrrigationEvent, IrrigationZone, IrrigationSource,
    Land, Tree, Structure, GerminationEvent, WateringEvent, CompanionRelationship
)


# =============================================================================
# PHASE 1: Critical Constraints Tests
# =============================================================================

@pytest.mark.database_constraints
class TestPhase1ForeignKeys:
    """Test Phase 1: Foreign key constraints and CASCADE behaviors"""

    def test_companion_relationship_plant_a_fk_enforced(self, db):
        """Test that plant_a_id must reference a valid plant variety"""
        with pytest.raises(IntegrityError) as exc_info:
            relationship = CompanionRelationship(
                plant_a_id=99999,  # Non-existent
                plant_b_id=99998,
                relationship_type="beneficial",
                mechanism="Test mechanism",
                confidence_level="high",
                source_reference="Test"
            )
            db.add(relationship)
            db.commit()

        assert "foreign key" in str(exc_info.value).lower()
        db.rollback()

    def test_companion_relationship_plant_b_fk_enforced(self, db):
        """Test that plant_b_id must reference a valid plant variety"""
        # Create a valid plant_a
        plant_a = PlantVariety(common_name="Test Plant A")
        db.add(plant_a)
        db.commit()

        with pytest.raises(IntegrityError) as exc_info:
            relationship = CompanionRelationship(
                plant_a_id=plant_a.id,
                plant_b_id=99999,  # Non-existent
                relationship_type="beneficial",
                mechanism="Test mechanism",
                confidence_level="high",
                source_reference="Test"
            )
            db.add(relationship)
            db.commit()

        assert "foreign key" in str(exc_info.value).lower()
        db.rollback()

    def test_companion_relationship_cascade_on_plant_delete(self, db):
        """Test that deleting a plant cascades to companion relationships"""
        plant_a = PlantVariety(common_name="Test Plant A")
        plant_b = PlantVariety(common_name="Test Plant B")
        db.add_all([plant_a, plant_b])
        db.commit()

        relationship = CompanionRelationship(
            plant_a_id=plant_a.id,
            plant_b_id=plant_b.id,
            relationship_type="beneficial",
            mechanism="Test",
            confidence_level="high",
            source_reference="Test"
        )
        db.add(relationship)
        db.commit()

        # Store relationship ID before cascade delete
        relationship_id = relationship.id

        # Delete plant_a should cascade to relationship
        db.delete(plant_a)
        db.commit()

        # Relationship should be gone
        assert db.query(CompanionRelationship).filter_by(id=relationship_id).first() is None

    def test_user_cascade_to_gardens(self, db, test_user):
        """Test that deleting a user cascades to their gardens"""
        garden = Garden(
            user_id=test_user.id,
            name="Test Garden",
            garden_type="outdoor",
            size_sq_ft=100
        )
        db.add(garden)
        db.commit()
        garden_id = garden.id

        # Delete user should cascade
        db.delete(test_user)
        db.commit()

        # Garden should be gone
        assert db.query(Garden).filter_by(id=garden_id).first() is None

    def test_sensor_reading_unique_per_day(self, db, test_user, test_garden):
        """Test that only one sensor reading per garden per day is allowed"""
        reading1 = SensorReading(
            user_id=test_user.id,
            garden_id=test_garden.id,
            reading_date=date.today(),
            temperature_f=70.0
        )
        db.add(reading1)
        db.commit()

        # Try to add another reading for the same garden on the same day
        with pytest.raises(IntegrityError) as exc_info:
            reading2 = SensorReading(
                user_id=test_user.id,
                garden_id=test_garden.id,
                reading_date=date.today(),  # Same date
                temperature_f=71.0
            )
            db.add(reading2)
            db.commit()

        assert "unique" in str(exc_info.value).lower()
        db.rollback()


@pytest.mark.database_constraints
class TestPhase1CheckConstraints:
    """Test Phase 1: CHECK constraints on CompanionRelationship"""

    def test_normalized_pair_enforced(self, db):
        """Test that plant_a_id must be < plant_b_id"""
        plant_a = PlantVariety(common_name="Test Plant A", id=10)
        plant_b = PlantVariety(common_name="Test Plant B", id=5)
        db.add_all([plant_a, plant_b])
        db.commit()

        with pytest.raises(IntegrityError) as exc_info:
            # plant_a.id (10) > plant_b.id (5), violates check
            relationship = CompanionRelationship(
                plant_a_id=10,
                plant_b_id=5,
                relationship_type="beneficial",
                mechanism="Test",
                confidence_level="high",
                source_reference="Test"
            )
            db.add(relationship)
            db.commit()

        assert "check_normalized_pair" in str(exc_info.value).lower()
        db.rollback()

    def test_not_self_companion_enforced(self, db):
        """Test that a plant cannot be its own companion"""
        plant = PlantVariety(common_name="Test Plant")
        db.add(plant)
        db.commit()

        with pytest.raises(IntegrityError) as exc_info:
            relationship = CompanionRelationship(
                plant_a_id=plant.id,
                plant_b_id=plant.id,  # Same as plant_a_id
                relationship_type="beneficial",
                mechanism="Test",
                confidence_level="high",
                source_reference="Test"
            )
            db.add(relationship)
            db.commit()

        assert "check_not_self_companion" in str(exc_info.value).lower()
        db.rollback()

    def test_effective_distance_positive_enforced(self, db):
        """Test that effective_distance_m must be > 0"""
        plant_a = PlantVariety(common_name="Test Plant A")
        plant_b = PlantVariety(common_name="Test Plant B")
        db.add_all([plant_a, plant_b])
        db.commit()

        with pytest.raises(IntegrityError) as exc_info:
            relationship = CompanionRelationship(
                plant_a_id=plant_a.id,
                plant_b_id=plant_b.id,
                relationship_type="beneficial",
                mechanism="Test",
                confidence_level="high",
                source_reference="Test",
                effective_distance_m=0  # Must be > 0
            )
            db.add(relationship)
            db.commit()

        assert "check_effective_distance_positive" in str(exc_info.value).lower()
        db.rollback()


# =============================================================================
# PHASE 2: High Priority Constraints Tests
# =============================================================================

@pytest.mark.database_constraints
class TestPhase2EnumConstraints:
    """Test Phase 2: ENUM type enforcement"""

    def test_irrigation_zone_delivery_type_enum_enforced(self, db, test_user, test_land):
        """Test that delivery_type must be a valid ENUM value"""
        with pytest.raises(IntegrityError) as exc_info:
            zone = IrrigationZone(
                user_id=test_user.id,
                land_id=test_land.id,
                name="Test Zone",
                delivery_type="invalid_type",  # Not in ENUM
                area_sq_m=10.0
            )
            db.add(zone)
            db.commit()

        assert "enum" in str(exc_info.value).lower() or "invalid input" in str(exc_info.value).lower()
        db.rollback()

    def test_irrigation_source_source_type_enum_enforced(self, db, test_user):
        """Test that source_type must be a valid ENUM value"""
        with pytest.raises(IntegrityError) as exc_info:
            source = IrrigationSource(
                user_id=test_user.id,
                name="Test Source",
                source_type="invalid_source",  # Not in ENUM
                capacity_liters=1000
            )
            db.add(source)
            db.commit()

        assert "enum" in str(exc_info.value).lower() or "invalid input" in str(exc_info.value).lower()
        db.rollback()


@pytest.mark.database_constraints
class TestPhase2NotNullConstraints:
    """Test Phase 2: NOT NULL constraints"""

    def test_planting_event_plant_count_not_null(self, db, test_user, test_garden, test_plant_variety):
        """Test that plant_count cannot be NULL"""
        with pytest.raises(IntegrityError) as exc_info:
            planting = PlantingEvent(
                user_id=test_user.id,
                garden_id=test_garden.id,
                plant_variety_id=test_plant_variety.id,
                planted_date=date.today(),
                plant_count=None  # Not allowed to be NULL
            )
            db.add(planting)
            db.commit()

        assert "not null" in str(exc_info.value).lower()
        db.rollback()

    def test_germination_event_seed_count_not_null(self, db, test_user, test_seed_batch, test_plant_variety):
        """Test that seed_count cannot be NULL"""
        with pytest.raises(IntegrityError) as exc_info:
            germination = GerminationEvent(
                user_id=test_user.id,
                seed_batch_id=test_seed_batch.id,
                plant_variety_id=test_plant_variety.id,
                started_date=date.today(),
                seed_count=None  # Not allowed to be NULL
            )
            db.add(germination)
            db.commit()

        assert "not null" in str(exc_info.value).lower()
        db.rollback()

    def test_germination_event_germinated_not_null(self, db, test_user, test_seed_batch, test_plant_variety):
        """Test that germinated cannot be NULL"""
        with pytest.raises(IntegrityError) as exc_info:
            germination = GerminationEvent(
                user_id=test_user.id,
                seed_batch_id=test_seed_batch.id,
                plant_variety_id=test_plant_variety.id,
                started_date=date.today(),
                seed_count=10,
                germinated=None  # Not allowed to be NULL
            )
            db.add(germination)
            db.commit()

        assert "not null" in str(exc_info.value).lower()
        db.rollback()


@pytest.mark.database_constraints
class TestPhase2UniqueConstraints:
    """Test Phase 2: User-scoped unique constraints"""

    def test_garden_name_unique_per_user(self, db, test_user):
        """Test that garden names must be unique per user (case-insensitive)"""
        garden1 = Garden(
            user_id=test_user.id,
            name="My Garden",
            garden_type="outdoor",
            size_sq_ft=100
        )
        db.add(garden1)
        db.commit()

        with pytest.raises(IntegrityError) as exc_info:
            garden2 = Garden(
                user_id=test_user.id,
                name="my garden",  # Case-insensitive duplicate
                garden_type="indoor",
                size_sq_ft=50
            )
            db.add(garden2)
            db.commit()

        assert "unique" in str(exc_info.value).lower()
        db.rollback()

    def test_land_name_unique_per_user(self, db, test_user):
        """Test that land names must be unique per user (case-insensitive)"""
        land1 = Land(
            user_id=test_user.id,
            name="My Land",
            width=10,
            height=10
        )
        db.add(land1)
        db.commit()

        with pytest.raises(IntegrityError) as exc_info:
            land2 = Land(
                user_id=test_user.id,
                name="MY LAND",  # Case-insensitive duplicate
                width=20,
                height=20
            )
            db.add(land2)
            db.commit()

        assert "unique" in str(exc_info.value).lower()
        db.rollback()


# =============================================================================
# PHASE 3: Data Quality Constraints Tests
# =============================================================================

@pytest.mark.database_constraints
class TestPhase3RangeConstraints:
    """Test Phase 3: Range CHECK constraints"""

    def test_garden_ph_range_enforced(self, db, test_user):
        """Test that garden pH must be between 0 and 14"""
        with pytest.raises(IntegrityError) as exc_info:
            garden = Garden(
                user_id=test_user.id,
                name="Test Garden",
                garden_type="outdoor",
                size_sq_ft=100,
                ph_min=15.0,  # Invalid: pH > 14
                ph_max=16.0
            )
            db.add(garden)
            db.commit()

        assert "check_garden_ph_range" in str(exc_info.value).lower()
        db.rollback()

    def test_sensor_reading_humidity_percentage_enforced(self, db, test_user, test_garden):
        """Test that humidity must be between 0 and 100"""
        with pytest.raises(IntegrityError) as exc_info:
            reading = SensorReading(
                user_id=test_user.id,
                garden_id=test_garden.id,
                reading_date=date.today(),
                humidity_percent=150  # Invalid: > 100
            )
            db.add(reading)
            db.commit()

        assert "check_sensor_reading_humidity_percentage" in str(exc_info.value).lower()
        db.rollback()

    def test_user_latitude_range_enforced(self, db):
        """Test that latitude must be between -90 and 90"""
        with pytest.raises(IntegrityError) as exc_info:
            user = User(
                email="test@example.com",
                hashed_password="hashed",
                latitude=100.0  # Invalid: > 90
            )
            db.add(user)
            db.commit()

        assert "check_user_latitude_range" in str(exc_info.value).lower()
        db.rollback()


@pytest.mark.database_constraints
class TestPhase3PositiveConstraints:
    """Test Phase 3: Positive value CHECK constraints"""

    def test_garden_size_positive_enforced(self, db, test_user):
        """Test that garden size must be > 0"""
        with pytest.raises(IntegrityError) as exc_info:
            garden = Garden(
                user_id=test_user.id,
                name="Test Garden",
                garden_type="outdoor",
                size_sq_ft=0  # Must be > 0
            )
            db.add(garden)
            db.commit()

        assert "check_garden_size_positive" in str(exc_info.value).lower()
        db.rollback()

    def test_planting_event_plant_count_positive_enforced(self, db, test_user, test_garden, test_plant_variety):
        """Test that plant_count must be > 0"""
        with pytest.raises(IntegrityError) as exc_info:
            planting = PlantingEvent(
                user_id=test_user.id,
                garden_id=test_garden.id,
                plant_variety_id=test_plant_variety.id,
                planted_date=date.today(),
                plant_count=0  # Must be > 0
            )
            db.add(planting)
            db.commit()

        assert "check_planting_event_plant_count_positive" in str(exc_info.value).lower()
        db.rollback()

    def test_tree_canopy_radius_non_negative_enforced(self, db, test_user, test_land):
        """Test that canopy_radius_m must be >= 0"""
        with pytest.raises(IntegrityError) as exc_info:
            tree = Tree(
                user_id=test_user.id,
                land_id=test_land.id,
                common_name="Test Tree",
                canopy_radius_m=-1.0,  # Must be >= 0
                position_x=0,
                position_y=0
            )
            db.add(tree)
            db.commit()

        assert "check_tree_canopy_radius_non_negative" in str(exc_info.value).lower()
        db.rollback()


@pytest.mark.database_constraints
class TestPhase3ConditionalConstraints:
    """Test Phase 3: Conditional CHECK constraints"""

    def test_hydro_system_type_required_if_hydroponic(self, db, test_user):
        """Test that hydroponic gardens must specify system type"""
        with pytest.raises(IntegrityError) as exc_info:
            garden = Garden(
                user_id=test_user.id,
                name="Test Hydro Garden",
                garden_type="indoor",
                size_sq_ft=100,
                is_hydroponic=True,
                hydro_system_type=None  # Required when is_hydroponic=True
            )
            db.add(garden)
            db.commit()

        assert "check_hydro_system_type_required" in str(exc_info.value).lower()
        db.rollback()

    def test_germination_date_required_if_germinated(self, db, test_user, test_seed_batch, test_plant_variety):
        """Test that germination_date is required when germinated=True"""
        with pytest.raises(IntegrityError) as exc_info:
            germination = GerminationEvent(
                user_id=test_user.id,
                seed_batch_id=test_seed_batch.id,
                plant_variety_id=test_plant_variety.id,
                started_date=date.today(),
                seed_count=10,
                germinated=True,
                germination_date=None  # Required when germinated=True
            )
            db.add(germination)
            db.commit()

        assert "check_germination_event_date_required_if_germinated" in str(exc_info.value).lower()
        db.rollback()

    def test_visual_placement_complete_or_null(self, db, test_user, test_garden, test_plant_variety):
        """Test that visual placement coordinates must all be set or all be null"""
        with pytest.raises(IntegrityError) as exc_info:
            # Only some coordinates set (invalid)
            planting = PlantingEvent(
                user_id=test_user.id,
                garden_id=test_garden.id,
                plant_variety_id=test_plant_variety.id,
                planted_date=date.today(),
                plant_count=1,
                visual_x=10,
                visual_y=20,
                visual_width=5,
                visual_height=None  # Must all be set or all be null
            )
            db.add(planting)
            db.commit()

        assert "check_planting_event_visual_placement_complete" in str(exc_info.value).lower()
        db.rollback()


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password"
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def test_garden(db, test_user):
    """Create a test garden"""
    garden = Garden(
        user_id=test_user.id,
        name="Test Garden",
        garden_type="outdoor",
        size_sq_ft=100
    )
    db.add(garden)
    db.commit()
    return garden


@pytest.fixture
def test_plant_variety(db):
    """Create a test plant variety"""
    plant = PlantVariety(common_name="Test Plant")
    db.add(plant)
    db.commit()
    return plant


@pytest.fixture
def test_seed_batch(db, test_user, test_plant_variety):
    """Create a test seed batch"""
    batch = SeedBatch(
        user_id=test_user.id,
        plant_variety_id=test_plant_variety.id,
        source="Test Source"
    )
    db.add(batch)
    db.commit()
    return batch


@pytest.fixture
def test_land(db, test_user):
    """Create a test land"""
    land = Land(
        user_id=test_user.id,
        name="Test Land",
        width=10,
        height=10
    )
    db.add(land)
    db.commit()
    return land
