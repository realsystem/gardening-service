"""Password Reset Token model"""
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class PasswordResetToken(Base):
    """
    Password reset token for secure password recovery.

    Security features:
    - Tokens are hashed before storage (never store raw tokens)
    - Tokens expire after a configurable time (default: 1 hour)
    - Tokens can only be used once
    - One active token per user (new token invalidates old ones)
    """
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="password_reset_tokens")

    # Indexes for query performance
    __table_args__ = (
        Index('idx_user_active_tokens', 'user_id', 'used_at', 'expires_at'),
    )

    def is_valid(self) -> bool:
        """
        Check if token is still valid.

        A token is valid if:
        - It has not been used
        - It has not expired
        """
        now = datetime.utcnow()
        return self.used_at is None and self.expires_at > now

    def mark_as_used(self) -> None:
        """Mark token as used (prevents reuse)"""
        self.used_at = datetime.utcnow()

    @staticmethod
    def get_expiration_time(hours: int = 1) -> datetime:
        """
        Calculate token expiration time.

        Args:
            hours: Number of hours until expiration (default: 1)

        Returns:
            Expiration datetime
        """
        return datetime.utcnow() + timedelta(hours=hours)
