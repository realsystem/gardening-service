"""Garden model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class GardenType(str, enum.Enum):
    """Garden type classification"""
    OUTDOOR = "outdoor"
    INDOOR = "indoor"


class LightSourceType(str, enum.Enum):
    """Indoor light source types"""
    LED = "led"
    FLUORESCENT = "fluorescent"
    NATURAL_SUPPLEMENT = "natural_supplement"
    HPS = "hps"  # High-Pressure Sodium
    MH = "mh"    # Metal Halide


class HydroSystemType(str, enum.Enum):
    """Hydroponic system types"""
    NFT = "nft"  # Nutrient Film Technique
    DWC = "dwc"  # Deep Water Culture
    EBB_FLOW = "ebb_flow"  # Ebb and Flow
    AEROPONICS = "aeroponics"
    DRIP = "drip"
    WICK = "wick"


class Garden(Base):
    """A user's garden or growing area (outdoor or indoor)"""
    __tablename__ = "gardens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    garden_type = Column(SQLEnum(GardenType, values_callable=lambda x: [e.value for e in x]), nullable=False, default=GardenType.OUTDOOR)

    # Indoor garden specific fields
    location = Column(String(100), nullable=True)  # Room or setup location
    light_source_type = Column(SQLEnum(LightSourceType, values_callable=lambda x: [e.value for e in x]), nullable=True)
    light_hours_per_day = Column(Float, nullable=True)  # Daily light hours
    temp_min_f = Column(Float, nullable=True)  # Minimum temperature in Fahrenheit
    temp_max_f = Column(Float, nullable=True)  # Maximum temperature in Fahrenheit
    humidity_min_percent = Column(Float, nullable=True)  # Minimum humidity percentage
    humidity_max_percent = Column(Float, nullable=True)  # Maximum humidity percentage
    container_type = Column(String(100), nullable=True)  # pot, tray, hydroponic system
    grow_medium = Column(String(100), nullable=True)  # soil, hydroponics, coco coir

    # Hydroponics-specific fields
    is_hydroponic = Column(Integer, nullable=False, default=0)  # Boolean flag (0 or 1)
    hydro_system_type = Column(SQLEnum(HydroSystemType, values_callable=lambda x: [e.value for e in x]), nullable=True)  # NFT, DWC, etc.
    reservoir_size_liters = Column(Float, nullable=True)  # Reservoir capacity
    nutrient_schedule = Column(Text, nullable=True)  # Nutrient solution schedule/notes
    ph_min = Column(Float, nullable=True)  # Minimum pH target
    ph_max = Column(Float, nullable=True)  # Maximum pH target
    ec_min = Column(Float, nullable=True)  # Minimum EC (mS/cm)
    ec_max = Column(Float, nullable=True)  # Maximum EC (mS/cm)
    ppm_min = Column(Integer, nullable=True)  # Minimum PPM
    ppm_max = Column(Integer, nullable=True)  # Maximum PPM
    water_temp_min_f = Column(Float, nullable=True)  # Minimum water temperature
    water_temp_max_f = Column(Float, nullable=True)  # Maximum water temperature

    # Spatial layout fields (optional - for visual land layout)
    land_id = Column(Integer, ForeignKey("lands.id", ondelete='SET NULL'), nullable=True, index=True)
    x = Column(Float, nullable=True)  # x-coordinate on land (top-left origin)
    y = Column(Float, nullable=True)  # y-coordinate on land (top-left origin)
    width = Column(Float, nullable=True)  # garden width in abstract units
    height = Column(Float, nullable=True)  # garden height in abstract units

    # Irrigation system fields
    irrigation_zone_id = Column(Integer, ForeignKey("irrigation_zones.id", ondelete='SET NULL'), nullable=True, index=True)
    mulch_depth_inches = Column(Float, nullable=True)  # Mulch depth affects water retention
    is_raised_bed = Column(Integer, nullable=False, default=0)  # Raised beds drain differently
    soil_texture_override = Column(String(50), nullable=True)  # sandy, loamy, clay (overrides defaults)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="gardens")
    land = relationship("Land", back_populates="gardens", foreign_keys=[land_id])
    irrigation_zone = relationship("IrrigationZone", back_populates="gardens", foreign_keys=[irrigation_zone_id])
    planting_events = relationship("PlantingEvent", back_populates="garden", cascade="all, delete-orphan")
    sensor_readings = relationship("SensorReading", back_populates="garden", cascade="all, delete-orphan")
    soil_samples = relationship("SoilSample", back_populates="garden", cascade="all, delete-orphan")
    irrigation_events = relationship("IrrigationEvent", back_populates="garden", cascade="all, delete-orphan")
