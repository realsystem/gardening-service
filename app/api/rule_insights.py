"""
Rule Insights API - Science-Based Gardening Recommendations.

Provides intelligent, explainable alerts and recommendations based on
measurable garden state using the rule engine.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.garden import Garden
from app.models.planting_event import PlantingEvent
from app.models.plant_variety import PlantVariety
from app.models.soil_sample import SoilSample
from app.models.irrigation_event import IrrigationEvent
from app.models.sensor_reading import SensorReading
from app.api.dependencies import get_current_user
from app.rules.engine import RuleContext, get_registry

router = APIRouter(prefix="/rule-insights", tags=["Rule Insights"])


@router.get("/garden/{garden_id}")
def get_garden_insights(
    garden_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get rule-based insights for an entire garden.

    Evaluates all rules against current garden state and returns
    triggered alerts with scientific explanations.

    **Note**: Returns empty results if user has disabled alerts (enable_alerts = false).
    """
    # Verify garden ownership
    garden = db.query(Garden).filter(
        Garden.id == garden_id,
        Garden.user_id == current_user.id
    ).first()

    if not garden:
        raise HTTPException(status_code=404, detail="Garden not found")

    # FEATURE GATE: Respect user's enable_alerts preference
    if not current_user.enable_alerts:
        return {
            "garden_id": garden_id,
            "garden_name": garden.name,
            "evaluation_time": datetime.utcnow().isoformat(),
            "triggered_rules": [],
            "rules_by_severity": {"critical": 0, "warning": 0, "info": 0},
            "rules_by_category": {},
            "message": "Alerts disabled. Enable in Settings to see recommendations."
        }

    # Get garden state
    context = _build_garden_context(db, garden)

    # Evaluate rules
    registry = get_registry()
    engine = registry.create_engine()
    results = engine.evaluate(context)

    # Convert to response format
    triggered_rules = [r.to_dict() for r in results]

    # Count by severity
    critical_count = len([r for r in results if r.severity.value == "critical"])
    warning_count = len([r for r in results if r.severity.value == "warning"])
    info_count = len([r for r in results if r.severity.value == "info"])

    # Count by category
    rules_by_category = {}
    for rule in results:
        category = rule.rule_category.value
        rules_by_category[category] = rules_by_category.get(category, 0) + 1

    return {
        "garden_id": garden_id,
        "garden_name": garden.name,
        "evaluation_time": datetime.utcnow().isoformat(),
        "triggered_rules": triggered_rules,
        "rules_by_severity": {
            "critical": critical_count,
            "warning": warning_count,
            "info": info_count
        },
        "rules_by_category": rules_by_category
    }


@router.get("/planting/{planting_id}")
def get_planting_insights(
    planting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get rule-based insights for a specific planting.

    More specific than garden-level insights, includes plant-specific
    recommendations based on variety requirements.
    """
    # Verify planting ownership
    planting = db.query(PlantingEvent).filter(
        PlantingEvent.id == planting_id,
        PlantingEvent.user_id == current_user.id
    ).first()

    if not planting:
        raise HTTPException(status_code=404, detail="Planting not found")

    # FEATURE GATE: Respect user's enable_alerts preference
    if not current_user.enable_alerts:
        return {
            "planting_id": planting_id,
            "plant_name": "Unknown",
            "plant_variety": None,
            "evaluation_time": datetime.utcnow().isoformat(),
            "triggered_rules": [],
            "rules_by_severity": {"critical": 0, "warning": 0, "info": 0},
            "rules_by_category": {},
            "message": "Alerts disabled. Enable in Settings to see recommendations."
        }

    # Get plant variety
    plant_variety = db.query(PlantVariety).filter(
        PlantVariety.id == planting.plant_variety_id
    ).first()

    # Build context
    context = _build_planting_context(db, planting, plant_variety)

    # Evaluate rules
    registry = get_registry()
    engine = registry.create_engine()
    results = engine.evaluate(context)

    # Convert to response
    triggered_rules = [r.to_dict() for r in results]

    # Count by severity
    critical_count = len([r for r in results if r.severity.value == "critical"])
    warning_count = len([r for r in results if r.severity.value == "warning"])
    info_count = len([r for r in results if r.severity.value == "info"])

    # Count by category
    rules_by_category = {}
    for rule in results:
        category = rule.rule_category.value
        rules_by_category[category] = rules_by_category.get(category, 0) + 1

    return {
        "planting_id": planting_id,
        "plant_name": plant_variety.common_name if plant_variety else "Unknown",
        "plant_variety": plant_variety.variety_name if plant_variety else None,
        "evaluation_time": datetime.utcnow().isoformat(),
        "triggered_rules": triggered_rules,
        "rules_by_severity": {
            "critical": critical_count,
            "warning": warning_count,
            "info": info_count
        },
        "rules_by_category": rules_by_category
    }


def _build_garden_context(db: Session, garden: Garden) -> RuleContext:
    """Build rule context from garden state."""
    context = RuleContext(
        user_id=garden.user_id,
        garden_id=garden.id,
        garden_type=garden.garden_type,
        is_indoor=garden.garden_type == "indoor",
        is_hydroponic=garden.garden_type == "hydroponic"
    )

    # Get most recent soil sample
    soil_sample = db.query(SoilSample).filter(
        SoilSample.garden_id == garden.id
    ).order_by(SoilSample.date_collected.desc()).first()

    if soil_sample:
        context.soil_ph = soil_sample.ph
        context.soil_moisture_percent = soil_sample.moisture_percent
        context.nitrogen_ppm = soil_sample.nitrogen_ppm
        context.phosphorus_ppm = soil_sample.phosphorus_ppm
        context.potassium_ppm = soil_sample.potassium_ppm
        context.organic_matter_percent = soil_sample.organic_matter_percent

    # Get most recent sensor reading (if indoor)
    if garden.garden_type == "indoor":
        sensor = db.query(SensorReading).filter(
            SensorReading.garden_id == garden.id
        ).order_by(SensorReading.reading_date.desc()).first()

        if sensor:
            context.temperature_f = sensor.temperature_f
            context.humidity_percent = sensor.humidity_percent
            context.light_hours_per_day = sensor.light_hours

        context.light_source_type = garden.light_source_type
        context.temperature_min_f = garden.temp_min_f
        context.temperature_max_f = garden.temp_max_f

    # Get irrigation summary (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    irrigation_events = db.query(IrrigationEvent).filter(
        IrrigationEvent.garden_id == garden.id,
        IrrigationEvent.irrigation_date >= seven_days_ago
    ).all()

    if irrigation_events:
        context.total_irrigation_events_7d = len(irrigation_events)
        context.avg_water_volume_liters = sum(
            e.water_volume_liters for e in irrigation_events if e.water_volume_liters
        ) / len(irrigation_events) if irrigation_events else None

        # Most recent irrigation
        most_recent = max(irrigation_events, key=lambda x: x.irrigation_date)
        context.days_since_last_watering = (datetime.utcnow() - most_recent.irrigation_date).days

    return context


def _build_planting_context(db: Session, planting: PlantingEvent, plant_variety: Optional[PlantVariety]) -> RuleContext:
    """Build rule context for a specific planting."""
    # Start with garden context
    garden = db.query(Garden).filter(Garden.id == planting.garden_id).first()
    context = _build_garden_context(db, garden) if garden else RuleContext()

    # Add planting-specific data
    context.planting_event_id = planting.id
    context.plant_variety_id = planting.plant_variety_id

    if plant_variety:
        context.plant_common_name = plant_variety.common_name
        context.plant_scientific_name = plant_variety.scientific_name

    # Calculate days since planting
    if planting.planting_date:
        context.planting_date = planting.planting_date
        context.days_since_planting = (datetime.utcnow().date() - planting.planting_date).days

    # Get planting-specific soil sample
    planting_soil = db.query(SoilSample).filter(
        SoilSample.planting_event_id == planting.id
    ).order_by(SoilSample.date_collected.desc()).first()

    if planting_soil:
        context.soil_ph = planting_soil.ph
        context.soil_moisture_percent = planting_soil.moisture_percent
        context.nitrogen_ppm = planting_soil.nitrogen_ppm
        context.phosphorus_ppm = planting_soil.phosphorus_ppm
        context.potassium_ppm = planting_soil.potassium_ppm

    # Get planting-specific irrigation
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    planting_irrigation = db.query(IrrigationEvent).filter(
        IrrigationEvent.planting_event_id == planting.id,
        IrrigationEvent.irrigation_date >= seven_days_ago
    ).all()

    if planting_irrigation:
        most_recent = max(planting_irrigation, key=lambda x: x.irrigation_date)
        context.days_since_last_watering = (datetime.utcnow() - most_recent.irrigation_date).days

    return context
