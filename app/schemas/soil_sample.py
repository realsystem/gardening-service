from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class SoilSampleCreate(BaseModel):
    """Schema for creating a new soil sample."""
    garden_id: Optional[int] = Field(None, description="Garden ID (either garden_id or planting_event_id required)")
    planting_event_id: Optional[int] = Field(None, description="Planting event ID")

    ph: float = Field(..., ge=0, le=14, description="Soil pH (0-14)")
    nitrogen_ppm: Optional[float] = Field(None, ge=0, description="Nitrogen in PPM")
    phosphorus_ppm: Optional[float] = Field(None, ge=0, description="Phosphorus in PPM")
    potassium_ppm: Optional[float] = Field(None, ge=0, description="Potassium in PPM")
    organic_matter_percent: Optional[float] = Field(None, ge=0, le=100, description="Organic matter percentage")
    moisture_percent: Optional[float] = Field(None, ge=0, le=100, description="Soil moisture percentage")

    date_collected: date = Field(..., description="Date sample was collected")
    notes: Optional[str] = Field(None, description="Additional observations")


class SoilRecommendation(BaseModel):
    """Scientific recommendation based on soil sample."""
    parameter: str = Field(..., description="Parameter being evaluated (pH, nitrogen, etc.)")
    current_value: float = Field(..., description="Current measured value")
    optimal_range: str = Field(..., description="Optimal range for this parameter")
    status: str = Field(..., description="Status: optimal, low, high, critical")
    recommendation: str = Field(..., description="Specific actionable advice")
    priority: str = Field(..., description="Priority: low, medium, high, critical")


class SoilSampleResponse(BaseModel):
    """Schema for soil sample response."""
    id: int
    user_id: int
    garden_id: Optional[int]
    planting_event_id: Optional[int]

    ph: float
    nitrogen_ppm: Optional[float]
    phosphorus_ppm: Optional[float]
    potassium_ppm: Optional[float]
    organic_matter_percent: Optional[float]
    moisture_percent: Optional[float]

    date_collected: date
    notes: Optional[str]

    # Include garden/planting info
    garden_name: Optional[str] = None
    plant_name: Optional[str] = None

    # Scientific recommendations
    recommendations: List[SoilRecommendation] = []

    class Config:
        from_attributes = True


class SoilSampleList(BaseModel):
    """List of soil samples with summary."""
    samples: List[SoilSampleResponse]
    total: int
    latest_sample: Optional[SoilSampleResponse] = None
