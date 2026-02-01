"""PlantingEvent model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Text, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class PlantingMethod(str, enum.Enum):
    """Method used for planting"""
    DIRECT_SOW = "direct_sow"      # Seeds planted directly in garden
    TRANSPLANT = "transplant"       # Seedlings transplanted from germination


class PlantHealth(str, enum.Enum):
    """Plant health status"""
    HEALTHY = "healthy"
    STRESSED = "stressed"
    DISEASED = "diseased"


class PlantingEvent(Base):
    """
    Records when and where plants are planted in the garden.
    This is the anchor for lifecycle calculations.
    Tracks plant health and notes.
    """
    __tablename__ = "planting_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    garden_id = Column(Integer, ForeignKey("gardens.id"), nullable=False)
    plant_variety_id = Column(Integer, ForeignKey("plant_varieties.id"), nullable=False)
    germination_event_id = Column(Integer, ForeignKey("germination_events.id"), nullable=True)

    # Planting details
    planting_date = Column(Date, nullable=False, index=True)  # Key date for calculations
    planting_method = Column(SQLEnum(PlantingMethod, values_callable=lambda x: [e.value for e in x]), nullable=False)
    plant_count = Column(Integer, nullable=True)
    location_in_garden = Column(String(200), nullable=True)  # e.g., "Bed 2, Row 3"

    # Plant tracking (NEW)
    health_status = Column(SQLEnum(PlantHealth, values_callable=lambda x: [e.value for e in x]), nullable=True)
    plant_notes = Column(Text, nullable=True)

    # Spatial position for companion planting analysis
    x = Column(Float, nullable=True)
    y = Column(Float, nullable=True)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="planting_events")
    garden = relationship("Garden", back_populates="planting_events")
    plant_variety = relationship("PlantVariety", back_populates="planting_events")
    germination_event = relationship("GerminationEvent", back_populates="planting_events")
    care_tasks = relationship("CareTask", back_populates="planting_event", cascade="all, delete-orphan")
    soil_samples = relationship("SoilSample", back_populates="planting_event", cascade="all, delete-orphan")
    irrigation_events = relationship("IrrigationEvent", back_populates="planting_event", cascade="all, delete-orphan")
