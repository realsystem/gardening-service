"""Pytest configuration and fixtures for testing"""
import pytest
from datetime import date, datetime, timedelta
from freezegun import freeze_time
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UnitSystem
from app.models.plant_variety import PlantVariety, WaterRequirement, SunRequirement
from app.models.seed_batch import SeedBatch
from app.models.garden import Garden, GardenType, LightSourceType, HydroSystemType
from app.models.planting_event import PlantingEvent, PlantingMethod, PlantHealth
from app.models.care_task import CareTask, TaskType, TaskPriority, TaskStatus, TaskSource
from app.services.auth_service import AuthService


# Freeze time globally for all tests to ensure determinism
# All tests will run as if it's 2026-01-15 12:00:00 UTC
@pytest.fixture(scope="session", autouse=True)
def frozen_time():
    """Freeze time globally for all tests to ensure determinism"""
    with freeze_time("2026-01-15 12:00:00"):
        yield


@pytest.fixture
def reference_date():
    """
    Provide the frozen reference date for tests that need explicit date access.
    Returns: 2026-01-15 (the frozen date from frozen_time fixture)
    """
    return date(2026, 1, 15)


@pytest.fixture
def reference_datetime():
    """
    Provide the frozen reference datetime for tests that need explicit datetime access.
    Returns: 2026-01-15 12:00:00 (the frozen datetime from frozen_time fixture)
    """
    return datetime(2026, 1, 15, 12, 0, 0)


@pytest.fixture(scope="function")
def test_db():
    """
    Create an in-memory SQLite database for testing.
    Each test gets a fresh database instance.
    """
    # Use in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Enable foreign key constraints in SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# User fixtures
@pytest.fixture
def sample_user(test_db):
    """Create a sample user for testing"""
    user = User(
        email="test@example.com",
        hashed_password=AuthService.hash_password("testpass123"),
        display_name="Test User",
        city="Portland",
        unit_system=UnitSystem.METRIC
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def second_user(test_db):
    """Create a second user for testing authorization"""
    user = User(
        email="user2@example.com",
        hashed_password=AuthService.hash_password("password456"),
        display_name="Second User",
        unit_system=UnitSystem.METRIC
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def user_token(sample_user):
    """Generate JWT token for sample user"""
    return AuthService.create_access_token(sample_user.id, sample_user.email)


@pytest.fixture
def admin_user(test_db):
    """Create an admin user for testing"""
    user = User(
        email="admin@example.com",
        hashed_password=AuthService.hash_password("adminpass123"),
        display_name="Admin User",
        is_admin=True,
        unit_system=UnitSystem.METRIC
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    """Generate JWT token for admin user"""
    return AuthService.create_access_token(admin_user.id, admin_user.email)


# Plant variety fixtures
@pytest.fixture
def sample_plant_variety(test_db):
    """Create a sample plant variety for testing"""
    variety = PlantVariety(
        common_name="Tomato",
        scientific_name="Solanum lycopersicum",
        variety_name="Beefsteak",
        days_to_germination_min=5,
        days_to_germination_max=10,
        days_to_harvest=80,
        spacing_inches=24,
        row_spacing_inches=36,
        sun_requirement=SunRequirement.FULL_SUN,
        water_requirement=WaterRequirement.HIGH,
        description="Classic large tomato variety",
    )
    test_db.add(variety)
    test_db.commit()
    test_db.refresh(variety)
    return variety


@pytest.fixture
def lettuce_variety(test_db):
    """Create a lettuce variety for testing"""
    variety = PlantVariety(
        common_name="Lettuce",
        scientific_name="Lactuca sativa",
        variety_name="Romaine",
        days_to_germination_min=3,
        days_to_germination_max=7,
        days_to_harvest=60,
        spacing_inches=12,
        row_spacing_inches=18,
        sun_requirement=SunRequirement.PARTIAL_SUN,
        water_requirement=WaterRequirement.MEDIUM,
        description="Crisp romaine lettuce",
    )
    test_db.add(variety)
    test_db.commit()
    test_db.refresh(variety)
    return variety


# Seed batch fixtures
@pytest.fixture
def sample_seed_batch(test_db, sample_user, sample_plant_variety):
    """Create a sample seed batch"""
    seed_batch = SeedBatch(
        user_id=sample_user.id,
        plant_variety_id=sample_plant_variety.id,
        source="Local Nursery",
        harvest_year=2023,
        quantity=50,
        notes="Organic seeds"
    )
    test_db.add(seed_batch)
    test_db.commit()
    test_db.refresh(seed_batch)
    return seed_batch


# Garden fixtures
@pytest.fixture
def outdoor_garden(test_db, sample_user):
    """Create an outdoor garden"""
    garden = Garden(
        user_id=sample_user.id,
        name="Main Garden",
        description="Outdoor vegetable garden",
        garden_type=GardenType.OUTDOOR,
        is_hydroponic=False
    )
    test_db.add(garden)
    test_db.commit()
    test_db.refresh(garden)
    return garden


@pytest.fixture
def indoor_garden(test_db, sample_user):
    """Create an indoor garden"""
    garden = Garden(
        user_id=sample_user.id,
        name="Indoor Grow Room",
        description="Indoor grow setup",
        garden_type=GardenType.INDOOR,
        location="Basement",
        light_source_type=LightSourceType.LED,
        light_hours_per_day=16.0,
        temp_min_f=65.0,
        temp_max_f=75.0,
        humidity_min_percent=40.0,
        humidity_max_percent=60.0,
        container_type="Pots",
        grow_medium="Soil",
        is_hydroponic=False
    )
    test_db.add(garden)
    test_db.commit()
    test_db.refresh(garden)
    return garden


@pytest.fixture
def hydroponic_garden(test_db, sample_user):
    """Create a hydroponic garden"""
    garden = Garden(
        user_id=sample_user.id,
        name="Hydro Setup",
        description="NFT hydroponic system",
        garden_type=GardenType.INDOOR,
        location="Grow Tent",
        light_source_type=LightSourceType.LED,
        light_hours_per_day=18.0,
        temp_min_f=68.0,
        temp_max_f=78.0,
        humidity_min_percent=50.0,
        humidity_max_percent=70.0,
        container_type="NFT channels",
        grow_medium="Hydroponics",
        is_hydroponic=True,
        hydro_system_type=HydroSystemType.NFT,
        reservoir_size_liters=100.0,
        nutrient_schedule="General Hydroponics Flora Series",
        ph_min=5.5,
        ph_max=6.5,
        ec_min=1.2,
        ec_max=2.0,
        ppm_min=800,
        ppm_max=1400,
        water_temp_min_f=65.0,
        water_temp_max_f=72.0
    )
    test_db.add(garden)
    test_db.commit()
    test_db.refresh(garden)
    return garden


# Planting event fixtures
@pytest.fixture
def outdoor_planting_event(test_db, sample_user, outdoor_garden, sample_plant_variety):
    """Create an outdoor planting event"""
    planting_event = PlantingEvent(
        user_id=sample_user.id,
        garden_id=outdoor_garden.id,
        plant_variety_id=sample_plant_variety.id,
        planting_date=date.today(),
        planting_method=PlantingMethod.DIRECT_SOW,
        plant_count=6,
        location_in_garden="Bed 1, Row 2",
        health_status=PlantHealth.HEALTHY,
        notes="First planting of the season"
    )
    test_db.add(planting_event)
    test_db.commit()
    test_db.refresh(planting_event)
    return planting_event


@pytest.fixture
def indoor_planting_event(test_db, sample_user, indoor_garden, lettuce_variety):
    """Create an indoor planting event"""
    planting_event = PlantingEvent(
        user_id=sample_user.id,
        garden_id=indoor_garden.id,
        plant_variety_id=lettuce_variety.id,
        planting_date=date.today() - timedelta(days=10),
        planting_method=PlantingMethod.TRANSPLANT,
        plant_count=12,
        location_in_garden="Shelf 2",
        health_status=PlantHealth.HEALTHY
    )
    test_db.add(planting_event)
    test_db.commit()
    test_db.refresh(planting_event)
    return planting_event


@pytest.fixture
def hydroponic_planting_event(test_db, sample_user, hydroponic_garden, lettuce_variety):
    """Create a hydroponic planting event"""
    planting_event = PlantingEvent(
        user_id=sample_user.id,
        garden_id=hydroponic_garden.id,
        plant_variety_id=lettuce_variety.id,
        planting_date=date.today() - timedelta(days=5),
        planting_method=PlantingMethod.TRANSPLANT,
        plant_count=24,
        location_in_garden="Channel 1",
        health_status=PlantHealth.HEALTHY
    )
    test_db.add(planting_event)
    test_db.commit()
    test_db.refresh(planting_event)
    return planting_event


# Care task fixtures
@pytest.fixture
def sample_care_task(test_db, sample_user, outdoor_planting_event):
    """Create a sample care task"""
    task = CareTask(
        user_id=sample_user.id,
        planting_event_id=outdoor_planting_event.id,
        task_type=TaskType.WATER,
        task_source=TaskSource.AUTO_GENERATED,
        title="Water Tomato - Beefsteak",
        description="Water plants in Bed 1, Row 2",
        priority=TaskPriority.MEDIUM,
        due_date=date.today(),
        is_recurring=False,
        status=TaskStatus.PENDING
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    return task


@pytest.fixture
def completed_task(test_db, sample_user, outdoor_planting_event):
    """Create a completed task"""
    task = CareTask(
        user_id=sample_user.id,
        planting_event_id=outdoor_planting_event.id,
        task_type=TaskType.FERTILIZE,
        task_source=TaskSource.MANUAL,
        title="Fertilize tomatoes",
        description="Apply organic fertilizer",
        priority=TaskPriority.LOW,
        due_date=date.today() - timedelta(days=1),
        is_recurring=False,
        status=TaskStatus.COMPLETED,
        completed_date=date.today() - timedelta(days=1)
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    return task


@pytest.fixture
def high_priority_task(test_db, sample_user, hydroponic_planting_event):
    """Create a high priority task"""
    task = CareTask(
        user_id=sample_user.id,
        planting_event_id=hydroponic_planting_event.id,
        task_type=TaskType.ADJUST_PH,
        task_source=TaskSource.AUTO_GENERATED,
        title="Adjust pH in Hydro Setup",
        description="pH is too high (7.2). Target: 5.5-6.5. Add pH DOWN solution.",
        priority=TaskPriority.HIGH,
        due_date=date.today(),
        is_recurring=False,
        status=TaskStatus.PENDING
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    return task


# Alias fixtures for compatibility with different test files
@pytest.fixture
def db(test_db):
    """Alias for test_db fixture (for backward compatibility)"""
    return test_db
