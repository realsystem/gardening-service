"""Tree model - represents trees that cast shade on gardens"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Tree(Base):
    """
    Represents a tree on a land plot that can cast shade on nearby gardens.

    Trees have spatial coordinates, physical dimensions (canopy radius, height),
    and a species reference (plant variety). They impact nearby gardens by
    reducing their effective sun exposure based on geometric intersection.

    Coordinate system matches Land: Top-left origin (0, 0)
    - x increases rightward
    - y increases downward
    - Units match the land's abstract units (meters, feet, etc.)
    """
    __tablename__ = "trees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    land_id = Column(Integer, ForeignKey("lands.id", ondelete='CASCADE'), nullable=False, index=True)

    # Tree identification
    name = Column(String(100), nullable=False)  # User-friendly name (e.g., "Oak in backyard")
    species_id = Column(Integer, ForeignKey("plant_varieties.id"), nullable=True, index=True)  # Link to tree variety

    # Spatial location (center point of trunk)
    x = Column(Float, nullable=False)  # x-coordinate on land
    y = Column(Float, nullable=False)  # y-coordinate on land

    # Physical dimensions
    canopy_radius = Column(Float, nullable=False)  # Radius of canopy in same units as land
    height = Column(Float, nullable=True)  # Tree height (optional, for future sun angle calculations)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="trees")
    land = relationship("Land", back_populates="trees")
    species = relationship("PlantVariety")
