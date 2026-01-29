"""PlantingEvent API endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.planting_event import PlantingEventCreate, PlantingEventUpdate, PlantingEventResponse
from app.repositories.planting_event_repository import PlantingEventRepository
from app.repositories.garden_repository import GardenRepository
from app.repositories.plant_variety_repository import PlantVarietyRepository
from app.api.dependencies import get_current_user
from app.models.user import User
from app.rules.task_generator import TaskGenerator

router = APIRouter(prefix="/planting-events", tags=["planting-events"])


@router.post("", response_model=PlantingEventResponse, status_code=status.HTTP_201_CREATED)
def create_planting_event(
    event_data: PlantingEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new planting event.
    Automatically generates care tasks (watering, harvest) based on rules.
    """
    # Verify garden exists and belongs to user
    garden_repo = GardenRepository(db)
    garden = garden_repo.get_by_id(event_data.garden_id)
    if not garden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garden not found"
        )
    if garden.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this garden"
        )

    # Verify plant variety exists
    variety_repo = PlantVarietyRepository(db)
    variety = variety_repo.get_by_id(event_data.plant_variety_id)
    if not variety:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant variety not found"
        )

    # Create planting event
    event_repo = PlantingEventRepository(db)
    event = event_repo.create(
        user_id=current_user.id,
        garden_id=event_data.garden_id,
        plant_variety_id=event_data.plant_variety_id,
        germination_event_id=event_data.germination_event_id,
        planting_date=event_data.planting_date,
        planting_method=event_data.planting_method,
        plant_count=event_data.plant_count,
        location_in_garden=event_data.location_in_garden,
        health_status=event_data.health_status,
        plant_notes=event_data.plant_notes,
        notes=event_data.notes
    )

    # Generate care tasks based on rules
    task_generator = TaskGenerator()
    task_generator.generate_tasks_for_planting(db, event, current_user.id)

    return event


@router.get("", response_model=List[PlantingEventResponse])
def get_planting_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all planting events for current user"""
    repo = PlantingEventRepository(db)
    events = repo.get_user_events(current_user.id)
    return events


@router.get("/{event_id}", response_model=PlantingEventResponse)
def get_planting_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific planting event"""
    repo = PlantingEventRepository(db)
    event = repo.get_by_id(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planting event not found"
        )

    if event.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this planting event"
        )

    return event


@router.patch("/{event_id}", response_model=PlantingEventResponse)
def update_planting_event(
    event_id: int,
    event_data: PlantingEventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a planting event"""
    repo = PlantingEventRepository(db)
    event = repo.get_by_id(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planting event not found"
        )

    if event.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this planting event"
        )

    update_data = event_data.model_dump(exclude_unset=True)
    event = repo.update(event, **update_data)

    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_planting_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a planting event.
    Cascades to delete all associated tasks.
    Historical data (sensor readings, soil samples, irrigation events) is preserved.
    """
    repo = PlantingEventRepository(db)
    event = repo.get_by_id(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planting event not found"
        )

    if event.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this planting event"
        )

    repo.delete(event)
