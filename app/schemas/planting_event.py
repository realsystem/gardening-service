"""PlantingEvent schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.models.planting_event import PlantingMethod, PlantHealth
from app.schemas.plant_variety import PlantVarietyResponse


class PlantingEventCreate(BaseModel):
    """Schema for creating a new planting event"""
    garden_id: int
    plant_variety_id: int
    germination_event_id: Optional[int] = None
    planting_date: date
    planting_method: PlantingMethod
    plant_count: Optional[int] = Field(None, ge=0)
    location_in_garden: Optional[str] = None
    health_status: Optional[PlantHealth] = None
    plant_notes: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    notes: Optional[str] = None


class PlantingEventUpdate(BaseModel):
    """Schema for updating a planting event"""
    plant_count: Optional[int] = Field(None, ge=0)
    location_in_garden: Optional[str] = None
    health_status: Optional[PlantHealth] = None
    plant_notes: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    notes: Optional[str] = None


class PlantingEventResponse(BaseModel):
    """Schema for planting event response"""
    id: int
    user_id: int
    garden_id: int
    plant_variety_id: int
    plant_variety: Optional[PlantVarietyResponse] = None
    germination_event_id: Optional[int] = None
    planting_date: date
    planting_method: PlantingMethod
    plant_count: Optional[int] = None
    location_in_garden: Optional[str] = None
    health_status: Optional[PlantHealth] = None
    plant_notes: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
