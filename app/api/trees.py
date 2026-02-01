"""Tree API endpoints - manage trees that cast shade on gardens"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.tree import TreeCreate, TreeUpdate, TreeResponse, TreeWithSpecies
from app.repositories.tree_repository import TreeRepository
from app.repositories.land_repository import LandRepository
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/trees", tags=["trees"])


@router.post("", response_model=TreeResponse, status_code=status.HTTP_201_CREATED)
def create_tree(
    tree_data: TreeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new tree on a land plot.

    Trees cast shade on nearby gardens based on their canopy radius.
    Coordinate system matches the land plot (top-left origin).
    """
    # Verify land belongs to user
    land_repo = LandRepository(db)
    land = land_repo.get_by_id(tree_data.land_id)

    if not land:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land not found"
        )

    if land.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add trees to this land"
        )

    # Create tree
    tree_repo = TreeRepository(db)
    tree_dict = tree_data.model_dump(exclude_unset=True)
    tree = tree_repo.create(
        user_id=current_user.id,
        **tree_dict
    )
    return tree


@router.get("", response_model=List[TreeResponse])
def get_user_trees(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all trees for current user across all land plots"""
    tree_repo = TreeRepository(db)
    trees = tree_repo.get_user_trees(current_user.id)
    return trees


@router.get("/land/{land_id}", response_model=List[TreeWithSpecies])
def get_land_trees(
    land_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all trees on a specific land plot with species details"""
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

    tree_repo = TreeRepository(db)
    trees = tree_repo.get_land_trees_with_species(land_id)

    # Convert to TreeWithSpecies response
    response = []
    for tree in trees:
        tree_dict = {
            "id": tree.id,
            "user_id": tree.user_id,
            "land_id": tree.land_id,
            "name": tree.name,
            "species_id": tree.species_id,
            "x": tree.x,
            "y": tree.y,
            "canopy_radius": tree.canopy_radius,
            "height": tree.height,
            "created_at": tree.created_at,
            "updated_at": tree.updated_at,
            "species_common_name": tree.species.common_name if tree.species else None,
            "species_scientific_name": tree.species.scientific_name if tree.species else None,
        }
        response.append(tree_dict)

    return response


@router.get("/{tree_id}", response_model=TreeWithSpecies)
def get_tree(
    tree_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tree details with species information"""
    tree_repo = TreeRepository(db)
    tree = tree_repo.get_tree_with_species(tree_id)

    if not tree:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree not found"
        )

    if tree.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this tree"
        )

    # Convert to TreeWithSpecies response
    tree_dict = {
        "id": tree.id,
        "user_id": tree.user_id,
        "land_id": tree.land_id,
        "name": tree.name,
        "species_id": tree.species_id,
        "x": tree.x,
        "y": tree.y,
        "canopy_radius": tree.canopy_radius,
        "height": tree.height,
        "created_at": tree.created_at,
        "updated_at": tree.updated_at,
        "species_common_name": tree.species.common_name if tree.species else None,
        "species_scientific_name": tree.species.scientific_name if tree.species else None,
    }

    return tree_dict


@router.patch("/{tree_id}", response_model=TreeResponse)
def update_tree(
    tree_id: int,
    tree_data: TreeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update tree properties (location, size, etc.)"""
    tree_repo = TreeRepository(db)
    tree = tree_repo.get_by_id(tree_id)

    if not tree:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree not found"
        )

    if tree.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this tree"
        )

    update_dict = tree_data.model_dump(exclude_unset=True)
    tree = tree_repo.update(tree, **update_dict)
    return tree


@router.delete("/{tree_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tree(
    tree_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a tree"""
    tree_repo = TreeRepository(db)
    tree = tree_repo.get_by_id(tree_id)

    if not tree:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree not found"
        )

    if tree.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this tree"
        )

    tree_repo.delete(tree)
    return None


@router.get("/{tree_id}/shadow-extent")
def get_tree_shadow_extent(
    tree_id: int,
    latitude: float = 40.0,
    hour: float | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate seasonal shadow extent for a tree.

    Returns shadow rectangles for winter, equinox, and summer based on
    sun altitude angles at the given latitude.

    Query parameters:
    - latitude: Latitude for sun angle calculation (default: 40.0 for temperate zone)
    - hour: Hour of day for shadow calculation (0-24, default: None for seasonal midday shadows)
    """
    from app.services.sun_exposure_service import SunExposureService

    tree_repo = TreeRepository(db)
    tree = tree_repo.get_by_id(tree_id)

    if not tree:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree not found"
        )

    if tree.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this tree"
        )

    # Get shadow extent data using the service
    shadow_data = SunExposureService.get_tree_shadow_extent(tree, latitude, hour)

    return shadow_data
