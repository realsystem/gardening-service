"""Admin API endpoints for user management"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.database import get_db
from app.api.dependencies import get_current_admin_user
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.feature_flags import reload_feature_flags, get_feature_flag_status

router = APIRouter(prefix="/admin", tags=["admin"])

# Set up audit logging
logger = logging.getLogger(__name__)


@router.post("/users/{user_id}/promote")
def promote_user_to_admin(
    user_id: int,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Promote a user to admin status.

    **Admin-only endpoint** - Grants admin privileges to the specified user.

    Security considerations:
    - Only existing admins can promote users
    - Operation is logged for audit purposes
    - Idempotent - promoting an already-admin user is a no-op

    Args:
        user_id: ID of the user to promote
        admin: Current admin user (from dependency)
        db: Database session

    Returns:
        Success message with user details

    Raises:
        403: If current user is not an admin
        404: If target user not found
    """
    repo = UserRepository(db)

    # Get target user
    target_user = repo.get_by_id(user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    # Check if already admin (idempotent)
    if target_user.is_admin:
        logger.info(
            f"Admin promotion no-op: User {user_id} ({target_user.email}) is already an admin. "
            f"Requested by admin {admin.id} ({admin.email}) at {datetime.utcnow().isoformat()}"
        )
        return {
            "message": f"User {target_user.email} is already an admin",
            "user_id": user_id,
            "email": target_user.email,
            "is_admin": True
        }

    # Promote to admin
    target_user.is_admin = True
    db.commit()
    db.refresh(target_user)

    # Audit log
    logger.warning(
        f"ADMIN PROMOTION: User {user_id} ({target_user.email}) promoted to admin "
        f"by admin {admin.id} ({admin.email}) at {datetime.utcnow().isoformat()}"
    )

    return {
        "message": f"User {target_user.email} promoted to admin successfully",
        "user_id": user_id,
        "email": target_user.email,
        "is_admin": True,
        "promoted_by": admin.email,
        "promoted_at": datetime.utcnow().isoformat()
    }


@router.post("/users/{user_id}/revoke")
def revoke_admin_privileges(
    user_id: int,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Revoke admin privileges from a user.

    **Admin-only endpoint** - Removes admin privileges from the specified user.

    Security considerations:
    - Only existing admins can revoke privileges
    - Operation is logged for audit purposes
    - Cannot revoke your own admin privileges (safety check)

    Args:
        user_id: ID of the user to demote
        admin: Current admin user (from dependency)
        db: Database session

    Returns:
        Success message with user details

    Raises:
        403: If current user is not an admin
        400: If attempting to revoke own admin privileges
        404: If target user not found
    """
    # Prevent self-demotion
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot revoke your own admin privileges"
        )

    repo = UserRepository(db)

    # Get target user
    target_user = repo.get_by_id(user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    # Check if already non-admin (idempotent)
    if not target_user.is_admin:
        logger.info(
            f"Admin revocation no-op: User {user_id} ({target_user.email}) is not an admin. "
            f"Requested by admin {admin.id} ({admin.email}) at {datetime.utcnow().isoformat()}"
        )
        return {
            "message": f"User {target_user.email} is not an admin",
            "user_id": user_id,
            "email": target_user.email,
            "is_admin": False
        }

    # Revoke admin
    target_user.is_admin = False
    db.commit()
    db.refresh(target_user)

    # Audit log
    logger.warning(
        f"ADMIN REVOCATION: User {user_id} ({target_user.email}) demoted from admin "
        f"by admin {admin.id} ({admin.email}) at {datetime.utcnow().isoformat()}"
    )

    return {
        "message": f"Admin privileges revoked from {target_user.email}",
        "user_id": user_id,
        "email": target_user.email,
        "is_admin": False,
        "revoked_by": admin.email,
        "revoked_at": datetime.utcnow().isoformat()
    }


@router.get("/feature-flags")
def get_feature_flags(
    admin: User = Depends(get_current_admin_user)
):
    """
    Get current feature flag status.

    **Admin-only endpoint** - View all feature flags and their current state.

    Returns:
        Dictionary with:
        - flags: Current flag states (enabled/disabled)
        - last_reload: When flags were last reloaded
        - definitions: Flag metadata and descriptions
    """
    logger.info(
        f"Feature flags queried by admin {admin.id} ({admin.email}) at {datetime.utcnow().isoformat()}"
    )

    return get_feature_flag_status()


@router.post("/feature-flags/reload")
def reload_feature_flags_endpoint(
    admin: User = Depends(get_current_admin_user)
):
    """
    Reload feature flags from environment/config.

    **Admin-only endpoint** - Reload feature flags without restarting the service.

    Use cases:
    - Apply feature flag changes from environment variables
    - Quick incident response (disable broken features)
    - Runtime configuration updates

    Returns:
        Dictionary with reloaded flags and reload timestamp
    """
    logger.warning(
        f"FEATURE FLAGS RELOAD: Triggered by admin {admin.id} ({admin.email}) at {datetime.utcnow().isoformat()}"
    )

    reloaded_flags = reload_feature_flags()

    return {
        "message": "Feature flags reloaded successfully",
        "flags": reloaded_flags,
        "reloaded_by": admin.email,
        "reloaded_at": datetime.utcnow().isoformat()
    }
