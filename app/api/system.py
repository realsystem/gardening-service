"""System-level API endpoints (admin-only)"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.api.dependencies import get_current_admin_user
from app.models.user import User

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/stats")
def get_system_stats(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get system-wide statistics.

    **Admin-only endpoint** - Returns aggregate statistics about the platform.

    Returns:
        - total_users: Total number of registered users
        - active_users_24h: Users who logged in within last 24 hours (placeholder)
        - total_gardens: Total gardens across all users
        - total_lands: Total land plots across all users

    Raises:
        403: If current user is not an admin
    """
    # Count total users
    total_users = db.query(func.count(User.id)).scalar()

    # Note: We don't currently track "last login" so active users is a placeholder
    # In a real implementation, you'd track last_login_at on User model
    active_users_24h = 0  # Placeholder - would need last_login_at field

    # Import here to avoid circular imports
    from app.models.garden import Garden
    from app.models.land import Land

    total_gardens = db.query(func.count(Garden.id)).scalar()
    total_lands = db.query(func.count(Land.id)).scalar()

    return {
        "total_users": total_users,
        "active_users_24h": active_users_24h,
        "total_gardens": total_gardens,
        "total_lands": total_lands,
        "timestamp": datetime.utcnow().isoformat()
    }
