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
from app.schemas.garden_layout import GardenLayoutUpdate
from app.schemas.sensor_reading import SensorReadingResponse
from app.schemas.tree import GardenShadingInfo
from app.schemas.nutrient_optimization import NutrientOptimizationResponse, ECRecommendation, PHRecommendation, ReplacementSchedule, NutrientWarning, ActivePlanting
from app.repositories.garden_repository import GardenRepository
from app.repositories.sensor_reading_repository import SensorReadingRepository
from app.repositories.land_repository import LandRepository
from app.models.planting_event import PlantingEvent
from app.models.care_task import CareTask, TaskStatus
from app.models.plant_variety import PlantVariety
from app.api.dependencies import get_current_user
from app.models.user import User, UserGroup
from app.services.layout_service import (
    validate_spatial_data_complete,
    validate_garden_placement,
    apply_snap_to_grid
)
from app.utils.grid_config import GRID_RESOLUTION
from app.compliance.service import get_compliance_service
from app.utils.feature_gating import is_feature_enabled, require_user_group

router = APIRouter(prefix="/gardens", tags=["gardens"])


@router.post("", response_model=GardenResponse, status_code=status.HTTP_201_CREATED)
def create_garden(
    garden_data: GardenCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new garden.

    **Feature Gating**:
    - Amateur users: Cannot create hydroponic gardens
    - Researchers: Full access to all garden types
    """
    repo = GardenRepository(db)

    # Convert Pydantic model to dict, excluding unset values
    garden_dict = garden_data.model_dump(exclude_unset=True)

    # FEATURE GATE: Hydroponic gardens require researcher account
    if garden_dict.get('is_hydroponic', False):
        if not is_feature_enabled(current_user, 'hydroponics'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Hydroponic features not available",
                    "message": "Hydroponic gardens require a Scientific Researcher account",
                    "your_account_type": current_user.user_group.value.replace('_', ' ').title(),
                    "upgrade_info": "Change your account type to 'Scientific Researcher' in Settings"
                }
            )

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
            status=status_text,
            x=planting.x,
            y=planting.y
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
            status=status_text,
            x=planting.x,
            y=planting.y
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


@router.put("/{garden_id}/layout", response_model=GardenResponse)
def update_garden_layout(
    garden_id: int,
    layout_data: GardenLayoutUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update garden's spatial layout on a land.

    Validates:
    - All spatial fields provided together (all-or-nothing)
    - Garden fits within land boundaries
    - No overlap with other gardens on same land
    - Only owner can modify

    To remove garden from layout, set all fields to None.
    """
    garden_repo = GardenRepository(db)
    garden = garden_repo.get_by_id(garden_id)

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

    # Extract layout data
    land_id = layout_data.land_id
    x = layout_data.x
    y = layout_data.y
    width = layout_data.width
    height = layout_data.height
    snap_enabled = layout_data.snap_to_grid

    # Validate spatial data completeness (all-or-nothing)
    validation_error = validate_spatial_data_complete(land_id, x, y, width, height)
    if validation_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation_error.message
        )

    # If all fields are None, remove from layout
    if land_id is None:
        garden.land_id = None
        garden.x = None
        garden.y = None
        garden.width = None
        garden.height = None
        db.commit()
        db.refresh(garden)
        return garden

    # Validate land exists and belongs to user
    land_repo = LandRepository(db)
    land = land_repo.get_land_with_gardens(land_id)

    if not land:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land not found"
        )

    if land.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to place gardens on this land"
        )

    # Apply snap-to-grid if enabled
    x, y, width, height = apply_snap_to_grid(x, y, width, height, snap_enabled)

    # Validate placement (bounds and overlap) with snapped coordinates
    placement_error = validate_garden_placement(
        garden_id=garden_id,
        land=land,
        x=x,
        y=y,
        width=width,
        height=height,
        existing_gardens=land.gardens
    )

    if placement_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=placement_error.message
        )

    # Update garden layout
    garden.land_id = land_id
    garden.x = x
    garden.y = y
    garden.width = width
    garden.height = height

    db.commit()
    db.refresh(garden)

    return garden


@router.get("/{garden_id}/shading", response_model=GardenShadingInfo)
def get_garden_shading(
    garden_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate tree shading impact on a garden.

    Returns sun exposure score (0.0 to 1.0), categorical level (full_sun/partial_sun/shade),
    and details of all contributing trees.

    Requires garden to have spatial layout (x, y, width, height) on a land plot.
    """
    from app.repositories.tree_repository import TreeRepository
    from app.services.shading_service import calculate_garden_shading

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

    # Check if garden has spatial layout
    if garden.land_id is None or garden.x is None or garden.y is None \
       or garden.width is None or garden.height is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Garden must have spatial layout (land_id, x, y, width, height) to calculate shading"
        )

    # Get all trees on the same land
    tree_repo = TreeRepository(db)
    trees = tree_repo.get_land_trees(garden.land_id)

    # Convert trees to dicts for shading calculation
    tree_dicts = [
        {
            'id': t.id,
            'name': t.name,
            'x': t.x,
            'y': t.y,
            'canopy_radius': t.canopy_radius,
            'garden_id': garden_id  # for response
        }
        for t in trees
    ]

    # Calculate shading impact
    shading_impact = calculate_garden_shading(
        garden_x=garden.x,
        garden_y=garden.y,
        garden_width=garden.width,
        garden_height=garden.height,
        trees=tree_dicts if tree_dicts else [],  # Handle no trees case
        baseline_sun_exposure=1.0  # Assume full sun baseline
    )

    return GardenShadingInfo(
        garden_id=garden_id,
        sun_exposure_score=shading_impact.sun_exposure_score,
        sun_exposure_category=shading_impact.sun_exposure_category,
        total_shade_factor=shading_impact.total_shade_factor,
        contributing_trees=[
            {
                "tree_id": t['tree_id'],
                "tree_name": t['tree_name'],
                "shade_contribution": t['shade_contribution'],
                "intersection_area": t['intersection_area'],
                "average_intensity": t['average_intensity']
            }
            for t in shading_impact.contributing_trees
        ],
        baseline_sun_exposure=1.0
    )


@router.get("/{garden_id}/sun-exposure")
def get_garden_sun_exposure(
    garden_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate seasonal sun exposure for a garden based on tree shadow projections.

    Uses sun-path model with seasonal sun angles to predict shading throughout the year.
    Returns exposure score, seasonal shading percentages, and warnings.

    Requires garden to have spatial layout (x, y, width, height) on a land plot.
    """
    from app.services.sun_exposure_service import SunExposureService

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

    # Get sun exposure data using the service
    exposure_data = SunExposureService.get_garden_sun_exposure(garden, db)

    return exposure_data


@router.get("/{garden_id}/nutrient-optimization", response_model=NutrientOptimizationResponse)
@require_user_group([UserGroup.SCIENTIFIC_RESEARCHER])
def get_nutrient_optimization(
    garden_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get nutrient optimization plan for a hydroponic, fertigation, or container garden.

    **Requires**: Scientific Researcher account

    Returns science-based EC/pH recommendations, water replacement schedule, and warnings
    based on active plantings and their growth stages.

    Only applicable to:
    - Hydroponic systems (NFT, DWC, Drip, Ebb & Flow, Aeroponics, Wick)
    - Fertigation systems (soil + nutrient solution)
    - Container growing with nutrients

    Returns 400 error for traditional outdoor soil gardens.
    Returns 403 error for non-researcher accounts.
    """
    from app.services.nutrient_optimization_service import NutrientOptimizationService
    from app.models.garden import HydroSystemType

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

    # Validate garden is hydroponic/fertigation/container
    if not garden.is_hydroponic and garden.hydro_system_type not in [
        HydroSystemType.FERTIGATION,
        HydroSystemType.CONTAINER
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nutrient optimization only applies to hydroponic, fertigation, or container systems. "
                   "This garden is configured as a traditional soil garden."
        )

    # Check for plantings in garden to detect parameter-only optimization attempts
    from app.repositories.planting_event_repository import PlantingEventRepository
    planting_repo = PlantingEventRepository(db)
    all_plantings = planting_repo.get_by_garden(garden.id)
    has_plantings = len(all_plantings) > 0

    # Compliance check: detect parameter-only optimization attempts
    # (requesting optimization with no plants could be an attempt to reverse-engineer parameters)
    if not has_plantings:
        compliance_service = get_compliance_service(db)
        compliance_service.detect_parameter_only_optimization(
            user=current_user,
            garden_id=garden_id,
            has_plantings=has_plantings,
            request_metadata={
                "endpoint": "nutrient_optimization",
                "garden_id": garden_id,
                "system_type": garden.hydro_system_type.value if garden.hydro_system_type else None
            }
        )

    # Generate optimization using service
    service = NutrientOptimizationService()
    result = service.optimize_for_garden(garden, db)

    # Convert service result to API response
    return NutrientOptimizationResponse(
        garden_id=result.garden_id,
        garden_name=result.garden_name,
        system_type=result.system_type,
        ec_recommendation=ECRecommendation(
            min_ms_cm=result.ec_recommendation.min_ms_cm,
            max_ms_cm=result.ec_recommendation.max_ms_cm,
            rationale=result.ec_recommendation.rationale
        ),
        ph_recommendation=PHRecommendation(
            min_ph=result.ph_recommendation.min_ph,
            max_ph=result.ph_recommendation.max_ph,
            rationale=result.ph_recommendation.rationale
        ),
        replacement_schedule=ReplacementSchedule(
            topoff_interval_days=result.replacement_schedule.topoff_interval_days,
            full_replacement_days=result.replacement_schedule.full_replacement_days,
            rationale=result.replacement_schedule.rationale
        ),
        warnings=[
            NutrientWarning(
                warning_id=w.warning_id,
                severity=w.severity,
                message=w.message,
                mitigation=w.mitigation
            )
            for w in result.warnings
        ],
        active_plantings=[
            ActivePlanting(
                plant_name=p['plant_name'],
                growth_stage=p['growth_stage']
            )
            for p in result.active_plantings
        ],
        generated_at=result.generated_at
    )
