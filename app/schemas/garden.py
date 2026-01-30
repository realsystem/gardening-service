"""Garden schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.garden import GardenType, LightSourceType, HydroSystemType


class GardenCreate(BaseModel):
    """Schema for creating a new garden"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    garden_type: GardenType = GardenType.OUTDOOR
    # Indoor garden specific fields
    location: Optional[str] = Field(None, max_length=100)
    light_source_type: Optional[LightSourceType] = None
    light_hours_per_day: Optional[float] = Field(None, ge=0, le=24)
    temp_min_f: Optional[float] = None
    temp_max_f: Optional[float] = None
    humidity_min_percent: Optional[float] = Field(None, ge=0, le=100)
    humidity_max_percent: Optional[float] = Field(None, ge=0, le=100)
    container_type: Optional[str] = Field(None, max_length=100)
    grow_medium: Optional[str] = Field(None, max_length=100)
    # Hydroponics-specific fields
    is_hydroponic: bool = False
    hydro_system_type: Optional[HydroSystemType] = None
    reservoir_size_liters: Optional[float] = Field(None, gt=0)
    nutrient_schedule: Optional[str] = None
    ph_min: Optional[float] = Field(None, ge=0, le=14)
    ph_max: Optional[float] = Field(None, ge=0, le=14)
    ec_min: Optional[float] = Field(None, ge=0)
    ec_max: Optional[float] = Field(None, ge=0)
    ppm_min: Optional[int] = Field(None, ge=0)
    ppm_max: Optional[int] = Field(None, ge=0)
    water_temp_min_f: Optional[float] = None
    water_temp_max_f: Optional[float] = None
    # Irrigation system fields
    irrigation_zone_id: Optional[int] = None
    mulch_depth_inches: Optional[float] = Field(None, ge=0)
    is_raised_bed: bool = False
    soil_texture_override: Optional[str] = Field(None, max_length=50)


class GardenUpdate(BaseModel):
    """Schema for updating a garden"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    light_source_type: Optional[LightSourceType] = None
    light_hours_per_day: Optional[float] = Field(None, ge=0, le=24)
    temp_min_f: Optional[float] = None
    temp_max_f: Optional[float] = None
    humidity_min_percent: Optional[float] = Field(None, ge=0, le=100)
    humidity_max_percent: Optional[float] = Field(None, ge=0, le=100)
    container_type: Optional[str] = Field(None, max_length=100)
    grow_medium: Optional[str] = Field(None, max_length=100)
    # Hydroponics-specific fields
    is_hydroponic: Optional[bool] = None
    hydro_system_type: Optional[HydroSystemType] = None
    reservoir_size_liters: Optional[float] = Field(None, gt=0)
    nutrient_schedule: Optional[str] = None
    ph_min: Optional[float] = Field(None, ge=0, le=14)
    ph_max: Optional[float] = Field(None, ge=0, le=14)
    ec_min: Optional[float] = Field(None, ge=0)
    ec_max: Optional[float] = Field(None, ge=0)
    ppm_min: Optional[int] = Field(None, ge=0)
    ppm_max: Optional[int] = Field(None, ge=0)
    water_temp_min_f: Optional[float] = None
    water_temp_max_f: Optional[float] = None
    # Irrigation system fields
    irrigation_zone_id: Optional[int] = None
    mulch_depth_inches: Optional[float] = Field(None, ge=0)
    is_raised_bed: Optional[bool] = None
    soil_texture_override: Optional[str] = Field(None, max_length=50)


class GardenResponse(BaseModel):
    """Schema for garden response"""
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    garden_type: GardenType
    # Indoor garden specific fields
    location: Optional[str] = None
    light_source_type: Optional[LightSourceType] = None
    light_hours_per_day: Optional[float] = None
    temp_min_f: Optional[float] = None
    temp_max_f: Optional[float] = None
    humidity_min_percent: Optional[float] = None
    humidity_max_percent: Optional[float] = None
    container_type: Optional[str] = None
    grow_medium: Optional[str] = None
    # Hydroponics-specific fields
    is_hydroponic: bool
    hydro_system_type: Optional[HydroSystemType] = None
    reservoir_size_liters: Optional[float] = None
    nutrient_schedule: Optional[str] = None
    ph_min: Optional[float] = None
    ph_max: Optional[float] = None
    ec_min: Optional[float] = None
    ec_max: Optional[float] = None
    ppm_min: Optional[int] = None
    ppm_max: Optional[int] = None
    water_temp_min_f: Optional[float] = None
    water_temp_max_f: Optional[float] = None
    # Spatial layout fields
    land_id: Optional[int] = None
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    # Irrigation system fields
    irrigation_zone_id: Optional[int] = None
    mulch_depth_inches: Optional[float] = None
    is_raised_bed: bool
    soil_texture_override: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
