from sqlalchemy import Column, Integer, Float, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SoilSample(Base):
    """Soil sample tracking for gardens and planting events."""
    __tablename__ = "soil_samples"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    garden_id = Column(Integer, ForeignKey("gardens.id", ondelete="CASCADE"), nullable=True)
    planting_event_id = Column(Integer, ForeignKey("planting_events.id", ondelete="CASCADE"), nullable=True)

    # Soil chemistry
    ph = Column(Float, nullable=False)  # pH level (0-14, typically 4-9)
    nitrogen_ppm = Column(Float, nullable=True)  # Nitrogen in parts per million
    phosphorus_ppm = Column(Float, nullable=True)  # Phosphorus in parts per million
    potassium_ppm = Column(Float, nullable=True)  # Potassium in parts per million
    organic_matter_percent = Column(Float, nullable=True)  # Organic matter percentage (0-100)
    moisture_percent = Column(Float, nullable=True)  # Soil moisture percentage (0-100)

    # Metadata
    date_collected = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="soil_samples")
    garden = relationship("Garden", back_populates="soil_samples")
    planting_event = relationship("PlantingEvent", back_populates="soil_samples")
