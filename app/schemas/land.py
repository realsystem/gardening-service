"""Land schemas for request/response validation"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class LandCreate(BaseModel):
    """Schema for creating a new land"""
    name: str = Field(..., min_length=1, max_length=100, description="Land name")
    width: float = Field(..., gt=0, description="Land width in abstract units (must be > 0)")
    height: float = Field(..., gt=0, description="Land height in abstract units (must be > 0)")

    @field_validator('width', 'height')
    @classmethod
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError('Width and height must be positive numbers')
        return v


class LandUpdate(BaseModel):
    """Schema for updating an existing land"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    width: Optional[float] = Field(None, gt=0)
    height: Optional[float] = Field(None, gt=0)

    @field_validator('width', 'height')
    @classmethod
    def validate_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Width and height must be positive numbers')
        return v


class LandResponse(BaseModel):
    """Schema for land response"""
    id: int
    user_id: int
    name: str
    width: float
    height: float
    created_at: datetime

    class Config:
        from_attributes = True


class GardenSpatialInfo(BaseModel):
    """Minimal garden info for displaying on canvas"""
    id: int
    name: str
    land_id: Optional[int] = None
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None

    class Config:
        from_attributes = True


class LandWithGardensResponse(LandResponse):
    """Land response with list of gardens placed on it"""
    gardens: List[GardenSpatialInfo] = []

    class Config:
        from_attributes = True
