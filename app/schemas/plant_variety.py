"""PlantVariety schemas"""
from pydantic import BaseModel
from typing import Optional
from app.models.plant_variety import SunRequirement, WaterRequirement


class PlantVarietyResponse(BaseModel):
    """Schema for plant variety response"""
    id: int
    common_name: str
    scientific_name: Optional[str] = None
    variety_name: Optional[str] = None
    days_to_germination_min: Optional[int] = None
    days_to_germination_max: Optional[int] = None
    days_to_harvest: Optional[int] = None
    spacing_inches: Optional[int] = None
    row_spacing_inches: Optional[int] = None
    sun_requirement: Optional[SunRequirement] = None
    water_requirement: Optional[WaterRequirement] = None
    description: Optional[str] = None
    growing_notes: Optional[str] = None
    photo_url: Optional[str] = None
    tags: Optional[str] = None

    class Config:
        from_attributes = True
