"""SeedBatch schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.plant_variety import PlantVarietyResponse


class SeedBatchCreate(BaseModel):
    """Schema for creating a new seed batch"""
    plant_variety_id: int
    source: Optional[str] = None
    harvest_year: Optional[int] = Field(None, ge=1900, le=2100)
    quantity: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class SeedBatchUpdate(BaseModel):
    """Schema for updating a seed batch"""
    source: Optional[str] = None
    harvest_year: Optional[int] = Field(None, ge=1900, le=2100)
    quantity: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class SeedBatchResponse(BaseModel):
    """Schema for seed batch response"""
    id: int
    user_id: int
    plant_variety_id: int
    plant_variety: Optional[PlantVarietyResponse] = None
    source: Optional[str] = None
    harvest_year: Optional[int] = None
    quantity: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
