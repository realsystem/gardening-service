"""Structure schemas for API"""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class StructureCreate(BaseModel):
    """Schema for creating a new structure"""
    land_id: int = Field(..., description="ID of the land plot where structure is located")
    name: str = Field(..., min_length=1, max_length=100, description="User-friendly structure name")
    x: float = Field(..., description="X-coordinate on land (top-left corner)")
    y: float = Field(..., description="Y-coordinate on land (top-left corner)")
    width: float = Field(..., gt=0, description="Structure width in land units")
    depth: float = Field(..., gt=0, description="Structure depth/length in land units")
    height: float = Field(..., gt=0, description="Structure height for shadow calculations")


class StructureUpdate(BaseModel):
    """Schema for updating a structure"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = Field(None, gt=0)
    depth: Optional[float] = Field(None, gt=0)
    height: Optional[float] = Field(None, gt=0)


class StructureResponse(BaseModel):
    """Schema for structure response"""
    id: int
    user_id: int
    land_id: int
    name: str
    x: float
    y: float
    width: float
    depth: float
    height: float
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class StructureResponseWithShadowExtent(StructureResponse):
    """
    Extended structure response with computed seasonal shadow data.

    These fields are computed from sun-path model based on:
    - Structure height
    - Seasonal sun angles
    - Latitude

    Not stored in database - calculated at request time.
    """
    seasonal_shadows: Optional[Dict[str, dict]] = Field(
        None,
        description="Shadow projections for each season (winter, equinox, summer)"
    )
    max_shadow_length: Optional[float] = Field(
        None,
        description="Maximum shadow length across all seasons (in land units)"
    )
