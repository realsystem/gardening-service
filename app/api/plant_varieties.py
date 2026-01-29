"""PlantVariety API endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.plant_variety import PlantVarietyResponse
from app.repositories.plant_variety_repository import PlantVarietyRepository
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/plant-varieties", tags=["plant-varieties"])


@router.get("", response_model=List[PlantVarietyResponse])
def get_plant_varieties(
    search: Optional[str] = Query(None, description="Search by common name"),
    db: Session = Depends(get_db)
):
    """
    Get all plant varieties, optionally filtered by search term.
    Public endpoint - no authentication required (read-only global data).
    """
    repo = PlantVarietyRepository(db)

    if search:
        varieties = repo.search_by_name(search)
    else:
        varieties = repo.get_all()

    return varieties


@router.get("/{variety_id}", response_model=PlantVarietyResponse)
def get_plant_variety(
    variety_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific plant variety.
    Public endpoint - no authentication required (read-only global data).
    """
    repo = PlantVarietyRepository(db)
    variety = repo.get_by_id(variety_id)

    if not variety:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant variety not found"
        )

    return variety
