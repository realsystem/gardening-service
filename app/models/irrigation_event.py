from sqlalchemy import Column, Integer, Float, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.database import Base


class IrrigationMethod(str, Enum):
    """Methods of irrigation."""
    DRIP = "drip"
    SPRINKLER = "sprinkler"
    HAND_WATERING = "hand_watering"
    SOAKER_HOSE = "soaker_hose"
    FLOOD = "flood"
    MISTING = "misting"


class IrrigationEvent(Base):
    """Irrigation event tracking for gardens and plantings."""
    __tablename__ = "irrigation_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    garden_id = Column(Integer, ForeignKey("gardens.id", ondelete="CASCADE"), nullable=True)
    planting_event_id = Column(Integer, ForeignKey("planting_events.id", ondelete="CASCADE"), nullable=True)

    # Irrigation details
    irrigation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    water_volume_liters = Column(Float, nullable=True)  # Volume in liters
    irrigation_method = Column(SQLEnum(IrrigationMethod), nullable=False)
    duration_minutes = Column(Integer, nullable=True)  # Duration in minutes

    # Metadata
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="irrigation_events")
    garden = relationship("Garden", back_populates="irrigation_events")
    planting_event = relationship("PlantingEvent", back_populates="irrigation_events")
