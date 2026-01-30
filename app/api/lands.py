"""Land API endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.land import (
    LandCreate,
    LandUpdate,
    LandResponse,
    LandWithGardensResponse
)
from app.repositories.land_repository import LandRepository
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/lands", tags=["lands"])


@router.post("", response_model=LandResponse, status_code=status.HTTP_201_CREATED)
def create_land(
    land_data: LandCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new land area for placing gardens.

    All measurements use abstract units (meters, feet, or grid squares - user's choice).
    """
    repo = LandRepository(db)
    land_dict = land_data.model_dump(exclude_unset=True)
    land = repo.create(
        user_id=current_user.id,
        **land_dict
    )
    return land


@router.get("", response_model=List[LandResponse])
def get_lands(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all lands for current user"""
    repo = LandRepository(db)
    lands = repo.get_user_lands(current_user.id)
    return lands


@router.get("/{land_id}", response_model=LandWithGardensResponse)
def get_land(
    land_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get land details with all gardens placed on it.

    Useful for displaying land layout with all garden positions.
    """
    repo = LandRepository(db)
    land = repo.get_land_with_gardens(land_id)

    if not land:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land not found"
        )

    if land.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this land"
        )

    return land


@router.patch("/{land_id}", response_model=LandResponse)
def update_land(
    land_id: int,
    land_data: LandUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update land properties.

    Note: Changing dimensions may cause gardens to be out of bounds.
    Validate garden placements after updating land size.
    """
    repo = LandRepository(db)
    land = repo.get_land_with_gardens(land_id)

    if not land:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land not found"
        )

    if land.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this land"
        )

    # Check if reducing dimensions would cause gardens to exceed bounds
    update_dict = land_data.model_dump(exclude_unset=True)
    new_width = update_dict.get('width', land.width)
    new_height = update_dict.get('height', land.height)

    # Warn if any gardens would be out of bounds
    for garden in land.gardens:
        if garden.x is not None and garden.width is not None:
            if garden.x + garden.width > new_width:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Cannot reduce width: Garden '{garden.name}' (ID: {garden.id}) "
                        f"would exceed new bounds"
                    )
                )
        if garden.y is not None and garden.height is not None:
            if garden.y + garden.height > new_height:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Cannot reduce height: Garden '{garden.name}' (ID: {garden.id}) "
                        f"would exceed new bounds"
                    )
                )

    land = repo.update(land, **update_dict)
    return land


@router.delete("/{land_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_land(
    land_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a land.

    All gardens on this land will have their land_id set to NULL (orphaned).
    Gardens themselves are not deleted.
    """
    repo = LandRepository(db)
    land = repo.get_by_id(land_id)

    if not land:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land not found"
        )

    if land.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this land"
        )

    repo.delete(land)
    return None
