"""Garden API endpoints"""
from typing import List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.garden import GardenCreate, GardenUpdate, GardenResponse
from app.schemas.garden_details import (
    GardenDetailsResponse,
    PlantingInGardenResponse,
    TaskSummaryInGarden,
    GardenStatsResponse
)
from app.schemas.sensor_reading import SensorReadingResponse
from app.repositories.garden_repository import GardenRepository
from app.repositories.sensor_reading_repository import SensorReadingRepository
from app.models.planting_event import PlantingEvent
from app.models.care_task import CareTask, TaskStatus
from app.models.plant_variety import PlantVariety
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
    # Convert Pydantic model to dict, excluding unset values
    garden_dict = garden_data.model_dump(exclude_unset=True)
    garden = repo.create(
        user_id=current_user.id,
        **garden_dict
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


@router.get("/{garden_id}", response_model=GardenDetailsResponse)
def get_garden(
    garden_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific garden with full details (plantings, tasks, stats)"""
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

    # Get plantings for this garden
    planting_events = db.query(PlantingEvent).filter(
        PlantingEvent.garden_id == garden_id
    ).all()

    # Build planting responses with plant names and harvest info
    plantings = []
    for planting in planting_events:
        # Get plant variety details
        variety = db.query(PlantVariety).filter(
            PlantVariety.id == planting.plant_variety_id
        ).first()

        # Calculate expected harvest date and status
        expected_harvest_date = None
        status_text = "growing"

        if variety and variety.days_to_harvest:
            expected_harvest_date = planting.planting_date + timedelta(days=variety.days_to_harvest)

            # Determine status based on dates
            days_since_planting = (date.today() - planting.planting_date).days
            if days_since_planting < 0:
                status_text = "pending"
            elif variety.days_to_harvest and days_since_planting >= variety.days_to_harvest:
                status_text = "ready_to_harvest"
            else:
                status_text = "growing"

        plantings.append(PlantingInGardenResponse(
            id=planting.id,
            plant_variety_id=planting.plant_variety_id,
            plant_name=variety.common_name if variety else "Unknown",
            variety_name=variety.variety_name if variety else None,
            planting_date=planting.planting_date,
            planting_method=planting.planting_method,
            plant_count=planting.plant_count,
            location_in_garden=planting.location_in_garden,
            health_status=planting.health_status,
            expected_harvest_date=expected_harvest_date,
            days_to_harvest=variety.days_to_harvest if variety else None,
            status=status_text
        ))

    # Get tasks for this garden (via planting events)
    planting_ids = [p.id for p in planting_events]
    tasks_query = db.query(CareTask).filter(
        CareTask.planting_event_id.in_(planting_ids)
    ) if planting_ids else db.query(CareTask).filter(False)

    all_tasks = tasks_query.order_by(CareTask.due_date.asc()).all()

    task_summaries = [
        TaskSummaryInGarden(
            id=task.id,
            title=task.title,
            task_type=task.task_type.value,
            priority=task.priority.value,
            due_date=task.due_date,
            status=task.status.value,
            planting_event_id=task.planting_event_id
        )
        for task in all_tasks
    ]

    # Calculate stats
    active_plantings = len([p for p in plantings if p.status in ["growing", "ready_to_harvest"]])
    pending_tasks = len([t for t in all_tasks if t.status == TaskStatus.PENDING])
    high_priority_tasks = len([t for t in all_tasks if t.priority.value == "high" and t.status == TaskStatus.PENDING])
    upcoming_harvests = len([p for p in plantings if p.status == "ready_to_harvest"])

    stats = GardenStatsResponse(
        total_plantings=len(plantings),
        active_plantings=active_plantings,
        total_tasks=len(all_tasks),
        pending_tasks=pending_tasks,
        high_priority_tasks=high_priority_tasks,
        upcoming_harvests=upcoming_harvests
    )

    return GardenDetailsResponse(
        garden=GardenResponse.model_validate(garden),
        plantings=plantings,
        tasks=task_summaries,
        stats=stats
    )


@router.get("/{garden_id}/plantings", response_model=List[PlantingInGardenResponse])
def get_garden_plantings(
    garden_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all plantings for a specific garden"""
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

    # Get all planting events for this garden
    planting_events = db.query(PlantingEvent).filter(
        PlantingEvent.garden_id == garden_id
    ).order_by(PlantingEvent.planting_date.desc()).all()

    # Build response with plant names and harvest info
    plantings = []
    for planting in planting_events:
        # Get plant variety details
        variety = db.query(PlantVariety).filter(
            PlantVariety.id == planting.plant_variety_id
        ).first()

        # Calculate expected harvest date and status
        expected_harvest_date = None
        status_text = "growing"

        if variety and variety.days_to_harvest:
            expected_harvest_date = planting.planting_date + timedelta(days=variety.days_to_harvest)

            # Determine status based on dates
            days_since_planting = (date.today() - planting.planting_date).days
            if days_since_planting < 0:
                status_text = "pending"
            elif variety.days_to_harvest and days_since_planting >= variety.days_to_harvest:
                status_text = "ready_to_harvest"
            else:
                status_text = "growing"

        plantings.append(PlantingInGardenResponse(
            id=planting.id,
            plant_variety_id=planting.plant_variety_id,
            plant_name=variety.common_name if variety else "Unknown",
            variety_name=variety.variety_name if variety else None,
            planting_date=planting.planting_date,
            planting_method=planting.planting_method,
            plant_count=planting.plant_count,
            location_in_garden=planting.location_in_garden,
            health_status=planting.health_status,
            expected_harvest_date=expected_harvest_date,
            days_to_harvest=variety.days_to_harvest if variety else None,
            status=status_text
        ))

    return plantings


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
    """Delete a garden (cascades to delete all associated plantings and tasks)"""
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


@router.get("/{garden_id}/sensor-readings", response_model=List[SensorReadingResponse])
def get_garden_sensor_readings(
    garden_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all sensor readings for a specific garden.
    Returns readings sorted by timestamp descending (most recent first).
    """
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

    # Get all sensor readings for this garden, sorted by date descending
    reading_repo = SensorReadingRepository(db)
    readings = reading_repo.get_by_garden(garden_id)

    return readings
