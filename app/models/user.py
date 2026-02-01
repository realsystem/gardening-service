"""User model"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UnitSystem(str, enum.Enum):
    """Unit system preference"""
    METRIC = "metric"  # meters, celsius
    IMPERIAL = "imperial"  # feet, fahrenheit


class User(Base):
    """
    User account.

    Timezone assumption: created_at and updated_at are stored in UTC.
    PostgreSQL stores DateTime(timezone=True) in UTC and converts on retrieval.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Authorization
    is_admin = Column(Boolean, default=False, nullable=False, server_default='false')

    # Profile data
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    gardening_preferences = Column(Text, nullable=True)  # JSON string for preferences

    # Location data
    zip_code = Column(String(10), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    usda_zone = Column(String(10), nullable=True)  # e.g., "7a", "9b"

    # Unit preferences
    unit_system = Column(Enum(UnitSystem), nullable=False, server_default='metric')

    # Timestamps stored in UTC
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    gardens = relationship("Garden", back_populates="user", cascade="all, delete-orphan")
    lands = relationship("Land", back_populates="user", cascade="all, delete-orphan")
    seed_batches = relationship("SeedBatch", back_populates="user", cascade="all, delete-orphan")
    germination_events = relationship("GerminationEvent", back_populates="user", cascade="all, delete-orphan")
    planting_events = relationship("PlantingEvent", back_populates="user", cascade="all, delete-orphan")
    care_tasks = relationship("CareTask", back_populates="user", cascade="all, delete-orphan")
    sensor_readings = relationship("SensorReading", back_populates="user", cascade="all, delete-orphan")
    soil_samples = relationship("SoilSample", back_populates="user", cascade="all, delete-orphan")
    irrigation_events = relationship("IrrigationEvent", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")

    # Irrigation system relationships
    irrigation_sources = relationship("IrrigationSource", back_populates="user", cascade="all, delete-orphan")
    irrigation_zones = relationship("IrrigationZone", back_populates="user", cascade="all, delete-orphan")
    watering_events = relationship("WateringEvent", back_populates="user", cascade="all, delete-orphan")

    # Tree shading relationships
    trees = relationship("Tree", back_populates="user", cascade="all, delete-orphan")
    structures = relationship("Structure", back_populates="user", cascade="all, delete-orphan")
