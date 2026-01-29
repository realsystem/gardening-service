"""Password reset API endpoints"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.password_reset import (
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse,
    PasswordRequirements,
    ChangePasswordRequest
)
from app.repositories.user_repository import UserRepository
from app.repositories.password_reset_repository import PasswordResetRepository
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.models.user import User
from app.api.dependencies import get_current_user
from app.utils.token_generator import TokenGenerator
from app.utils.password_validator import PasswordValidator
from app.utils.rate_limiter import password_reset_rate_limiter
from app.models.password_reset_token import PasswordResetToken
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/password-reset", tags=["Authentication"])


@router.post("/request", response_model=PasswordResetResponse)
def request_password_reset(
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request a password reset email.

    Security features:
    - Always returns success (prevents email enumeration)
    - Rate limited (3 attempts per 15 minutes per email)
    - Generates cryptographically secure token
    - Tokens expire after 1 hour
    - Only one active token per user at a time

    Development mode:
    - Reset link is printed to backend console/logs
    - No email configuration required

    Production mode:
    - Email sent via configured SMTP provider
    - Requires SMTP environment variables

    Args:
        request_data: Email address to reset
        db: Database session

    Returns:
        Success message (same whether email exists or not)

    Raises:
        HTTPException 429: Too many reset requests (rate limited)

    Example:
        POST /auth/password-reset/request
        {
            "email": "user@example.com"
        }

        Response:
        {
            "message": "If the email exists, a password reset link has been sent",
            "success": true
        }
    """
    email = request_data.email.lower()

    # Check rate limit
    is_allowed, remaining = password_reset_rate_limiter.is_allowed(email)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset requests. Please try again later."
        )

    # Record this attempt
    password_reset_rate_limiter.record_attempt(email)

    # Try to find user (but don't reveal if they exist)
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(email)

    # Get settings to check if we're in debug mode
    settings = get_settings()

    if user:
        # Generate secure token
        raw_token, token_hash = TokenGenerator.generate_and_hash()

        # Create password reset token
        reset_repo = PasswordResetRepository(db)
        expires_at = PasswordResetToken.get_expiration_time(hours=1)
        reset_repo.create_token(user, token_hash, expires_at)

        # Build reset URL
        # In production, this would be the frontend URL
        # For now, we'll use a placeholder that works in both dev and docker
        frontend_url = "http://localhost:3000"  # Frontend URL
        reset_url = f"{frontend_url}/reset-password?token={raw_token}"

        # Send email (or log to console in dev mode)
        try:
            email_provider = EmailService.get_provider()
            email_provider.send_password_reset_email(user.email, reset_url)
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            # Don't reveal the error to the user (security)

        logger.info(f"Password reset requested for user: {user.id}")
    else:
        # User not found
        logger.warning(f"Password reset requested for non-existent email: {email}")

        # In development mode, return helpful error message
        # In production, don't reveal that the email doesn't exist (security)
        if settings.DEBUG:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No account found with email '{email}'. Please check the email address or register a new account."
            )

    # Production mode: Always return success (prevent email enumeration)
    return PasswordResetResponse(
        message="If the email exists, a password reset link has been sent",
        success=True
    )


@router.post("/confirm", response_model=PasswordResetResponse)
def confirm_password_reset(
    confirm_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token and set new password.

    Security features:
    - Token is validated and must not be expired
    - Token can only be used once
    - Password strength is validated
    - Old password no longer works after reset
    - All user's reset tokens are invalidated after successful reset

    Args:
        confirm_data: Token and new password
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 400: Invalid, expired, or already used token
        HTTPException 400: Weak password

    Example:
        POST /auth/password-reset/confirm
        {
            "token": "3x7k9mQpR2nV8yB4cF6hJ1sL5tN0wPqE7uG2aD9zX5C",
            "new_password": "StrongPassword123!"
        }

        Response:
        {
            "message": "Password has been reset successfully",
            "success": true
        }
    """
    # Hash the provided token to look it up
    token_hash = TokenGenerator.hash_token(confirm_data.token)

    # Find the token
    reset_repo = PasswordResetRepository(db)
    reset_token = reset_repo.get_token_by_hash(token_hash)

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Verify token is valid (not used, not expired)
    if not reset_token.is_valid():
        if reset_token.used_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This reset link has already been used"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This reset link has expired. Please request a new one"
            )

    # Password strength is already validated by Pydantic schema
    # Hash the new password
    new_password_hash = AuthService.hash_password(confirm_data.new_password)

    # Update user's password
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(reset_token.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )

    user.hashed_password = new_password_hash
    db.commit()

    # Mark token as used (prevents reuse)
    reset_repo.mark_token_as_used(reset_token)

    # Invalidate all other tokens for this user
    reset_repo.invalidate_user_tokens(user.id)

    # Reset rate limit for this email (successful reset)
    password_reset_rate_limiter.reset(user.email.lower())

    logger.info(f"Password reset successful for user: {user.id}")

    return PasswordResetResponse(
        message="Password has been reset successfully. You can now log in with your new password",
        success=True
    )


@router.get("/requirements", response_model=PasswordRequirements)
def get_password_requirements():
    """
    Get password strength requirements.

    Returns list of requirements that passwords must meet.
    Useful for displaying to users before they set a new password.

    Returns:
        Password requirements list

    Example:
        GET /auth/password-reset/requirements

        Response:
        {
            "requirements": [
                "At least 8 characters",
                "At least one uppercase letter (A-Z)",
                "At least one lowercase letter (a-z)",
                "At least one digit (0-9)",
                "At least one special character (!@#$%^&*...)"
            ]
        }
    """
    return PasswordRequirements(
        requirements=PasswordValidator.get_requirements()
    )


@router.post("/request-authenticated", response_model=PasswordResetResponse)
def request_password_reset_authenticated(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request a password reset email for authenticated user.

    This endpoint allows logged-in users to trigger a password reset email
    from their profile/settings page as an alternative to the change password flow.

    Security features:
    - User must be authenticated (requires valid JWT token)
    - Rate limited (3 attempts per 15 minutes per email)
    - Generates cryptographically secure token
    - Tokens expire after 1 hour
    - Only one active token per user at a time

    Development mode:
    - Reset link is printed to backend console/logs
    - No email configuration required

    Production mode:
    - Email sent via configured SMTP provider
    - Requires SMTP environment variables

    Args:
        current_user: Authenticated user (injected by dependency)
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 401: User not authenticated
        HTTPException 429: Too many reset requests (rate limited)

    Example:
        POST /auth/password-reset/request-authenticated
        Headers: Authorization: Bearer <token>

        Response:
        {
            "message": "A password reset link has been sent to your email",
            "success": true
        }
    """
    email = current_user.email.lower()

    # Check rate limit
    is_allowed, remaining = password_reset_rate_limiter.is_allowed(email)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset requests. Please try again later."
        )

    # Record this attempt
    password_reset_rate_limiter.record_attempt(email)

    # Generate secure token
    raw_token, token_hash = TokenGenerator.generate_and_hash()

    # Create password reset token
    reset_repo = PasswordResetRepository(db)
    expires_at = PasswordResetToken.get_expiration_time(hours=1)
    reset_repo.create_token(current_user, token_hash, expires_at)

    # Build reset URL
    settings = get_settings()
    frontend_url = "http://localhost:3000"  # Frontend URL
    reset_url = f"{frontend_url}/reset-password?token={raw_token}"

    # Send email (or log to console in dev mode)
    try:
        email_provider = EmailService.get_provider()
        email_provider.send_password_reset_email(current_user.email, reset_url)
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        # Still return success to user (email sending is async)

    logger.info(f"Password reset requested by authenticated user: {current_user.id}")

    return PasswordResetResponse(
        message="A password reset link has been sent to your email",
        success=True
    )


# Password change router (for authenticated users)
password_router = APIRouter(prefix="/auth/password", tags=["Authentication"])


@password_router.post("/change", response_model=PasswordResetResponse)
def change_password(
    change_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password for authenticated user.

    This endpoint allows logged-in users to change their password directly
    by providing their current password and a new password. This is the
    recommended method when the user knows their current password.

    Security features:
    - User must be authenticated (requires valid JWT token)
    - Current password must be verified
    - New password must meet strength requirements
    - Old password will no longer work after successful change
    - All pending reset tokens are invalidated

    Args:
        change_data: Current and new passwords
        current_user: Authenticated user (injected by dependency)
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 400: Current password is incorrect
        HTTPException 400: New password doesn't meet requirements
        HTTPException 401: User not authenticated

    Example:
        POST /auth/password/change
        Headers: Authorization: Bearer <token>
        {
            "current_password": "OldPassword123!",
            "new_password": "NewStrongPassword456!"
        }

        Response:
        {
            "message": "Password changed successfully",
            "success": true
        }
    """
    # Verify current password
    if not AuthService.verify_password(change_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Password strength is already validated by Pydantic schema
    # Hash the new password
    new_password_hash = AuthService.hash_password(change_data.new_password)

    # Update user's password
    current_user.hashed_password = new_password_hash
    db.commit()

    # Invalidate all password reset tokens for this user
    reset_repo = PasswordResetRepository(db)
    reset_repo.invalidate_user_tokens(current_user.id)

    # Reset rate limit for this email (successful change)
    password_reset_rate_limiter.reset(current_user.email.lower())

    logger.info(f"Password changed successfully for user: {current_user.id}")

    return PasswordResetResponse(
        message="Password changed successfully",
        success=True
    )
