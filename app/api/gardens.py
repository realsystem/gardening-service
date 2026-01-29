"""Garden API endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.garden import GardenCreate, GardenUpdate, GardenResponse
from app.repositories.garden_repository import GardenRepository
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/gardens", tags=["gardens"])


@router.post("", response_model=GardenResponse, status_code=status.HTTP_201_CREATED)
def create_garden(
    garden_data: GardenCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new garden"""
    repo = GardenRepository(db)
    garden = repo.create(
        user_id=current_user.id,
        name=garden_data.name,
        description=garden_data.description
    )
    return garden


@router.get("", response_model=List[GardenResponse])
def get_gardens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all gardens for current user"""
    repo = GardenRepository(db)
    gardens = repo.get_user_gardens(current_user.id)
    return gardens


@router.get("/{garden_id}", response_model=GardenResponse)
def get_garden(
    garden_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific garden"""
    repo = GardenRepository(db)
    garden = repo.get_by_id(garden_id)

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

    return garden


@router.patch("/{garden_id}", response_model=GardenResponse)
def update_garden(
    garden_id: int,
    garden_data: GardenUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a garden"""
    repo = GardenRepository(db)
    garden = repo.get_by_id(garden_id)

    if not garden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garden not found"
        )

    if garden.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this garden"
        )

    # Update only provided fields
    update_data = garden_data.model_dump(exclude_unset=True)
    garden = repo.update(garden, **update_data)

    return garden


@router.delete("/{garden_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_garden(
    garden_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a garden"""
    repo = GardenRepository(db)
    garden = repo.get_by_id(garden_id)

    if not garden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garden not found"
        )

    if garden.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this garden"
        )

    repo.delete(garden)
