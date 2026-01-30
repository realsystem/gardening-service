"""Irrigation source schemas"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class IrrigationSourceBase(BaseModel):
    """Base schema for irrigation source"""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the water source")
    source_type: str = Field(..., description="Type: city, well, rain, manual")
    flow_capacity_lpm: Optional[float] = Field(None, ge=0, description="Flow capacity in liters per minute")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes")

    @field_validator('source_type')
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        """Validate source type is one of allowed values"""
        allowed = ['city', 'well', 'rain', 'manual']
        if v not in allowed:
            raise ValueError(f"source_type must be one of: {', '.join(allowed)}")
        return v


class IrrigationSourceCreate(IrrigationSourceBase):
    """Schema for creating an irrigation source"""
    pass


class IrrigationSourceUpdate(BaseModel):
    """Schema for updating an irrigation source"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    source_type: Optional[str] = None
    flow_capacity_lpm: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('source_type')
    @classmethod
    def validate_source_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate source type if provided"""
        if v is not None:
            allowed = ['city', 'well', 'rain', 'manual']
            if v not in allowed:
                raise ValueError(f"source_type must be one of: {', '.join(allowed)}")
        return v


class IrrigationSourceResponse(IrrigationSourceBase):
    """Schema for irrigation source responses"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
