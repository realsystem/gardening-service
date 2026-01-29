"""Repository for password reset token operations"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User


class PasswordResetRepository:
    """
    Repository for managing password reset tokens.

    Handles:
    - Creating new reset tokens
    - Finding tokens by hash
    - Invalidating old tokens for a user
    - Cleaning up expired tokens
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create_token(
        self,
        user: User,
        token_hash: str,
        expires_at: datetime
    ) -> PasswordResetToken:
        """
        Create a new password reset token for a user.

        Also invalidates any existing active tokens for this user.

        Args:
            user: User object
            token_hash: Hashed token value
            expires_at: Expiration datetime

        Returns:
            Created PasswordResetToken object

        Example:
            from app.utils.token_generator import TokenGenerator

            raw_token, token_hash = TokenGenerator.generate_and_hash()
            expires_at = PasswordResetToken.get_expiration_time(hours=1)
            reset_token = repo.create_token(user, token_hash, expires_at)
        """
        # Invalidate any existing active tokens for this user
        self.invalidate_user_tokens(user.id)

        # Create new token
        token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )

        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)

        return token

    def get_token_by_hash(self, token_hash: str) -> Optional[PasswordResetToken]:
        """
        Find a password reset token by its hash.

        Args:
            token_hash: Hashed token value

        Returns:
            PasswordResetToken object if found, None otherwise

        Example:
            from app.utils.token_generator import TokenGenerator

            user_token = request.form['token']
            token_hash = TokenGenerator.hash_token(user_token)
            reset_token = repo.get_token_by_hash(token_hash)
        """
        return self.db.query(PasswordResetToken).filter(
            PasswordResetToken.token_hash == token_hash
        ).first()

    def invalidate_user_tokens(self, user_id: int) -> None:
        """
        Invalidate all active tokens for a user.

        Marks all unused tokens as used to prevent their use.
        Called when:
        - User requests a new reset token
        - User successfully resets password
        - Admin invalidates user tokens

        Args:
            user_id: User ID

        Example:
            repo.invalidate_user_tokens(user.id)
        """
        now = datetime.utcnow()
        self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None)
        ).update({
            'used_at': now
        })
        self.db.commit()

    def mark_token_as_used(self, token: PasswordResetToken) -> None:
        """
        Mark a token as used to prevent reuse.

        Args:
            token: PasswordResetToken object

        Example:
            if token.is_valid():
                repo.mark_token_as_used(token)
                # Reset password...
        """
        token.mark_as_used()
        self.db.commit()

    def cleanup_expired_tokens(self, days_old: int = 7) -> int:
        """
        Delete expired password reset tokens older than specified days.

        This is a maintenance operation to keep the database clean.
        Should be run periodically (e.g., daily cron job).

        Args:
            days_old: Delete tokens older than this many days (default: 7)

        Returns:
            Number of tokens deleted

        Example:
            # Delete tokens older than 7 days
            deleted_count = repo.cleanup_expired_tokens(days_old=7)
            logger.info(f"Cleaned up {deleted_count} expired tokens")
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        deleted = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.created_at < cutoff_date
        ).delete()

        self.db.commit()
        return deleted

    def get_active_token_for_user(self, user_id: int) -> Optional[PasswordResetToken]:
        """
        Get the active (unused, unexpired) token for a user.

        Args:
            user_id: User ID

        Returns:
            PasswordResetToken object if active token exists, None otherwise

        Example:
            active_token = repo.get_active_token_for_user(user.id)
            if active_token:
                print(f"Token expires at: {active_token.expires_at}")
        """
        now = datetime.utcnow()
        return self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > now
        ).first()
