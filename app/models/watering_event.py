"""Watering event model - tracks actual irrigation that occurred"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class WateringEvent(Base):
    """
    Represents an actual watering that occurred.

    Records what happened (not what was scheduled) for analysis and rule evaluation.
    """
    __tablename__ = 'watering_events'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    irrigation_zone_id = Column(Integer, ForeignKey('irrigation_zones.id', ondelete='CASCADE'), nullable=False)

    watered_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    duration_minutes = Column(Float, nullable=False)  # How long water ran
    estimated_volume_liters = Column(Float, nullable=True)  # Optional volume estimate

    is_manual = Column(Boolean, default=False, nullable=False)  # Manual vs automated
    notes = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship('User', back_populates='watering_events')
    zone = relationship('IrrigationZone', back_populates='watering_events')

    def __repr__(self):
        return f"<WateringEvent(id={self.id}, zone_id={self.irrigation_zone_id}, duration={self.duration_minutes}min)>"
