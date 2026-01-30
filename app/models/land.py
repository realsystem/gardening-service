"""Land model - represents a physical land area for garden placement"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Land(Base):
    """
    Land area for placing gardens.

    Represents a user's physical land with defined dimensions.
    Gardens can be placed on the land using 2D coordinates.

    Coordinate system: Top-left origin (0, 0)
    - x increases rightward
    - y increases downward
    - Units are abstract (meters, feet, or grid squares - user's choice)
    """
    __tablename__ = "lands"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    width = Column(Float, nullable=False)  # abstract units
    height = Column(Float, nullable=False)  # abstract units

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="lands")
    gardens = relationship("Garden", back_populates="land", foreign_keys="Garden.land_id")
