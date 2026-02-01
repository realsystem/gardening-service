"""Structure API endpoints - manage structures that cast shadows on gardens"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.structure import StructureCreate, StructureUpdate, StructureResponse
from app.repositories.structure_repository import StructureRepository
from app.repositories.land_repository import LandRepository
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/structures", tags=["structures"])


@router.post("", response_model=StructureResponse, status_code=status.HTTP_201_CREATED)
def create_structure(
    structure_data: StructureCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new structure on a land plot.

    Structures (buildings, fences, walls, etc.) cast shadows on nearby gardens
    based on their height and dimensions.
    Coordinate system matches the land plot (top-left origin).
    """
    # Verify land belongs to user
    land_repo = LandRepository(db)
    land = land_repo.get_by_id(structure_data.land_id)

    if not land:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land not found"
        )

    if land.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add structures to this land"
        )

    # Create structure
    structure_repo = StructureRepository(db)
    structure_dict = structure_data.model_dump(exclude_unset=True)
    structure = structure_repo.create(
        user_id=current_user.id,
        land_id=structure_data.land_id,
        **{k: v for k, v in structure_dict.items() if k != 'land_id'}
    )
    return structure


@router.get("", response_model=List[StructureResponse])
def get_user_structures(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all structures for current user across all land plots"""
    structure_repo = StructureRepository(db)
    structures = structure_repo.get_user_structures(current_user.id)
    return structures


@router.get("/land/{land_id}", response_model=List[StructureResponse])
def get_land_structures(
    land_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all structures on a specific land plot"""
    # Verify land belongs to user
    land_repo = LandRepository(db)
    land = land_repo.get_by_id(land_id)

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

    structure_repo = StructureRepository(db)
    structures = structure_repo.get_by_land(land_id)
    return structures


@router.get("/{structure_id}", response_model=StructureResponse)
def get_structure(
    structure_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get structure details"""
    structure_repo = StructureRepository(db)
    structure = structure_repo.get_by_id(structure_id)

    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure not found"
        )

    if structure.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this structure"
        )

    return structure


@router.patch("/{structure_id}", response_model=StructureResponse)
def update_structure(
    structure_id: int,
    structure_data: StructureUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update structure properties (location, size, etc.)"""
    structure_repo = StructureRepository(db)
    structure = structure_repo.get_by_id(structure_id)

    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure not found"
        )

    if structure.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this structure"
        )

    update_dict = structure_data.model_dump(exclude_unset=True)
    structure = structure_repo.update(structure, **update_dict)
    return structure


@router.delete("/{structure_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_structure(
    structure_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a structure"""
    structure_repo = StructureRepository(db)
    structure = structure_repo.get_by_id(structure_id)

    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure not found"
        )

    if structure.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this structure"
        )

    structure_repo.delete(structure)
    return None


@router.get("/{structure_id}/shadow-extent")
def get_structure_shadow_extent(
    structure_id: int,
    latitude: float = 40.0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate seasonal shadow extent for a structure.

    Returns shadow rectangles for winter, equinox, and summer based on
    sun altitude angles at the given latitude.

    Query parameters:
    - latitude: Latitude for sun angle calculation (default: 40.0 for temperate zone)
    """
    from app.services.sun_exposure_service import SunExposureService

    structure_repo = StructureRepository(db)
    structure = structure_repo.get_by_id(structure_id)

    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure not found"
        )

    if structure.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this structure"
        )

    # Get shadow extent data using the service
    shadow_data = SunExposureService.get_structure_shadow_extent(structure, latitude)

    return shadow_data
