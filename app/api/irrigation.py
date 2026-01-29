"""Irrigation tracking endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, date

from app.database import get_db
from app.models.user import User
from app.models.irrigation_event import IrrigationEvent
from app.models.garden import Garden
from app.models.planting_event import PlantingEvent
from app.models.plant_variety import PlantVariety
from app.models.soil_sample import SoilSample
from app.schemas.irrigation import (
    IrrigationEventCreate,
    IrrigationEventResponse,
    IrrigationEventList,
    IrrigationSummary,
)
from app.rules.irrigation_rules import (
    generate_irrigation_recommendation,
    calculate_total_water_volume,
    get_most_common_method,
)
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/irrigation", tags=["Irrigation"])


@router.post("", response_model=IrrigationEventResponse, status_code=201)
def create_irrigation_event(
    event_data: IrrigationEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Log a new irrigation event.

    Either garden_id or planting_event_id must be provided.
    Records water volume, method, duration, and timing for tracking and recommendations.
    """
    # Validate that at least one link is provided
    if not event_data.garden_id and not event_data.planting_event_id:
        raise HTTPException(
            status_code=400,
            detail="Either garden_id or planting_event_id must be provided"
        )

    # Validate garden ownership if garden_id provided
    if event_data.garden_id:
        garden = db.query(Garden).filter(
            Garden.id == event_data.garden_id,
            Garden.user_id == current_user.id
        ).first()
        if not garden:
            raise HTTPException(status_code=404, detail="Garden not found")

    # Validate planting event ownership if planting_event_id provided
    if event_data.planting_event_id:
        planting = db.query(PlantingEvent).filter(
            PlantingEvent.id == event_data.planting_event_id,
            PlantingEvent.user_id == current_user.id
        ).first()
        if not planting:
            raise HTTPException(status_code=404, detail="Planting event not found")

    # Create irrigation event
    irrigation_event = IrrigationEvent(
        user_id=current_user.id,
        garden_id=event_data.garden_id,
        planting_event_id=event_data.planting_event_id,
        irrigation_date=event_data.irrigation_date,
        water_volume_liters=event_data.water_volume_liters,
        irrigation_method=event_data.irrigation_method,
        duration_minutes=event_data.duration_minutes,
        notes=event_data.notes
    )

    db.add(irrigation_event)
    db.commit()
    db.refresh(irrigation_event)

    # Build response
    response = IrrigationEventResponse.from_orm(irrigation_event)

    # Add garden/plant names
    if event_data.garden_id and irrigation_event.garden:
        response.garden_name = irrigation_event.garden.name
    if event_data.planting_event_id and irrigation_event.planting_event:
        planting = irrigation_event.planting_event
        plant_variety = db.query(PlantVariety).filter(
            PlantVariety.id == planting.plant_variety_id
        ).first()
        if plant_variety:
            response.plant_name = plant_variety.plant_name

    return response


@router.get("", response_model=IrrigationEventList)
def list_irrigation_events(
    garden_id: Optional[int] = Query(None, description="Filter by garden ID"),
    planting_event_id: Optional[int] = Query(None, description="Filter by planting event ID"),
    start_date: Optional[datetime] = Query(None, description="Filter events from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter events until this date"),
    days: Optional[int] = Query(None, description="Get events from last N days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List irrigation events for the current user.

    Supports filtering by garden, planting event, and date range.
    Includes summary statistics and irrigation recommendations.
    """
    query = db.query(IrrigationEvent).filter(IrrigationEvent.user_id == current_user.id)

    # Apply filters
    if garden_id:
        query = query.filter(IrrigationEvent.garden_id == garden_id)
    if planting_event_id:
        query = query.filter(IrrigationEvent.planting_event_id == planting_event_id)
    if start_date:
        query = query.filter(IrrigationEvent.irrigation_date >= start_date)
    if end_date:
        query = query.filter(IrrigationEvent.irrigation_date <= end_date)
    if days:
        cutoff = datetime.now() - timedelta(days=days)
        query = query.filter(IrrigationEvent.irrigation_date >= cutoff)

    # Order by date (most recent first)
    events = query.order_by(IrrigationEvent.irrigation_date.desc()).all()

    # Build event responses
    event_responses = []
    for event in events:
        response = IrrigationEventResponse.from_orm(event)

        # Add garden/plant names
        if event.garden:
            response.garden_name = event.garden.name
        if event.planting_event:
            planting = event.planting_event
            plant_variety = db.query(PlantVariety).filter(
                PlantVariety.id == planting.plant_variety_id
            ).first()
            if plant_variety:
                response.plant_name = plant_variety.plant_name

        event_responses.append(response)

    # Calculate summary statistics
    total_volume = calculate_total_water_volume(events)
    most_common_method = get_most_common_method(events)
    last_irrigation = events[0] if events else None
    avg_volume = total_volume / len(events) if events else None

    days_since_last = None
    if last_irrigation:
        days_since_last = (datetime.now() - last_irrigation.irrigation_date).days

    # Generate irrigation recommendations for plantings
    recommendations = []
    if planting_event_id:
        # Specific planting: generate recommendation
        planting = db.query(PlantingEvent).filter(
            PlantingEvent.id == planting_event_id
        ).first()
        if planting:
            plant_variety = db.query(PlantVariety).filter(
                PlantVariety.id == planting.plant_variety_id
            ).first()

            # Get most recent soil sample for moisture data
            soil_sample = db.query(SoilSample).filter(
                SoilSample.planting_event_id == planting_event_id
            ).order_by(SoilSample.date_collected.desc()).first()

            if plant_variety:
                rec = generate_irrigation_recommendation(
                    plant_variety,
                    events,
                    soil_sample,
                    planting.planting_date
                )
                recommendations.append(rec)

    elif garden_id:
        # Garden: generate recommendations for all plantings in garden
        plantings = db.query(PlantingEvent).filter(
            PlantingEvent.garden_id == garden_id,
            PlantingEvent.user_id == current_user.id
        ).all()

        for planting in plantings:
            plant_variety = db.query(PlantVariety).filter(
                PlantVariety.id == planting.plant_variety_id
            ).first()

            # Get irrigation events for this planting
            planting_events = db.query(IrrigationEvent).filter(
                IrrigationEvent.planting_event_id == planting.id
            ).order_by(IrrigationEvent.irrigation_date.desc()).all()

            # Get most recent soil sample
            soil_sample = db.query(SoilSample).filter(
                SoilSample.planting_event_id == planting.id
            ).order_by(SoilSample.date_collected.desc()).first()

            if plant_variety:
                rec = generate_irrigation_recommendation(
                    plant_variety,
                    planting_events,
                    soil_sample,
                    planting.planting_date
                )
                recommendations.append(rec)

    summary = IrrigationSummary(
        total_events=len(events),
        total_volume_liters=total_volume,
        last_irrigation_date=last_irrigation.irrigation_date if last_irrigation else None,
        days_since_last_irrigation=days_since_last,
        average_volume_per_event=avg_volume,
        most_common_method=most_common_method,
        recommendations=recommendations
    )

    return IrrigationEventList(
        events=event_responses,
        summary=summary
    )


@router.get("/summary", response_model=IrrigationSummary)
def get_irrigation_summary(
    garden_id: Optional[int] = Query(None, description="Garden ID"),
    planting_event_id: Optional[int] = Query(None, description="Planting event ID"),
    days: int = Query(30, description="Number of days to include in summary"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get irrigation summary and recommendations.

    Provides aggregate statistics and watering recommendations for a garden or specific planting.
    """
    cutoff = datetime.now() - timedelta(days=days)

    query = db.query(IrrigationEvent).filter(
        IrrigationEvent.user_id == current_user.id,
        IrrigationEvent.irrigation_date >= cutoff
    )

    if garden_id:
        query = query.filter(IrrigationEvent.garden_id == garden_id)
    if planting_event_id:
        query = query.filter(IrrigationEvent.planting_event_id == planting_event_id)

    events = query.order_by(IrrigationEvent.irrigation_date.desc()).all()

    # Calculate statistics
    total_volume = calculate_total_water_volume(events)
    most_common_method = get_most_common_method(events)
    last_irrigation = events[0] if events else None
    avg_volume = total_volume / len(events) if events else None

    days_since_last = None
    if last_irrigation:
        days_since_last = (datetime.now() - last_irrigation.irrigation_date).days

    # Generate recommendations
    recommendations = []
    if planting_event_id:
        planting = db.query(PlantingEvent).filter(
            PlantingEvent.id == planting_event_id
        ).first()
        if planting:
            plant_variety = db.query(PlantVariety).filter(
                PlantVariety.id == planting.plant_variety_id
            ).first()

            soil_sample = db.query(SoilSample).filter(
                SoilSample.planting_event_id == planting_event_id
            ).order_by(SoilSample.date_collected.desc()).first()

            if plant_variety:
                rec = generate_irrigation_recommendation(
                    plant_variety,
                    events,
                    soil_sample,
                    planting.planting_date
                )
                recommendations.append(rec)

    return IrrigationSummary(
        total_events=len(events),
        total_volume_liters=total_volume,
        last_irrigation_date=last_irrigation.irrigation_date if last_irrigation else None,
        days_since_last_irrigation=days_since_last,
        average_volume_per_event=avg_volume,
        most_common_method=most_common_method,
        recommendations=recommendations
    )


@router.delete("/{event_id}", status_code=204)
def delete_irrigation_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an irrigation event.

    Only the owner can delete their own irrigation records.
    """
    event = db.query(IrrigationEvent).filter(
        IrrigationEvent.id == event_id,
        IrrigationEvent.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(status_code=404, detail="Irrigation event not found")

    db.delete(event)
    db.commit()

    return None
