"""GerminationEvent API endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.germination_event import GerminationEventCreate, GerminationEventUpdate, GerminationEventResponse
from app.repositories.germination_event_repository import GerminationEventRepository
from app.repositories.seed_batch_repository import SeedBatchRepository
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/germination-events", tags=["germination-events"])


@router.post("", response_model=GerminationEventResponse, status_code=status.HTTP_201_CREATED)
def create_germination_event(
    event_data: GerminationEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new germination event"""
    # Verify seed batch exists and belongs to user
    batch_repo = SeedBatchRepository(db)
    batch = batch_repo.get_by_id(event_data.seed_batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seed batch not found"
        )
    if batch.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this seed batch"
        )

    # Create germination event
    event_repo = GerminationEventRepository(db)
    event = event_repo.create(
        user_id=current_user.id,
        seed_batch_id=event_data.seed_batch_id,
        plant_variety_id=batch.plant_variety_id,
        started_date=event_data.started_date,
        germination_location=event_data.germination_location,
        seed_count=event_data.seed_count,
        notes=event_data.notes
    )

    return event


@router.get("", response_model=List[GerminationEventResponse])
def get_germination_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all germination events for current user"""
    repo = GerminationEventRepository(db)
    events = repo.get_user_events(current_user.id)
    return events


@router.get("/{event_id}", response_model=GerminationEventResponse)
def get_germination_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific germination event"""
    repo = GerminationEventRepository(db)
    event = repo.get_by_id(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Germination event not found"
        )

    if event.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this germination event"
        )

    return event


@router.patch("/{event_id}", response_model=GerminationEventResponse)
def update_germination_event(
    event_id: int,
    event_data: GerminationEventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a germination event"""
    repo = GerminationEventRepository(db)
    event = repo.get_by_id(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Germination event not found"
        )

    if event.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this germination event"
        )

    update_data = event_data.model_dump(exclude_unset=True)
    event = repo.update(event, **update_data)

    return event
