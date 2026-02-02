"""Tree schemas for API"""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class TreeCreate(BaseModel):
    """
    Schema for creating a new tree.

    **Simplified in Phase 4**: Users only specify species and position.
    Tree dimensions (canopy_radius, height) are auto-calculated from species defaults.
    """
    land_id: int = Field(..., description="ID of the land plot where tree is located")
    name: str = Field(..., min_length=1, max_length=100, description="User-friendly tree name (e.g., 'Oak in backyard')")
    species_id: int = Field(..., description="ID of plant variety (tree species) - REQUIRED for auto-dimension calculation")
    x: float = Field(..., description="X-coordinate on land (trunk center)")
    y: float = Field(..., description="Y-coordinate on land (trunk center)")
    # Dimensions now optional - auto-calculated from species if not provided
    canopy_radius: Optional[float] = Field(None, gt=0, description="Canopy radius override (uses species default if omitted)")
    height: Optional[float] = Field(None, gt=0, description="Tree height override (uses species default if omitted)")


class TreeUpdate(BaseModel):
    """Schema for updating a tree"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    species_id: Optional[int] = None
    x: Optional[float] = None
    y: Optional[float] = None
    canopy_radius: Optional[float] = Field(None, gt=0)
    height: Optional[float] = Field(None, gt=0)


class TreeResponse(BaseModel):
    """Schema for tree response"""
    id: int
    user_id: int
    land_id: int
    name: str
    species_id: Optional[int]
    x: float
    y: float
    canopy_radius: float
    height: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TreeWithSpecies(TreeResponse):
    """Tree response with species details"""
    species_common_name: Optional[str] = None
    species_scientific_name: Optional[str] = None

    class Config:
        from_attributes = True


class ShadingContribution(BaseModel):
    """Details of a tree's shading contribution to a garden"""
    tree_id: int
    tree_name: str
    shade_contribution: float = Field(..., description="Shade contribution factor (0.0 to 1.0)")
    intersection_area: float = Field(..., description="Area of overlap between tree canopy and garden")
    average_intensity: float = Field(..., description="Average shade intensity in overlap area")


class GardenShadingInfo(BaseModel):
    """Shading information for a garden"""
    garden_id: int
    sun_exposure_score: float = Field(..., ge=0.0, le=1.0, description="Effective sun exposure (0=full shade, 1=full sun)")
    sun_exposure_category: str = Field(..., description="Categorical sun level: full_sun, partial_sun, or shade")
    total_shade_factor: float = Field(..., ge=0.0, le=1.0, description="Overall shade reduction factor")
    contributing_trees: list[ShadingContribution] = Field(default_factory=list, description="Trees casting shade on this garden")
    baseline_sun_exposure: float = Field(1.0, description="Baseline sun exposure without trees")


class TreeResponseWithShadowExtent(TreeResponse):
    """
    Extended tree response with computed seasonal shadow data.

    These fields are computed from sun-path model based on:
    - Tree height
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
