"""Admin-only compliance API endpoints.

These endpoints provide visibility into restricted plant detection events
and user flagging. Access is restricted to admin users only.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.api.dependencies import get_current_admin_user
from app.models.user import User
from app.compliance import DENY_LIST_VERSION
from pydantic import BaseModel


router = APIRouter(prefix="/admin/compliance", tags=["admin", "compliance"])


# Response models
class FlaggedUserResponse(BaseModel):
    """Response model for flagged user summary."""
    id: int
    email: str
    display_name: str | None
    restricted_crop_flag: bool
    restricted_crop_count: int
    restricted_crop_first_violation: datetime | None
    restricted_crop_last_violation: datetime | None
    restricted_crop_reason: str | None

    class Config:
        from_attributes = True


class ComplianceStatsResponse(BaseModel):
    """System-wide compliance statistics."""
    total_flagged_users: int
    total_violations: int
    deny_list_version: str
    violations_last_30_days: int


# Endpoints

@router.get("/flagged-users", response_model=List[FlaggedUserResponse])
def get_flagged_users(
    limit: int = Query(100, ge=1, le=500, description="Maximum number of users to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get list of users flagged for restricted plant violations.

    **Admin-only endpoint.**

    Returns users sorted by most recent violation first.
    """
    flagged_users = db.query(User).filter(
        User.restricted_crop_flag == True
    ).order_by(
        User.restricted_crop_last_violation.desc()
    ).limit(limit).offset(offset).all()

    return flagged_users


@router.get("/flagged-users/{user_id}", response_model=FlaggedUserResponse)
def get_flagged_user_details(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed compliance information for a specific user.

    **Admin-only endpoint.**

    Returns:
        Violation history and flag status for the user.

    Raises:
        404: User not found
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.get("/stats", response_model=ComplianceStatsResponse)
def get_compliance_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get system-wide compliance statistics.

    **Admin-only endpoint.**

    Returns:
        Aggregated compliance metrics and deny-list version.
    """
    from datetime import timedelta

    # Count flagged users
    total_flagged = db.query(User).filter(
        User.restricted_crop_flag == True
    ).count()

    # Sum total violations across all users
    from sqlalchemy import func
    total_violations = db.query(
        func.sum(User.restricted_crop_count)
    ).scalar() or 0

    # Count violations in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_violations = db.query(User).filter(
        User.restricted_crop_last_violation >= thirty_days_ago
    ).count()

    return ComplianceStatsResponse(
        total_flagged_users=total_flagged,
        total_violations=int(total_violations),
        deny_list_version=DENY_LIST_VERSION,
        violations_last_30_days=recent_violations
    )
