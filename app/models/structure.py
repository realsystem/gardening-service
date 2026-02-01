"""Structure model - represents buildings and obstacles that cast shadows on gardens"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Structure(Base):
    """
    Represents a structure (building, fence, wall, etc.) on a land plot that can cast shadows.

    Structures have spatial coordinates, physical dimensions (width, depth, height),
    and can cast shadows on nearby gardens based on their height and the sun's position.

    Coordinate system matches Land: Top-left origin (0, 0)
    - x increases rightward
    - y increases downward
    - Units match the land's abstract units (meters, feet, etc.)
    """
    __tablename__ = "structures"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    land_id = Column(Integer, ForeignKey("lands.id", ondelete='CASCADE'), nullable=False, index=True)

    # Structure identification
    name = Column(String(100), nullable=False)  # User-friendly name (e.g., "Garage", "Shed", "North Fence")

    # Spatial location (top-left corner of structure footprint)
    x = Column(Float, nullable=False)  # x-coordinate on land
    y = Column(Float, nullable=False)  # y-coordinate on land

    # Physical dimensions (footprint)
    width = Column(Float, nullable=False)  # Width in same units as land
    depth = Column(Float, nullable=False)  # Depth/length in same units as land

    # Vertical dimension for shadow calculation
    height = Column(Float, nullable=False)  # Structure height (affects shadow length)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="structures")
    land = relationship("Land", back_populates="structures")
