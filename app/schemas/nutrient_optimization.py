"""Nutrient Optimization API Schemas"""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class ECRecommendation(BaseModel):
    """EC (Electrical Conductivity) range recommendation"""
    min_ms_cm: float = Field(..., description="Minimum EC in mS/cm (millisiemens per centimeter)")
    max_ms_cm: float = Field(..., description="Maximum EC in mS/cm")
    rationale: str = Field(..., description="Explanation of EC recommendation")

    class Config:
        json_schema_extra = {
            "example": {
                "min_ms_cm": 1.5,
                "max_ms_cm": 2.0,
                "rationale": "Optimized for Tomato in vegetative stage"
            }
        }


class PHRecommendation(BaseModel):
    """pH range recommendation"""
    min_ph: float = Field(..., description="Minimum pH (0-14 scale)")
    max_ph: float = Field(..., description="Maximum pH (0-14 scale)")
    rationale: str = Field(..., description="Explanation of pH recommendation")

    class Config:
        json_schema_extra = {
            "example": {
                "min_ph": 5.5,
                "max_ph": 6.5,
                "rationale": "pH range compatible with all 3 crops"
            }
        }


class ReplacementSchedule(BaseModel):
    """Water and nutrient solution replacement schedule"""
    topoff_interval_days: int = Field(..., description="Days between top-off (water replacement)")
    full_replacement_days: int = Field(..., description="Days between full solution changes")
    rationale: str = Field(..., description="Explanation of schedule recommendation")

    class Config:
        json_schema_extra = {
            "example": {
                "topoff_interval_days": 1,
                "full_replacement_days": 10,
                "rationale": "Standard replacement schedule based on system characteristics"
            }
        }


class NutrientWarning(BaseModel):
    """Warning or alert about nutrient management"""
    warning_id: str = Field(..., description="Unique warning identifier")
    severity: str = Field(..., description="Severity level: info, warning, or critical")
    message: str = Field(..., description="Warning message")
    mitigation: str = Field(..., description="Suggested mitigation steps")

    class Config:
        json_schema_extra = {
            "example": {
                "warning_id": "SMALL_RESERVOIR",
                "severity": "warning",
                "message": "Small reservoir (15L) may be unstable",
                "mitigation": "Monitor EC/pH daily. Consider upgrading to larger reservoir (20L+)"
            }
        }


class ActivePlanting(BaseModel):
    """Summary of active planting for context"""
    plant_name: str = Field(..., description="Common name of plant")
    growth_stage: str = Field(..., description="Current growth stage")

    class Config:
        json_schema_extra = {
            "example": {
                "plant_name": "Tomato",
                "growth_stage": "vegetative"
            }
        }


class NutrientOptimizationResponse(BaseModel):
    """Complete nutrient optimization recommendation for a garden"""
    garden_id: int = Field(..., description="Garden ID")
    garden_name: str = Field(..., description="Garden name")
    system_type: str = Field(..., description="System type (nft, dwc, drip, etc.)")

    ec_recommendation: ECRecommendation = Field(..., description="EC range recommendation")
    ph_recommendation: PHRecommendation = Field(..., description="pH range recommendation")
    replacement_schedule: ReplacementSchedule = Field(..., description="Water replacement schedule")

    warnings: List[NutrientWarning] = Field(default_factory=list, description="Active warnings/alerts")
    active_plantings: List[ActivePlanting] = Field(default_factory=list, description="Active plantings providing context")

    generated_at: datetime = Field(..., description="Timestamp when optimization was generated")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "garden_id": 1,
                "garden_name": "Hydroponic Garden",
                "system_type": "dwc",
                "ec_recommendation": {
                    "min_ms_cm": 1.5,
                    "max_ms_cm": 2.0,
                    "rationale": "Optimized for Tomato in vegetative stage"
                },
                "ph_recommendation": {
                    "min_ph": 5.5,
                    "max_ph": 6.5,
                    "rationale": "pH range compatible with all 2 crops"
                },
                "replacement_schedule": {
                    "topoff_interval_days": 1,
                    "full_replacement_days": 10,
                    "rationale": "Standard schedule for 50L reservoir"
                },
                "warnings": [
                    {
                        "warning_id": "HIGH_EC",
                        "severity": "warning",
                        "message": "EC recommendation (2.8 mS/cm) is high",
                        "mitigation": "Watch for leaf tip burn"
                    }
                ],
                "active_plantings": [
                    {"plant_name": "Tomato", "growth_stage": "vegetative"},
                    {"plant_name": "Basil", "growth_stage": "vegetative"}
                ],
                "generated_at": "2026-02-01T12:00:00Z"
            }
        }