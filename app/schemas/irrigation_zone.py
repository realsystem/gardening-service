"""Irrigation zone schemas"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Dict, Any


class IrrigationZoneSchedule(BaseModel):
    """Schema for irrigation schedule"""
    frequency_days: Optional[int] = Field(None, ge=1, description="Water every N days")
    duration_minutes: Optional[int] = Field(None, ge=1, description="Duration in minutes")
    time_of_day: Optional[str] = Field(None, description="Preferred time, e.g., '06:00'")

    class Config:
        extra = 'allow'  # Allow additional fields for future expansion


class IrrigationZoneBase(BaseModel):
    """Base schema for irrigation zone"""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the irrigation zone")
    irrigation_source_id: Optional[int] = Field(None, description="Water source for this zone")
    delivery_type: str = Field(..., description="Type: drip, sprinkler, soaker, manual")
    schedule: Optional[Dict[str, Any]] = Field(None, description="Watering schedule as JSON")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes")

    @field_validator('delivery_type')
    @classmethod
    def validate_delivery_type(cls, v: str) -> str:
        """Validate delivery type is one of allowed values"""
        allowed = ['drip', 'sprinkler', 'soaker', 'manual']
        if v not in allowed:
            raise ValueError(f"delivery_type must be one of: {', '.join(allowed)}")
        return v


class IrrigationZoneCreate(IrrigationZoneBase):
    """Schema for creating an irrigation zone"""
    pass


class IrrigationZoneUpdate(BaseModel):
    """Schema for updating an irrigation zone"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    irrigation_source_id: Optional[int] = None
    delivery_type: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('delivery_type')
    @classmethod
    def validate_delivery_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate delivery type if provided"""
        if v is not None:
            allowed = ['drip', 'sprinkler', 'soaker', 'manual']
            if v not in allowed:
                raise ValueError(f"delivery_type must be one of: {', '.join(allowed)}")
        return v


class IrrigationZoneResponse(IrrigationZoneBase):
    """Schema for irrigation zone responses"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    # Include count of gardens in this zone (optional, populated by service)
    garden_count: Optional[int] = None

    class Config:
        from_attributes = True
