from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.irrigation_event import IrrigationMethod


class IrrigationEventCreate(BaseModel):
    """Schema for creating a new irrigation event."""
    model_config = ConfigDict(use_enum_values=True)

    garden_id: Optional[int] = Field(None, description="Garden ID (either garden_id or planting_event_id required)")
    planting_event_id: Optional[int] = Field(None, description="Planting event ID")

    irrigation_date: datetime = Field(..., description="Date and time of irrigation")
    water_volume_liters: Optional[float] = Field(None, ge=0, description="Water volume in liters")
    irrigation_method: IrrigationMethod = Field(..., description="Irrigation method used")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Duration in minutes")

    notes: Optional[str] = Field(None, description="Additional observations")


class IrrigationEventResponse(BaseModel):
    """Schema for irrigation event response."""
    id: int
    user_id: int
    garden_id: Optional[int]
    planting_event_id: Optional[int]

    irrigation_date: datetime
    water_volume_liters: Optional[float]
    irrigation_method: IrrigationMethod
    duration_minutes: Optional[int]

    notes: Optional[str]

    # Include garden/planting info
    garden_name: Optional[str] = None
    plant_name: Optional[str] = None

    class Config:
        from_attributes = True


class IrrigationRecommendation(BaseModel):
    """Irrigation recommendation based on plant needs and history."""
    plant_name: str = Field(..., description="Plant name")
    days_since_last_watering: Optional[int] = Field(None, description="Days since last watered")
    recommended_frequency_days: int = Field(..., description="Recommended watering frequency")
    recommended_volume_liters: Optional[float] = Field(None, description="Recommended volume per watering")
    status: str = Field(..., description="Status: on_schedule, overdue, overwatered")
    recommendation: str = Field(..., description="Specific actionable advice")
    priority: str = Field(..., description="Priority: low, medium, high")


class IrrigationSummary(BaseModel):
    """Summary of irrigation for a garden or planting."""
    total_events: int = Field(..., description="Total irrigation events")
    total_volume_liters: float = Field(..., description="Total water applied in liters")
    last_irrigation_date: Optional[datetime] = Field(None, description="Most recent irrigation")
    days_since_last_irrigation: Optional[int] = Field(None, description="Days since last watered")
    average_volume_per_event: Optional[float] = Field(None, description="Average volume per event")
    most_common_method: Optional[IrrigationMethod] = Field(None, description="Most frequently used method")

    # Recommendations
    recommendations: List[IrrigationRecommendation] = []


class IrrigationEventList(BaseModel):
    """List of irrigation events with summary."""
    events: List[IrrigationEventResponse]
    summary: IrrigationSummary
