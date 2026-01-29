"""Dashboard summary schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class SoilHealthStatus(str, Enum):
    """Status indicators for soil parameters"""
    IN_RANGE = "in_range"
    LOW = "low"
    HIGH = "high"
    UNKNOWN = "unknown"


class SoilParameterStatus(BaseModel):
    """Status for individual soil parameter"""
    value: Optional[float] = None
    status: SoilHealthStatus = SoilHealthStatus.UNKNOWN
    unit: str


class SoilTrendPoint(BaseModel):
    """Single data point for soil trend"""
    date: date
    value: float


class SoilRecommendationSummary(BaseModel):
    """Summary of a soil recommendation"""
    severity: str = Field(..., description="info, warning, or critical")
    message: str
    parameter: str = Field(..., description="Which parameter this addresses")


class SoilHealthSummary(BaseModel):
    """Summary of soil health for a garden"""
    garden_id: Optional[int] = Field(None, description="Garden ID, null for all gardens")
    garden_name: Optional[str] = Field(None, description="Garden name")

    # Latest sample data
    last_sample_date: Optional[date] = None
    ph: Optional[SoilParameterStatus] = None
    nitrogen: Optional[SoilParameterStatus] = None
    phosphorus: Optional[SoilParameterStatus] = None
    potassium: Optional[SoilParameterStatus] = None
    organic_matter: Optional[SoilParameterStatus] = None
    moisture: Optional[SoilParameterStatus] = None

    # Trends (last 10 samples)
    ph_trend: List[SoilTrendPoint] = []
    moisture_trend: List[SoilTrendPoint] = []

    # Active recommendations
    recommendations: List[SoilRecommendationSummary] = []

    # Status
    overall_health: str = Field("unknown", description="good, fair, poor, or unknown")
    total_samples: int = 0


class IrrigationAlert(BaseModel):
    """Irrigation alert or warning"""
    type: str = Field(..., description="under_watering, over_watering, or moisture_mismatch")
    severity: str = Field(..., description="info, warning, or critical")
    message: str
    garden_id: Optional[int] = None
    planting_event_id: Optional[int] = None


class IrrigationWeeklySummary(BaseModel):
    """7-day irrigation summary"""
    total_volume_liters: float = Field(0, description="Total water applied in last 7 days")
    event_count: int = Field(0, description="Number of irrigation events")
    average_interval_days: Optional[float] = Field(None, description="Average days between watering")


class IrrigationOverviewSummary(BaseModel):
    """Overview of irrigation activity for a garden"""
    garden_id: Optional[int] = Field(None, description="Garden ID, null for all gardens")
    garden_name: Optional[str] = Field(None, description="Garden name")

    # Recent activity
    last_irrigation_date: Optional[datetime] = None
    last_irrigation_volume: Optional[float] = Field(None, description="Volume in liters")
    last_irrigation_method: Optional[str] = None
    days_since_last_watering: Optional[int] = None

    # Weekly summary
    weekly: IrrigationWeeklySummary

    # Alerts
    alerts: List[IrrigationAlert] = []

    # Status
    total_events: int = 0
