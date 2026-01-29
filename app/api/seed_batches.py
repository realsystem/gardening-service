"""SeedBatch API endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.seed_batch import SeedBatchCreate, SeedBatchUpdate, SeedBatchResponse
from app.repositories.seed_batch_repository import SeedBatchRepository
from app.repositories.plant_variety_repository import PlantVarietyRepository
from app.api.dependencies import get_current_user
from app.models.user import User
from app.rules.task_generator import TaskGenerator

router = APIRouter(prefix="/seed-batches", tags=["seed-batches"])


@router.post("", response_model=SeedBatchResponse, status_code=status.HTTP_201_CREATED)
def create_seed_batch(
    batch_data: SeedBatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new seed batch.
    Automatically generates viability warning tasks if seeds are old.
    """
    # Verify plant variety exists
    variety_repo = PlantVarietyRepository(db)
    variety = variety_repo.get_by_id(batch_data.plant_variety_id)
    if not variety:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant variety not found"
        )

    # Create seed batch
    batch_repo = SeedBatchRepository(db)
    batch = batch_repo.create(
        user_id=current_user.id,
        plant_variety_id=batch_data.plant_variety_id,
        source=batch_data.source,
        harvest_year=batch_data.harvest_year,
        quantity=batch_data.quantity,
        notes=batch_data.notes
    )

    # Generate viability warning tasks if applicable
    task_generator = TaskGenerator()
    task_generator.generate_tasks_for_seed_batch(db, batch, current_user.id)

    return batch


@router.get("", response_model=List[SeedBatchResponse])
def get_seed_batches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all seed batches for current user"""
    repo = SeedBatchRepository(db)
    batches = repo.get_user_batches(current_user.id)
    return batches


@router.get("/{batch_id}", response_model=SeedBatchResponse)
def get_seed_batch(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific seed batch"""
    repo = SeedBatchRepository(db)
    batch = repo.get_by_id(batch_id)

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

    return batch


@router.patch("/{batch_id}", response_model=SeedBatchResponse)
def update_seed_batch(
    batch_id: int,
    batch_data: SeedBatchUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a seed batch"""
    repo = SeedBatchRepository(db)
    batch = repo.get_by_id(batch_id)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seed batch not found"
        )

    if batch.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this seed batch"
        )

    update_data = batch_data.model_dump(exclude_unset=True)
    batch = repo.update(batch, **update_data)

    return batch


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_seed_batch(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a seed batch"""
    repo = SeedBatchRepository(db)
    batch = repo.get_by_id(batch_id)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seed batch not found"
        )

    if batch.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this seed batch"
        )

    repo.delete(batch)
