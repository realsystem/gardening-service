"""User model"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


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

    # Timestamps stored in UTC
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    gardens = relationship("Garden", back_populates="user", cascade="all, delete-orphan")
    seed_batches = relationship("SeedBatch", back_populates="user", cascade="all, delete-orphan")
    germination_events = relationship("GerminationEvent", back_populates="user", cascade="all, delete-orphan")
    planting_events = relationship("PlantingEvent", back_populates="user", cascade="all, delete-orphan")
    care_tasks = relationship("CareTask", back_populates="user", cascade="all, delete-orphan")
    sensor_readings = relationship("SensorReading", back_populates="user", cascade="all, delete-orphan")
    soil_samples = relationship("SoilSample", back_populates="user", cascade="all, delete-orphan")
    irrigation_events = relationship("IrrigationEvent", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
