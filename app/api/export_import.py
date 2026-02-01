"""Export/Import API endpoints for user data portability"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.export_service import ExportService
from app.services.import_service import ImportService
from app.schemas.export_import import (
    ExportData,
    ImportRequest,
    ImportPreview,
    ImportResult,
    ImportMode,
)

router = APIRouter(prefix="/export-import", tags=["export-import"])


@router.get("/export", response_model=ExportData)
def export_user_data(
    include_sensor_readings: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export all user data to a portable JSON format.

    This endpoint exports all user data including:
    - User profile (non-sensitive data only)
    - Lands and their layouts
    - Gardens with all configuration
    - Trees and their positions
    - Planting events
    - Soil samples
    - Irrigation sources, zones, and watering events
    - Sensor readings (optional - can be large)

    The export includes metadata with schema version for compatibility checking.
    Sensitive data (email, password, auth tokens) is never included.

    Args:
        include_sensor_readings: Include sensor readings (can make file large)
        current_user: Authenticated user
        db: Database session

    Returns:
        ExportData: Complete user data in portable format
    """
    try:
        export_data = ExportService.export_user_data(
            db=db,
            user=current_user,
            include_sensor_readings=include_sensor_readings
        )
        return export_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {str(e)}"
        )


@router.post("/import/preview", response_model=ImportPreview)
def preview_import(
    import_data: ExportData,
    mode: str = ImportMode.DRY_RUN,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Preview what would happen if data is imported (dry-run validation).

    This endpoint validates the import data without making any changes:
    - Checks schema version compatibility
    - Validates all relationships and foreign keys
    - Validates data types and required fields
    - Checks for potential conflicts
    - Counts items that would be imported
    - In overwrite mode, shows how many items would be deleted

    Args:
        import_data: Data to import (from export endpoint)
        mode: Import mode (dry_run, merge, or overwrite)
        current_user: Authenticated user (data will be imported to this user)
        db: Database session

    Returns:
        ImportPreview: Validation results and preview of changes
    """
    # Validate mode
    if mode not in [ImportMode.DRY_RUN, ImportMode.MERGE, ImportMode.OVERWRITE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode. Must be one of: {ImportMode.DRY_RUN}, {ImportMode.MERGE}, {ImportMode.OVERWRITE}"
        )

    try:
        preview = ImportService.validate_import(
            db=db,
            user=current_user,
            data=import_data,
            mode=mode
        )
        return preview
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate import: {str(e)}"
        )


@router.post("/import", response_model=ImportResult)
def import_user_data(
    request: ImportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import user data with specified mode.

    Import modes:
    - dry_run: Validate only, make no changes (returns validation results)
    - merge: Import data alongside existing data (new IDs assigned, no deletion)
    - overwrite: Delete all existing user data first, then import (DESTRUCTIVE!)

    Import process:
    1. Validates schema version compatibility (major version must match)
    2. Validates all relationships and data integrity
    3. If validation fails, returns error (no partial imports)
    4. In dry_run mode: stops here, returns validation results
    5. In overwrite mode: deletes all existing data first
    6. Imports data with proper ID remapping to preserve relationships
    7. Uses database transaction (commits all or rolls back on error)

    Security:
    - Data is always imported to the authenticated user (ownership reassigned)
    - Email, password, and auth tokens are never imported
    - All imported data becomes owned by the importing user

    Args:
        request: Import request with mode and data
        current_user: Authenticated user (data owner after import)
        db: Database session

    Returns:
        ImportResult: Results including counts, errors, warnings, ID mappings

    Raises:
        HTTPException: If validation fails or import encounters errors
    """
    # Validate mode
    if request.mode not in [ImportMode.DRY_RUN, ImportMode.MERGE, ImportMode.OVERWRITE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode. Must be one of: {ImportMode.DRY_RUN}, {ImportMode.MERGE}, {ImportMode.OVERWRITE}"
        )

    # Special confirmation for overwrite mode
    if request.mode == ImportMode.OVERWRITE:
        # Count existing data
        from app.models.land import Land
        existing_count = db.query(Land).filter(Land.user_id == current_user.id).count()
        if existing_count > 0:
            # This is a destructive operation - user should be warned in frontend
            pass

    try:
        result = ImportService.import_user_data(
            db=db,
            user=current_user,
            data=request.data,
            mode=request.mode
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Import failed: {', '.join(result.errors)}"
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        # Rollback should already have happened in the service
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import data: {str(e)}"
        )
