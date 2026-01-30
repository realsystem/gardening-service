"""Irrigation zone model - represents a shared watering schedule"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class IrrigationZone(Base):
    """
    Represents a group of gardens that share the same irrigation schedule.

    The atomic unit of watering - all gardens in a zone get watered together.
    """
    __tablename__ = 'irrigation_zones'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    irrigation_source_id = Column(Integer, ForeignKey('irrigation_sources.id', ondelete='SET NULL'), nullable=True)
    name = Column(String, nullable=False)
    delivery_type = Column(String, nullable=False)  # drip, sprinkler, soaker, manual

    # Schedule stored as JSON with flexibility for different patterns
    # Example: {"frequency_days": 3, "duration_minutes": 20, "time_of_day": "06:00"}
    schedule = Column(JSON, nullable=True)

    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship('User', back_populates='irrigation_zones')
    source = relationship('IrrigationSource', back_populates='irrigation_zones')
    gardens = relationship('Garden', back_populates='irrigation_zone')
    watering_events = relationship('WateringEvent', back_populates='zone', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<IrrigationZone(id={self.id}, name='{self.name}', delivery='{self.delivery_type}')>"
