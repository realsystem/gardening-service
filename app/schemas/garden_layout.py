"""Garden layout schemas for spatial placement"""
from pydantic import BaseModel, Field
from typing import Optional, List


class GardenLayoutUpdate(BaseModel):
    """
    Schema for updating garden's spatial layout.

    All spatial fields must be provided together (all-or-nothing).
    To remove garden from layout, set all fields to None.
    """
    land_id: Optional[int] = None
    x: Optional[float] = Field(None, ge=0, description="X-coordinate (top-left origin)")
    y: Optional[float] = Field(None, ge=0, description="Y-coordinate (top-left origin)")
    width: Optional[float] = Field(None, gt=0, description="Garden width (must be > 0)")
    height: Optional[float] = Field(None, gt=0, description="Garden height (must be > 0)")
    snap_to_grid: bool = Field(True, description="Whether to snap coordinates to grid (default: True)")


class GardenLayoutResponse(BaseModel):
    """Response schema for garden layout operations"""
    garden_id: int
    land_id: Optional[int]
    x: Optional[float]
    y: Optional[float]
    width: Optional[float]
    height: Optional[float]
    grid_resolution: float = Field(description="Grid resolution used (units per grid cell)")
    snapped: bool = Field(description="Whether coordinates were snapped to grid")


class LayoutValidationError(BaseModel):
    """Schema for layout validation errors"""
    error_type: str  # "overlap", "out_of_bounds", "incomplete_data"
    message: str
    conflicting_garden_ids: Optional[List[int]] = None
