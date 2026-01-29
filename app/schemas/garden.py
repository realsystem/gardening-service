"""Garden schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GardenCreate(BaseModel):
    """Schema for creating a new garden"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class GardenUpdate(BaseModel):
    """Schema for updating a garden"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class GardenResponse(BaseModel):
    """Schema for garden response"""
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
