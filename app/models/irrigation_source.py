"""Irrigation source model - represents where water comes from"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class IrrigationSource(Base):
    """
    Represents a water source for irrigation.

    Examples: city water, well, rainwater collection, manual watering
    """
    __tablename__ = 'irrigation_sources'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # city, well, rain, manual
    flow_capacity_lpm = Column(Float, nullable=True)  # Liters per minute (optional)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship('User', back_populates='irrigation_sources')
    irrigation_zones = relationship('IrrigationZone', back_populates='source', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<IrrigationSource(id={self.id}, name='{self.name}', type='{self.source_type}')>"
