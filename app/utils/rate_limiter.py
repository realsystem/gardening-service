"""Simple in-memory rate limiter for password reset requests"""
from datetime import datetime, timedelta
from typing import Dict, Tuple
from collections import defaultdict
import threading


class RateLimiter:
    """
    In-memory rate limiter to prevent password reset abuse.

    Features:
    - Per-email rate limiting
    - Configurable time window and max attempts
    - Thread-safe
    - Automatic cleanup of old entries

    Default: Max 3 attempts per 15 minutes per email

    Note: This is an in-memory implementation. For production with multiple
    servers, consider using Redis or a distributed cache.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        window_minutes: int = 15
    ):
        """
        Initialize rate limiter.

        Args:
            max_attempts: Maximum attempts allowed within the time window
            window_minutes: Time window in minutes
        """
        self.max_attempts = max_attempts
        self.window_minutes = window_minutes
        # Store: {email: [(timestamp1, timestamp2, ...)]}
        self._attempts: Dict[str, list[datetime]] = defaultdict(list)
        self._lock = threading.Lock()

    def is_allowed(self, email: str) -> Tuple[bool, int]:
        """
        Check if a request is allowed for the given email.

        Args:
            email: Email address to check

        Returns:
            Tuple of (is_allowed, remaining_attempts)
            - is_allowed: True if request is allowed, False if rate limited
            - remaining_attempts: Number of attempts remaining (0 if rate limited)

        Example:
            allowed, remaining = rate_limiter.is_allowed("user@example.com")
            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many requests. Try again later."
                )
        """
        with self._lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(minutes=self.window_minutes)

            # Clean up old attempts (outside time window)
            if email in self._attempts:
                self._attempts[email] = [
                    timestamp for timestamp in self._attempts[email]
                    if timestamp > cutoff
                ]

            # Get current attempt count
            current_attempts = len(self._attempts[email])

            if current_attempts >= self.max_attempts:
                return False, 0

            remaining = self.max_attempts - current_attempts - 1
            return True, remaining

    def record_attempt(self, email: str) -> None:
        """
        Record a password reset attempt for an email.

        Args:
            email: Email address

        Example:
            if rate_limiter.is_allowed(email):
                rate_limiter.record_attempt(email)
                # Process reset request...
        """
        with self._lock:
            self._attempts[email].append(datetime.utcnow())

    def reset(self, email: str) -> None:
        """
        Reset rate limit for an email (clear all attempts).

        Args:
            email: Email address

        Example:
            # After successful password reset
            rate_limiter.reset(email)
        """
        with self._lock:
            if email in self._attempts:
                del self._attempts[email]

    def cleanup_old_entries(self, hours_old: int = 24) -> int:
        """
        Remove entries older than specified hours.

        This is a maintenance operation to prevent memory growth.

        Args:
            hours_old: Remove entries older than this many hours

        Returns:
            Number of emails cleaned up

        Example:
            # Run periodically
            cleaned = rate_limiter.cleanup_old_entries(hours_old=24)
            logger.info(f"Cleaned up {cleaned} old rate limit entries")
        """
        with self._lock:
            cutoff = datetime.utcnow() - timedelta(hours=hours_old)
            emails_to_remove = []

            for email, timestamps in self._attempts.items():
                # Filter out old timestamps
                recent_timestamps = [ts for ts in timestamps if ts > cutoff]

                if not recent_timestamps:
                    # No recent attempts, remove this email
                    emails_to_remove.append(email)
                else:
                    # Update with only recent timestamps
                    self._attempts[email] = recent_timestamps

            # Remove emails with no recent attempts
            for email in emails_to_remove:
                del self._attempts[email]

            return len(emails_to_remove)


# Global rate limiter instance
# 3 attempts per 15 minutes per email
password_reset_rate_limiter = RateLimiter(max_attempts=3, window_minutes=15)
