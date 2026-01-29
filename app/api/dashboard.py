"""Dashboard summary endpoints for soil and irrigation."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timedelta, date

from app.database import get_db
from app.models.user import User
from app.models.soil_sample import SoilSample
from app.models.irrigation_event import IrrigationEvent
from app.models.garden import Garden
from app.schemas.dashboard import (
    SoilHealthSummary,
    SoilParameterStatus,
    SoilHealthStatus,
    SoilTrendPoint,
    SoilRecommendationSummary,
    IrrigationOverviewSummary,
    IrrigationWeeklySummary,
    IrrigationAlert,
)
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def evaluate_ph_status(ph: Optional[float]) -> SoilHealthStatus:
    """Evaluate pH status (optimal range 6.0-7.0 for most plants)"""
    if ph is None:
        return SoilHealthStatus.UNKNOWN
    if 6.0 <= ph <= 7.0:
        return SoilHealthStatus.IN_RANGE
    elif ph < 5.5 or ph > 7.5:
        return SoilHealthStatus.HIGH if ph > 7.5 else SoilHealthStatus.LOW
    else:
        return SoilHealthStatus.LOW if ph < 6.0 else SoilHealthStatus.HIGH


def evaluate_npk_status(value: Optional[float], optimal_min: float, optimal_max: float) -> SoilHealthStatus:
    """Evaluate NPK status based on optimal ranges"""
    if value is None:
        return SoilHealthStatus.UNKNOWN
    if optimal_min <= value <= optimal_max:
        return SoilHealthStatus.IN_RANGE
    return SoilHealthStatus.LOW if value < optimal_min else SoilHealthStatus.HIGH


def evaluate_moisture_status(moisture: Optional[float]) -> SoilHealthStatus:
    """Evaluate moisture status (optimal range 40-60%)"""
    if moisture is None:
        return SoilHealthStatus.UNKNOWN
    if 40 <= moisture <= 60:
        return SoilHealthStatus.IN_RANGE
    return SoilHealthStatus.LOW if moisture < 40 else SoilHealthStatus.HIGH


def evaluate_organic_matter_status(om: Optional[float]) -> SoilHealthStatus:
    """Evaluate organic matter status (optimal >3%)"""
    if om is None:
        return SoilHealthStatus.UNKNOWN
    if om >= 3.0:
        return SoilHealthStatus.IN_RANGE
    elif om >= 2.0:
        return SoilHealthStatus.LOW
    else:
        return SoilHealthStatus.LOW


def determine_overall_health(ph_status: SoilHealthStatus,
                            n_status: SoilHealthStatus,
                            p_status: SoilHealthStatus,
                            k_status: SoilHealthStatus) -> str:
    """Determine overall soil health based on key parameters"""
    statuses = [ph_status, n_status, p_status, k_status]

    # Count unknowns and in-range
    unknown_count = sum(1 for s in statuses if s == SoilHealthStatus.UNKNOWN)
    in_range_count = sum(1 for s in statuses if s == SoilHealthStatus.IN_RANGE)

    if unknown_count == len(statuses):
        return "unknown"

    # If any critical parameter is out of range
    if ph_status in [SoilHealthStatus.LOW, SoilHealthStatus.HIGH]:
        return "poor"

    # Calculate percentage in range (excluding unknowns)
    known_count = len(statuses) - unknown_count
    if known_count > 0:
        in_range_pct = in_range_count / known_count
        if in_range_pct >= 0.75:
            return "good"
        elif in_range_pct >= 0.5:
            return "fair"
        else:
            return "poor"

    return "unknown"


@router.get("/soil-summary", response_model=SoilHealthSummary)
def get_soil_summary(
    garden_id: Optional[int] = Query(None, description="Filter by garden ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get soil health summary for a specific garden or all gardens.

    Returns latest soil sample data with status indicators,
    trends over time, and active recommendations.
    """
    # Build query
    query = db.query(SoilSample).filter(SoilSample.user_id == current_user.id)

    garden_name = None
    if garden_id is not None:
        # Verify garden ownership
        garden = db.query(Garden).filter(
            Garden.id == garden_id,
            Garden.user_id == current_user.id
        ).first()
        if not garden:
            raise HTTPException(status_code=404, detail="Garden not found")

        query = query.filter(SoilSample.garden_id == garden_id)
        garden_name = garden.name

    # Get total sample count
    total_samples = query.count()

    if total_samples == 0:
        # Return empty state
        return SoilHealthSummary(
            garden_id=garden_id,
            garden_name=garden_name,
            overall_health="unknown",
            total_samples=0
        )

    # Get latest sample
    latest_sample = query.order_by(desc(SoilSample.date_collected)).first()

    # Evaluate statuses
    ph_status = evaluate_ph_status(latest_sample.ph)
    n_status = evaluate_npk_status(latest_sample.nitrogen_ppm, 20, 50)  # Typical range
    p_status = evaluate_npk_status(latest_sample.phosphorus_ppm, 15, 40)
    k_status = evaluate_npk_status(latest_sample.potassium_ppm, 80, 200)
    om_status = evaluate_organic_matter_status(latest_sample.organic_matter_percent)
    moisture_status = evaluate_moisture_status(latest_sample.moisture_percent)

    # Build parameter status objects
    ph_param = SoilParameterStatus(
        value=latest_sample.ph,
        status=ph_status,
        unit="pH"
    ) if latest_sample.ph is not None else None

    n_param = SoilParameterStatus(
        value=latest_sample.nitrogen_ppm,
        status=n_status,
        unit="ppm"
    ) if latest_sample.nitrogen_ppm is not None else None

    p_param = SoilParameterStatus(
        value=latest_sample.phosphorus_ppm,
        status=p_status,
        unit="ppm"
    ) if latest_sample.phosphorus_ppm is not None else None

    k_param = SoilParameterStatus(
        value=latest_sample.potassium_ppm,
        status=k_status,
        unit="ppm"
    ) if latest_sample.potassium_ppm is not None else None

    om_param = SoilParameterStatus(
        value=latest_sample.organic_matter_percent,
        status=om_status,
        unit="%"
    ) if latest_sample.organic_matter_percent is not None else None

    moisture_param = SoilParameterStatus(
        value=latest_sample.moisture_percent,
        status=moisture_status,
        unit="%"
    ) if latest_sample.moisture_percent is not None else None

    # Get trends (last 10 samples with pH and moisture data)
    trend_samples = query.order_by(desc(SoilSample.date_collected)).limit(10).all()

    ph_trend = [
        SoilTrendPoint(date=sample.date_collected, value=sample.ph)
        for sample in reversed(trend_samples)
        if sample.ph is not None
    ]

    moisture_trend = [
        SoilTrendPoint(date=sample.date_collected, value=sample.moisture_percent)
        for sample in reversed(trend_samples)
        if sample.moisture_percent is not None
    ]

    # Generate recommendations based on status
    recommendations = []

    if ph_status == SoilHealthStatus.LOW:
        recommendations.append(SoilRecommendationSummary(
            severity="warning",
            message=f"pH is acidic ({latest_sample.ph:.1f}). Add lime to raise pH to 6.0-7.0 range.",
            parameter="pH"
        ))
    elif ph_status == SoilHealthStatus.HIGH:
        recommendations.append(SoilRecommendationSummary(
            severity="warning",
            message=f"pH is alkaline ({latest_sample.ph:.1f}). Add sulfur or organic matter to lower pH.",
            parameter="pH"
        ))

    if n_status == SoilHealthStatus.LOW and latest_sample.nitrogen_ppm is not None:
        recommendations.append(SoilRecommendationSummary(
            severity="warning",
            message=f"Nitrogen is low ({latest_sample.nitrogen_ppm:.1f} ppm). Apply nitrogen-rich fertilizer or compost.",
            parameter="nitrogen"
        ))

    if p_status == SoilHealthStatus.LOW and latest_sample.phosphorus_ppm is not None:
        recommendations.append(SoilRecommendationSummary(
            severity="info",
            message=f"Phosphorus is low ({latest_sample.phosphorus_ppm:.1f} ppm). Add bone meal or rock phosphate.",
            parameter="phosphorus"
        ))

    if k_status == SoilHealthStatus.LOW and latest_sample.potassium_ppm is not None:
        recommendations.append(SoilRecommendationSummary(
            severity="info",
            message=f"Potassium is low ({latest_sample.potassium_ppm:.1f} ppm). Apply potash or wood ash.",
            parameter="potassium"
        ))

    if om_status == SoilHealthStatus.LOW and latest_sample.organic_matter_percent is not None:
        recommendations.append(SoilRecommendationSummary(
            severity="info",
            message=f"Organic matter is low ({latest_sample.organic_matter_percent:.1f}%). Add compost regularly.",
            parameter="organic_matter"
        ))

    if moisture_status == SoilHealthStatus.LOW and latest_sample.moisture_percent is not None:
        recommendations.append(SoilRecommendationSummary(
            severity="warning",
            message=f"Soil is dry ({latest_sample.moisture_percent:.1f}%). Increase watering frequency.",
            parameter="moisture"
        ))
    elif moisture_status == SoilHealthStatus.HIGH and latest_sample.moisture_percent is not None:
        recommendations.append(SoilRecommendationSummary(
            severity="critical",
            message=f"Soil is waterlogged ({latest_sample.moisture_percent:.1f}%). Improve drainage or reduce watering.",
            parameter="moisture"
        ))

    # Determine overall health
    overall_health = determine_overall_health(ph_status, n_status, p_status, k_status)

    return SoilHealthSummary(
        garden_id=garden_id,
        garden_name=garden_name,
        last_sample_date=latest_sample.date_collected,
        ph=ph_param,
        nitrogen=n_param,
        phosphorus=p_param,
        potassium=k_param,
        organic_matter=om_param,
        moisture=moisture_param,
        ph_trend=ph_trend,
        moisture_trend=moisture_trend,
        recommendations=recommendations,
        overall_health=overall_health,
        total_samples=total_samples
    )


@router.get("/irrigation-summary", response_model=IrrigationOverviewSummary)
def get_irrigation_summary(
    garden_id: Optional[int] = Query(None, description="Filter by garden ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get irrigation overview for a specific garden or all gardens.

    Returns recent activity, 7-day summary, and alerts for
    under/over-watering conditions.
    """
    # Build query
    query = db.query(IrrigationEvent).filter(IrrigationEvent.user_id == current_user.id)

    garden_name = None
    if garden_id is not None:
        # Verify garden ownership
        garden = db.query(Garden).filter(
            Garden.id == garden_id,
            Garden.user_id == current_user.id
        ).first()
        if not garden:
            raise HTTPException(status_code=404, detail="Garden not found")

        query = query.filter(IrrigationEvent.garden_id == garden_id)
        garden_name = garden.name

    # Get total event count
    total_events = query.count()

    if total_events == 0:
        # Return empty state
        return IrrigationOverviewSummary(
            garden_id=garden_id,
            garden_name=garden_name,
            weekly=IrrigationWeeklySummary(),
            total_events=0
        )

    # Get latest irrigation event
    latest_event = query.order_by(desc(IrrigationEvent.irrigation_date)).first()

    days_since_last = None
    if latest_event:
        days_since_last = (datetime.utcnow() - latest_event.irrigation_date).days

    # Get 7-day summary
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_events = query.filter(IrrigationEvent.irrigation_date >= seven_days_ago).all()

    weekly_volume = sum(
        event.water_volume_liters for event in recent_events
        if event.water_volume_liters is not None
    )
    weekly_count = len(recent_events)

    # Calculate average interval
    average_interval = None
    if weekly_count > 1:
        # Sort events by date
        sorted_events = sorted(recent_events, key=lambda e: e.irrigation_date)
        intervals = []
        for i in range(1, len(sorted_events)):
            delta = (sorted_events[i].irrigation_date - sorted_events[i-1].irrigation_date).total_seconds()
            intervals.append(delta / 86400)  # Convert to days
        if intervals:
            average_interval = sum(intervals) / len(intervals)

    weekly_summary = IrrigationWeeklySummary(
        total_volume_liters=weekly_volume,
        event_count=weekly_count,
        average_interval_days=average_interval
    )

    # Generate alerts
    alerts = []

    # Under-watering check (no water in 7+ days)
    if days_since_last is not None and days_since_last >= 7:
        alerts.append(IrrigationAlert(
            type="under_watering",
            severity="warning",
            message=f"No irrigation recorded in {days_since_last} days. Consider watering soon.",
            garden_id=garden_id
        ))

    # Over-watering check (more than 2 events per day on average)
    if weekly_count > 0 and average_interval is not None and average_interval < 0.5:
        alerts.append(IrrigationAlert(
            type="over_watering",
            severity="warning",
            message=f"High irrigation frequency (avg {average_interval:.1f} days between watering). Check for overwatering.",
            garden_id=garden_id
        ))

    # Check moisture vs irrigation (if we have recent soil data)
    if garden_id is not None:
        latest_soil = db.query(SoilSample).filter(
            SoilSample.user_id == current_user.id,
            SoilSample.garden_id == garden_id
        ).order_by(desc(SoilSample.date_collected)).first()

        if latest_soil and latest_soil.moisture_percent is not None:
            # If moisture is low but we watered recently
            if latest_soil.moisture_percent < 30 and days_since_last is not None and days_since_last <= 2:
                alerts.append(IrrigationAlert(
                    type="moisture_mismatch",
                    severity="info",
                    message=f"Soil moisture is low ({latest_soil.moisture_percent:.1f}%) despite recent watering. Check irrigation effectiveness or drainage.",
                    garden_id=garden_id
                ))
            # If moisture is high but we haven't watered in a while
            elif latest_soil.moisture_percent > 70 and days_since_last is not None and days_since_last > 5:
                alerts.append(IrrigationAlert(
                    type="moisture_mismatch",
                    severity="info",
                    message=f"Soil moisture is high ({latest_soil.moisture_percent:.1f}%) without recent irrigation. Check for water retention issues.",
                    garden_id=garden_id
                ))

    return IrrigationOverviewSummary(
        garden_id=garden_id,
        garden_name=garden_name,
        last_irrigation_date=latest_event.irrigation_date if latest_event else None,
        last_irrigation_volume=latest_event.water_volume_liters if latest_event else None,
        last_irrigation_method=latest_event.irrigation_method.value if latest_event else None,
        days_since_last_watering=days_since_last,
        weekly=weekly_summary,
        alerts=alerts,
        total_events=total_events
    )
