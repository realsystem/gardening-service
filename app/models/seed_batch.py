"""SeedBatch model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class SeedBatch(Base):
    """
    A batch of seeds from a single source and year.
    Tracks seed inventory and viability.
    """
    __tablename__ = "seed_batches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plant_variety_id = Column(Integer, ForeignKey("plant_varieties.id"), nullable=False)

    # Batch information
    source = Column(String(200), nullable=True)  # Where seeds came from
    harvest_year = Column(Integer, nullable=True)  # Year seeds were harvested/packaged
    quantity = Column(Integer, nullable=True)     # Number of seeds (if known)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="seed_batches")
    plant_variety = relationship("PlantVariety", back_populates="seed_batches")
    germination_events = relationship("GerminationEvent", back_populates="seed_batch", cascade="all, delete-orphan")
