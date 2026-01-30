"""Watering event schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class WateringEventBase(BaseModel):
    """Base schema for watering event"""
    irrigation_zone_id: int = Field(..., description="Zone that was watered")
    watered_at: datetime = Field(..., description="When the watering occurred")
    duration_minutes: float = Field(..., gt=0, description="How long water ran (minutes)")
    estimated_volume_liters: Optional[float] = Field(None, ge=0, description="Estimated volume (liters)")
    is_manual: bool = Field(False, description="Was this manual watering?")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")


class WateringEventCreate(WateringEventBase):
    """Schema for creating a watering event"""
    pass


class WateringEventUpdate(BaseModel):
    """Schema for updating a watering event"""
    watered_at: Optional[datetime] = None
    duration_minutes: Optional[float] = Field(None, gt=0)
    estimated_volume_liters: Optional[float] = Field(None, ge=0)
    is_manual: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)


class WateringEventResponse(WateringEventBase):
    """Schema for watering event responses"""
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
