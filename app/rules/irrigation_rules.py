"""
Irrigation science-based recommendation engine.

Provides irrigation scheduling and watering recommendations based on:
- Plant-specific water requirements
- Historical irrigation data
- Soil moisture levels
- Growth stage and climate considerations
"""

from typing import List, Optional, Dict
from datetime import datetime, date
from app.schemas.irrigation import IrrigationRecommendation
from app.models.irrigation_event import IrrigationEvent
from app.models.plant_variety import PlantVariety
from app.models.soil_sample import SoilSample


# Plant-specific water requirements
PLANT_WATER_REQUIREMENTS = {
    # Format: {"frequency_days": X, "volume_per_sqft_liters": Y, "critical_stages": [...]}

    # Vegetables
    "tomato": {
        "frequency_days": 3,
        "volume_per_sqft_liters": 1.5,
        "critical_stages": ["flowering", "fruiting"],
        "notes": "Consistent moisture critical during fruit development"
    },
    "lettuce": {
        "frequency_days": 2,
        "volume_per_sqft_liters": 1.0,
        "critical_stages": ["all"],
        "notes": "Keep soil consistently moist, shallow roots"
    },
    "carrot": {
        "frequency_days": 4,
        "volume_per_sqft_liters": 1.2,
        "critical_stages": ["germination", "root_development"],
        "notes": "Even moisture prevents splitting"
    },
    "pepper": {
        "frequency_days": 3,
        "volume_per_sqft_liters": 1.4,
        "critical_stages": ["flowering", "fruiting"],
        "notes": "Reduce water slightly during fruit ripening for flavor"
    },
    "cucumber": {
        "frequency_days": 2,
        "volume_per_sqft_liters": 1.6,
        "critical_stages": ["flowering", "fruiting"],
        "notes": "High water needs, especially during fruiting"
    },
    "broccoli": {
        "frequency_days": 3,
        "volume_per_sqft_liters": 1.3,
        "critical_stages": ["head_formation"],
        "notes": "Consistent moisture for head development"
    },
    "spinach": {
        "frequency_days": 3,
        "volume_per_sqft_liters": 1.1,
        "critical_stages": ["all"],
        "notes": "Cool-season crop, avoid overwatering in heat"
    },
    "basil": {
        "frequency_days": 2,
        "volume_per_sqft_liters": 1.0,
        "critical_stages": ["all"],
        "notes": "Keep moist but not waterlogged"
    },

    # Default for unknown plants
    "default": {
        "frequency_days": 3,
        "volume_per_sqft_liters": 1.3,
        "critical_stages": ["flowering", "fruiting"],
        "notes": "Standard watering for most vegetables"
    }
}


def get_plant_water_requirements(plant_name: Optional[str]) -> Dict:
    """Get water requirements for a specific plant."""
    if not plant_name:
        return PLANT_WATER_REQUIREMENTS["default"]

    # Normalize plant name (lowercase, first word only)
    plant_key = plant_name.lower().split()[0]
    return PLANT_WATER_REQUIREMENTS.get(plant_key, PLANT_WATER_REQUIREMENTS["default"])


def generate_irrigation_recommendation(
    plant_variety: PlantVariety,
    irrigation_history: List[IrrigationEvent],
    soil_sample: Optional[SoilSample] = None,
    planting_date: Optional[date] = None
) -> IrrigationRecommendation:
    """
    Generate irrigation recommendation for a specific plant.

    Args:
        plant_variety: Plant variety being grown
        irrigation_history: List of past irrigation events (sorted by date, most recent first)
        soil_sample: Most recent soil sample (optional, for moisture data)
        planting_date: Date plant was planted (optional, for growth stage)

    Returns:
        IrrigationRecommendation with specific watering advice
    """
    plant_name = plant_variety.common_name
    requirements = get_plant_water_requirements(plant_name)

    recommended_frequency = requirements["frequency_days"]
    recommended_volume = requirements["volume_per_sqft_liters"]

    # Calculate days since last watering
    days_since_last = None
    if irrigation_history:
        last_irrigation = irrigation_history[0]
        days_since_last = (datetime.now().date() - last_irrigation.irrigation_date.date()).days

    # Determine status and recommendation
    if days_since_last is None:
        # No irrigation history
        return IrrigationRecommendation(
            plant_name=plant_name,
            days_since_last_watering=None,
            recommended_frequency_days=recommended_frequency,
            recommended_volume_liters=recommended_volume,
            status="no_data",
            recommendation=f"No irrigation history. Water {plant_name} every {recommended_frequency} days with approximately {recommended_volume:.1f} liters per square foot. {requirements['notes']}",
            priority="medium"
        )

    # Check soil moisture if available
    soil_moisture_override = None
    if soil_sample and soil_sample.moisture_percent is not None:
        if soil_sample.moisture_percent > 60:
            soil_moisture_override = "too_wet"
        elif soil_sample.moisture_percent < 20:
            soil_moisture_override = "too_dry"

    # Determine watering status
    if soil_moisture_override == "too_wet":
        return IrrigationRecommendation(
            plant_name=plant_name,
            days_since_last_watering=days_since_last,
            recommended_frequency_days=recommended_frequency,
            recommended_volume_liters=recommended_volume,
            status="overwatered",
            recommendation=f"Soil moisture is high ({soil_sample.moisture_percent:.0f}%). Skip watering. Allow soil to dry to 40-50% moisture before next watering. Risk of root rot if overwatered.",
            priority="high"
        )
    elif soil_moisture_override == "too_dry" or days_since_last > recommended_frequency + 1:
        # Overdue for watering
        days_overdue = days_since_last - recommended_frequency
        urgency = "critical" if days_overdue > 2 else "high"

        return IrrigationRecommendation(
            plant_name=plant_name,
            days_since_last_watering=days_since_last,
            recommended_frequency_days=recommended_frequency,
            recommended_volume_liters=recommended_volume,
            status="overdue",
            recommendation=f"Water immediately! Last watered {days_since_last} days ago (recommended: every {recommended_frequency} days). Apply {recommended_volume:.1f} liters per sq ft. Water deeply in early morning. {requirements['notes']}",
            priority=urgency
        )
    elif days_since_last < recommended_frequency - 1:
        # Potentially overwatering
        return IrrigationRecommendation(
            plant_name=plant_name,
            days_since_last_watering=days_since_last,
            recommended_frequency_days=recommended_frequency,
            recommended_volume_liters=recommended_volume,
            status="overwatered",
            recommendation=f"Watering too frequently. Last watered {days_since_last} days ago. Wait {recommended_frequency - days_since_last} more days before next watering. Overwatering can cause root rot and nutrient leaching.",
            priority="medium"
        )
    else:
        # On schedule
        next_watering_days = recommended_frequency - days_since_last
        return IrrigationRecommendation(
            plant_name=plant_name,
            days_since_last_watering=days_since_last,
            recommended_frequency_days=recommended_frequency,
            recommended_volume_liters=recommended_volume,
            status="on_schedule",
            recommendation=f"Watering schedule is good. Last watered {days_since_last} days ago. Next watering in {next_watering_days} days. Apply {recommended_volume:.1f} liters per sq ft when watering.",
            priority="low"
        )


def calculate_total_water_volume(irrigation_events: List[IrrigationEvent]) -> float:
    """Calculate total water volume from irrigation events."""
    total = 0.0
    for event in irrigation_events:
        if event.water_volume_liters:
            total += event.water_volume_liters
    return total


def get_most_common_method(irrigation_events: List[IrrigationEvent]) -> Optional[str]:
    """Determine most frequently used irrigation method."""
    if not irrigation_events:
        return None

    method_counts = {}
    for event in irrigation_events:
        method = event.irrigation_method.value
        method_counts[method] = method_counts.get(method, 0) + 1

    return max(method_counts, key=method_counts.get) if method_counts else None


def should_generate_irrigation_task(
    plant_variety: PlantVariety,
    last_irrigation: Optional[IrrigationEvent],
    soil_moisture: Optional[float] = None
) -> bool:
    """
    Determine if an irrigation task should be generated.

    Returns:
        True if watering is needed, False otherwise
    """
    requirements = get_plant_water_requirements(plant_variety.common_name)
    recommended_frequency = requirements["frequency_days"]

    # Check soil moisture first
    if soil_moisture is not None:
        if soil_moisture > 60:
            return False  # Too wet, don't water
        elif soil_moisture < 20:
            return True  # Too dry, water immediately

    # Check time since last irrigation
    if last_irrigation is None:
        return True  # No history, create task

    days_since_last = (datetime.now().date() - last_irrigation.irrigation_date.date()).days

    # Create task if overdue (1 day grace period)
    return days_since_last >= recommended_frequency


def get_seasonal_adjustment_factor(current_month: int) -> float:
    """
    Get seasonal water adjustment factor (1.0 = baseline).

    Summer months require more water, winter months require less.
    """
    # Northern hemisphere seasonality
    if current_month in [6, 7, 8]:  # Summer
        return 1.3
    elif current_month in [12, 1, 2]:  # Winter
        return 0.7
    elif current_month in [3, 4, 5, 9, 10, 11]:  # Spring/Fall
        return 1.0
    return 1.0
