"""Irrigation system API endpoints - zone-based irrigation management"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.repositories.irrigation_source_repository import IrrigationSourceRepository
from app.repositories.irrigation_zone_repository import IrrigationZoneRepository
from app.repositories.watering_event_repository import WateringEventRepository
from app.services.irrigation_service import IrrigationService
from app.schemas.irrigation_source import (
    IrrigationSourceCreate,
    IrrigationSourceUpdate,
    IrrigationSourceResponse
)
from app.schemas.irrigation_zone import (
    IrrigationZoneCreate,
    IrrigationZoneUpdate,
    IrrigationZoneResponse
)
from app.schemas.watering_event import (
    WateringEventCreate,
    WateringEventUpdate,
    WateringEventResponse
)

router = APIRouter(prefix="/irrigation-system", tags=["irrigation-system"])


# ============================================================================
# IRRIGATION SOURCES
# ============================================================================

@router.post("/sources", response_model=IrrigationSourceResponse, status_code=status.HTTP_201_CREATED)
def create_irrigation_source(
    source_data: IrrigationSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new irrigation source"""
    source = IrrigationSourceRepository.create(db, current_user.id, source_data)
    return source


@router.get("/sources", response_model=List[IrrigationSourceResponse])
def get_irrigation_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all irrigation sources for the current user"""
    sources = IrrigationSourceRepository.get_all(db, current_user.id)
    return sources


@router.get("/sources/{source_id}", response_model=IrrigationSourceResponse)
def get_irrigation_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific irrigation source by ID"""
    source = IrrigationSourceRepository.get_by_id(db, source_id, current_user.id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Irrigation source not found"
        )
    return source


@router.patch("/sources/{source_id}", response_model=IrrigationSourceResponse)
def update_irrigation_source(
    source_id: int,
    source_data: IrrigationSourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an irrigation source"""
    source = IrrigationSourceRepository.update(db, source_id, current_user.id, source_data)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Irrigation source not found"
        )
    return source


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_irrigation_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an irrigation source"""
    success = IrrigationSourceRepository.delete(db, source_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Irrigation source not found"
        )


# ============================================================================
# IRRIGATION ZONES
# ============================================================================

@router.post("/zones", response_model=IrrigationZoneResponse, status_code=status.HTTP_201_CREATED)
def create_irrigation_zone(
    zone_data: IrrigationZoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new irrigation zone"""
    zone = IrrigationZoneRepository.create(db, current_user.id, zone_data)
    return zone


@router.get("/zones", response_model=List[IrrigationZoneResponse])
def get_irrigation_zones(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all irrigation zones for the current user"""
    zones_with_counts = IrrigationZoneRepository.get_with_garden_count(db, current_user.id)

    # Transform to response format
    zones = []
    for zone, garden_count in zones_with_counts:
        zone_dict = IrrigationZoneResponse.model_validate(zone).model_dump()
        zone_dict['garden_count'] = garden_count
        zones.append(IrrigationZoneResponse(**zone_dict))

    return zones


@router.get("/zones/{zone_id}", response_model=IrrigationZoneResponse)
def get_irrigation_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific irrigation zone by ID"""
    zone = IrrigationZoneRepository.get_by_id(db, zone_id, current_user.id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Irrigation zone not found"
        )
    return zone


@router.patch("/zones/{zone_id}", response_model=IrrigationZoneResponse)
def update_irrigation_zone(
    zone_id: int,
    zone_data: IrrigationZoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an irrigation zone"""
    zone = IrrigationZoneRepository.update(db, zone_id, current_user.id, zone_data)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Irrigation zone not found"
        )
    return zone


@router.delete("/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_irrigation_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an irrigation zone (gardens will be unassigned)"""
    success = IrrigationZoneRepository.delete(db, zone_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Irrigation zone not found"
        )


# ============================================================================
# WATERING EVENTS
# ============================================================================

@router.post("/events", response_model=WateringEventResponse, status_code=status.HTTP_201_CREATED)
def create_watering_event(
    event_data: WateringEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a watering event"""
    # Verify zone ownership
    zone = IrrigationZoneRepository.get_by_id(db, event_data.irrigation_zone_id, current_user.id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Irrigation zone not found"
        )

    event = WateringEventRepository.create(db, current_user.id, event_data)
    return event


@router.get("/events", response_model=List[WateringEventResponse])
def get_watering_events(
    zone_id: Optional[int] = Query(None, description="Filter by zone ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get watering events, optionally filtered by zone"""
    if zone_id is not None:
        events = WateringEventRepository.get_by_zone(db, zone_id, current_user.id, days)
    else:
        events = WateringEventRepository.get_all(db, current_user.id, limit=100)

    return events


@router.get("/events/{event_id}", response_model=WateringEventResponse)
def get_watering_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific watering event by ID"""
    event = WateringEventRepository.get_by_id(db, event_id, current_user.id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watering event not found"
        )
    return event


@router.patch("/events/{event_id}", response_model=WateringEventResponse)
def update_watering_event(
    event_id: int,
    event_data: WateringEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a watering event"""
    event = WateringEventRepository.update(db, event_id, current_user.id, event_data)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watering event not found"
        )
    return event


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watering_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a watering event"""
    success = WateringEventRepository.delete(db, event_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watering event not found"
        )


# ============================================================================
# HIGH-LEVEL OPERATIONS
# ============================================================================

@router.get("/overview")
def get_irrigation_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete irrigation overview.

    Includes zones, sources, recent events, and upcoming scheduled waterings.
    """
    overview = IrrigationService.get_irrigation_overview(db, current_user.id)
    return overview


@router.get("/zones/{zone_id}/details")
def get_zone_details(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific zone"""
    details = IrrigationService.get_zone_details(db, zone_id, current_user.id)
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Irrigation zone not found"
        )
    return details


@router.get("/insights")
def get_irrigation_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get science-based irrigation insights and recommendations.

    Returns analysis of watering practices with actionable suggestions.
    """
    insights = IrrigationService.get_irrigation_insights(db, current_user.id)

    # Convert dataclasses to dicts
    return {
        'insights': [
            {
                'rule_id': rule.rule_id,
                'severity': rule.severity.value,
                'title': rule.title,
                'explanation': rule.explanation,
                'suggested_action': rule.suggested_action,
                'affected_zones': rule.affected_zones,
                'affected_gardens': rule.affected_gardens
            }
            for rule in insights
        ],
        'total_count': len(insights),
        'by_severity': {
            'critical': sum(1 for r in insights if r.severity.value == 'critical'),
            'warning': sum(1 for r in insights if r.severity.value == 'warning'),
            'info': sum(1 for r in insights if r.severity.value == 'info')
        }
    }


@router.post("/gardens/{garden_id}/assign-zone")
def assign_garden_to_zone(
    garden_id: int,
    zone_id: Optional[int] = Query(None, description="Zone ID to assign to, or null to unassign"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign a garden to an irrigation zone (or remove from zone)"""
    success = IrrigationService.assign_garden_to_zone(db, garden_id, zone_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garden or zone not found"
        )
    return {"message": "Garden assignment updated successfully"}
