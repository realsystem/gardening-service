"""Compliance service for restricted plant detection and audit logging.

This module handles:
- User flagging when violations occur
- Secure audit logging
- Pattern detection for evasive attempts
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
import hashlib
import json

from app.models.user import User
from app.compliance.deny_list import check_plant_restricted, get_user_facing_message, DENY_LIST_VERSION
from app.utils.metrics import MetricsCollector


class ComplianceService:
    """Service for handling compliance violations and audit logging."""

    def __init__(self, db: Session):
        self.db = db

    def flag_user_for_restricted_plant(
        self,
        user: User,
        violation_reason: str,
        request_metadata: dict = None
    ) -> None:
        """Flag a user for attempting to create a restricted plant.

        This is an immutable operation - flags are never removed, only incremented.

        Args:
            user: The User instance to flag
            violation_reason: Internal reason code (e.g., "restricted_term_in_common_name")
            request_metadata: Sanitized request metadata for audit log
        """
        now = datetime.utcnow()

        # Set first violation timestamp if this is the first time
        if not user.restricted_crop_flag:
            user.restricted_crop_first_violation = now

        # Always update these fields
        user.restricted_crop_flag = True
        user.restricted_crop_count = (user.restricted_crop_count or 0) + 1
        user.restricted_crop_last_violation = now
        user.restricted_crop_reason = violation_reason

        self.db.commit()

        # Track metrics for user flagging
        MetricsCollector.track_user_flagged()

        # Log the violation securely
        self._log_violation(
            user_id=user.id,
            user_email=user.email,
            violation_reason=violation_reason,
            request_metadata=request_metadata
        )

    def _log_violation(
        self,
        user_id: int,
        user_email: str,
        violation_reason: str,
        request_metadata: dict = None
    ) -> None:
        """Log compliance violation securely.

        Logs are written to application logger, NOT to database, to prevent
        user access to violation details.

        Args:
            user_id: User ID
            user_email: User email (for admin reference)
            violation_reason: Internal reason code
            request_metadata: Sanitized metadata (no plant parameters)
        """
        import logging
        logger = logging.getLogger("compliance")

        # Create a hash of the request for audit purposes (not full content)
        request_hash = self._hash_request(request_metadata) if request_metadata else "none"

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "user_email": user_email,
            "violation_reason": violation_reason,
            "deny_list_version": DENY_LIST_VERSION,
            "request_hash": request_hash,
            "event": "RESTRICTED_PLANT_ATTEMPT"
        }

        # Log at WARNING level (not ERROR - this is expected behavior)
        logger.warning(
            f"Compliance violation: {json.dumps(log_entry)}",
            extra={"compliance_event": True}
        )

    def _hash_request(self, request_metadata: dict) -> str:
        """Create a hash of request metadata for audit purposes.

        Args:
            request_metadata: Request metadata to hash

        Returns:
            SHA256 hash of metadata
        """
        # Sort keys for consistent hashing
        serialized = json.dumps(request_metadata, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]

    def check_and_enforce_plant_restriction(
        self,
        user: User,
        common_name: str = None,
        scientific_name: str = None,
        species: str = None,
        genus: str = None,
        notes: str = None,
        request_metadata: dict = None
    ) -> None:
        """Check if plant is restricted and enforce blocking if needed.

        Raises HTTPException if plant is restricted.

        Args:
            user: User attempting the operation
            common_name: Plant common name
            scientific_name: Plant scientific name
            species: Plant species
            genus: Plant genus
            notes: Plant notes
            request_metadata: Sanitized request metadata for logging

        Raises:
            HTTPException: 403 Forbidden if plant is restricted
        """
        from fastapi import HTTPException, status

        is_restricted, reason = check_plant_restricted(
            common_name=common_name,
            scientific_name=scientific_name,
            species=species,
            genus=genus,
            notes=notes
        )

        # Track compliance check metrics
        endpoint = request_metadata.get("endpoint", "unknown") if request_metadata else "unknown"
        MetricsCollector.track_compliance_check(
            check_type="plant_restriction",
            blocked=is_restricted
        )

        if is_restricted:
            # Track violation and block metrics
            MetricsCollector.track_compliance_violation(
                violation_type=reason,
                endpoint=endpoint
            )
            MetricsCollector.track_compliance_block(endpoint=endpoint)

            # Flag the user
            self.flag_user_for_restricted_plant(
                user=user,
                violation_reason=reason,
                request_metadata=request_metadata
            )

            # Block the request with generic message
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=get_user_facing_message()
            )

    def detect_parameter_only_optimization(
        self,
        user: User,
        garden_id: int,
        has_plantings: bool,
        request_metadata: dict = None
    ) -> None:
        """Detect suspicious parameter-only optimization attempts.

        Flags pattern where user requests nutrient optimization without any
        plantings (potential attempt to infer restricted plant parameters).

        Args:
            user: User making the request
            garden_id: Garden ID
            has_plantings: Whether garden has any plantings
            request_metadata: Request metadata for logging
        """
        from fastapi import HTTPException, status

        if not has_plantings:
            # Track suspicious pattern detection
            MetricsCollector.track_compliance_violation(
                violation_type="parameter_only_optimization_attempt",
                endpoint="nutrient_optimization"
            )
            MetricsCollector.track_compliance_block(endpoint="nutrient_optimization")

            # This is suspicious - requesting optimization with no plants
            # could be an attempt to reverse-engineer parameters
            self.flag_user_for_restricted_plant(
                user=user,
                violation_reason="parameter_only_optimization_attempt",
                request_metadata={
                    "garden_id": garden_id,
                    "endpoint": "nutrient_optimization",
                    "pattern": "no_plantings"
                }
            )

            # Block with generic message
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=get_user_facing_message()
            )


def get_compliance_service(db: Session) -> ComplianceService:
    """Factory function to create ComplianceService instance."""
    return ComplianceService(db)
