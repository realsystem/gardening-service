"""PlantVariety model - static reference data"""
from sqlalchemy import Column, Integer, String, Text, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class SunRequirement(str, enum.Enum):
    """Sun requirement levels"""
    FULL_SUN = "full_sun"           # 6+ hours direct sun
    PARTIAL_SUN = "partial_sun"     # 3-6 hours direct sun
    PARTIAL_SHADE = "partial_shade" # 3-6 hours, prefers morning sun
    FULL_SHADE = "full_shade"       # Less than 3 hours direct sun


class WaterRequirement(str, enum.Enum):
    """Water requirement levels"""
    LOW = "low"         # Drought tolerant
    MEDIUM = "medium"   # Regular watering
    HIGH = "high"       # Frequent watering


class PlantVariety(Base):
    """
    Static reference table for plant varieties.
    Contains growing metadata for different plant types.
    """
    __tablename__ = "plant_varieties"

    id = Column(Integer, primary_key=True, index=True)

    # Identification
    common_name = Column(String(100), nullable=False, index=True)
    scientific_name = Column(String(100), nullable=True)
    variety_name = Column(String(100), nullable=True)  # e.g., "Beefsteak", "Cherry"

    # Growing metadata
    days_to_germination_min = Column(Integer, nullable=True)  # Minimum days to germinate
    days_to_germination_max = Column(Integer, nullable=True)  # Maximum days to germinate
    days_to_harvest = Column(Integer, nullable=True)          # Days from planting to harvest

    # Spacing (in inches)
    spacing_inches = Column(Integer, nullable=True)           # Plant spacing
    row_spacing_inches = Column(Integer, nullable=True)       # Row spacing

    # Requirements
    sun_requirement = Column(SQLEnum(SunRequirement, values_callable=lambda x: [e.value for e in x]), nullable=True)
    water_requirement = Column(SQLEnum(WaterRequirement, values_callable=lambda x: [e.value for e in x]), nullable=True)

    # Additional info
    description = Column(Text, nullable=True)
    growing_notes = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    tags = Column(Text, nullable=True)  # Comma-separated tags: "easy,fruiting,perennial"

    # Nutrient optimization profile (growth stage dependent EC ranges in mS/cm)
    seedling_ec_min = Column(Float, nullable=True)  # Seedling stage EC minimum
    seedling_ec_max = Column(Float, nullable=True)  # Seedling stage EC maximum
    vegetative_ec_min = Column(Float, nullable=True)  # Vegetative stage EC minimum
    vegetative_ec_max = Column(Float, nullable=True)  # Vegetative stage EC maximum
    flowering_ec_min = Column(Float, nullable=True)  # Flowering stage EC minimum
    flowering_ec_max = Column(Float, nullable=True)  # Flowering stage EC maximum
    fruiting_ec_min = Column(Float, nullable=True)  # Fruiting stage EC minimum
    fruiting_ec_max = Column(Float, nullable=True)  # Fruiting stage EC maximum

    # pH optimization (usually consistent across growth stages)
    optimal_ph_min = Column(Float, nullable=True)  # Optimal pH minimum
    optimal_ph_max = Column(Float, nullable=True)  # Optimal pH maximum

    # Solution management schedule
    solution_change_days_min = Column(Integer, nullable=True)  # Minimum days between full changes
    solution_change_days_max = Column(Integer, nullable=True)  # Maximum days between full changes

    # Relationships
    seed_batches = relationship("SeedBatch", back_populates="plant_variety")
    germination_events = relationship("GerminationEvent", back_populates="plant_variety")
    planting_events = relationship("PlantingEvent", back_populates="plant_variety")
