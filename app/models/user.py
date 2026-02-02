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


class UserGroup(str, enum.Enum):
    """User group for progressive feature disclosure"""
    AMATEUR_GARDENER = "amateur_gardener"  # Simplified interface, 90% of users
    FARMER = "farmer"  # Intermediate features, commercial growers
    SCIENTIFIC_RESEARCHER = "scientific_researcher"  # Full access to all features


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

    # User group for progressive feature disclosure
    user_group = Column(Enum(UserGroup), nullable=False, server_default='amateur_gardener')

    # Feature toggles (amateur users control visibility)
    show_trees = Column(Boolean, default=False, nullable=False, server_default='false')
    enable_alerts = Column(Boolean, default=False, nullable=False, server_default='false')

    # Compliance audit fields (immutable, admin-only visibility)
    restricted_crop_flag = Column(Boolean, default=False, nullable=False, server_default='false')
    restricted_crop_count = Column(Integer, default=0, nullable=False, server_default='0')
    restricted_crop_first_violation = Column(DateTime(timezone=True), nullable=True)
    restricted_crop_last_violation = Column(DateTime(timezone=True), nullable=True)
    restricted_crop_reason = Column(String(100), nullable=True)  # Internal reason code

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
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")

    # Tree shading relationships (hidden for amateur users by default)
    trees = relationship("Tree", back_populates="user", cascade="all, delete-orphan")
    structures = relationship("Structure", back_populates="user", cascade="all, delete-orphan")
