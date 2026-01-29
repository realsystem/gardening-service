"""Pytest configuration and fixtures for testing"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.plant_variety import PlantVariety, WaterRequirement, SunRequirement


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

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


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
