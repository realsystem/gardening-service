"""GerminationEvent model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Boolean, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class GerminationEvent(Base):
    """
    Records when seeds are started for germination.
    This is the first step before planting.
    Tracks germination success rate.
    """
    __tablename__ = "germination_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seed_batch_id = Column(Integer, ForeignKey("seed_batches.id"), nullable=False)
    plant_variety_id = Column(Integer, ForeignKey("plant_varieties.id"), nullable=False)

    # Germination details
    started_date = Column(Date, nullable=False)
    germination_location = Column(String(100), nullable=True)  # e.g., "indoor", "greenhouse"
    seed_count = Column(Integer, nullable=True)

    # Outcome tracking
    germinated = Column(Boolean, default=False)
    germination_date = Column(Date, nullable=True)
    germination_count = Column(Integer, nullable=True)  # How many actually germinated

    # Success tracking (NEW)
    germination_success_rate = Column(Float, nullable=True)  # Percentage (0-100)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="germination_events")
    seed_batch = relationship("SeedBatch", back_populates="germination_events")
    plant_variety = relationship("PlantVariety", back_populates="germination_events")
    planting_events = relationship("PlantingEvent", back_populates="germination_event")
