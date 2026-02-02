"""Rate limiting middleware for API protection.

Protects against:
- Brute force authentication attacks
- API abuse
- Denial of Service (DoS)

Features:
- Per-IP rate limiting
- Different limits for authenticated vs unauthenticated requests
- Stricter limits for authentication endpoints
- Redis support for multi-server deployments (future)
- Configurable limits via environment
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from typing import Callable
from datetime import datetime, timedelta
from collections import defaultdict
import threading
import logging

logger = logging.getLogger(__name__)


class InMemoryRateLimiter:
    """
    In-memory rate limiter for single-server deployments.

    For production with multiple servers, replace with Redis-backed implementation.
    """

    def __init__(self):
        self._requests: dict[str, list[datetime]] = defaultdict(list)
        self._lock = threading.Lock()

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> tuple[bool, int]:
        """
        Check if request is allowed.

        Args:
            key: Unique key for rate limiting (e.g., IP address)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            (is_allowed, retry_after_seconds)
        """
        with self._lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=window_seconds)

            # Clean up old requests
            if key in self._requests:
                self._requests[key] = [
                    timestamp for timestamp in self._requests[key]
                    if timestamp > cutoff
                ]

            current_count = len(self._requests[key])

            if current_count >= max_requests:
                # Calculate retry-after (time until oldest request expires)
                if self._requests[key]:
                    oldest = self._requests[key][0]
                    retry_after = int((oldest - cutoff).total_seconds())
                    return False, retry_after
                return False, window_seconds

            # Record this request
            self._requests[key].append(now)
            return True, 0

    def cleanup_old_entries(self, hours_old: int = 24) -> int:
        """Remove entries older than specified hours."""
        with self._lock:
            cutoff = datetime.utcnow() - timedelta(hours=hours_old)
            keys_to_remove = []

            for key, timestamps in self._requests.items():
                recent = [ts for ts in timestamps if ts > cutoff]
                if not recent:
                    keys_to_remove.append(key)
                else:
                    self._requests[key] = recent

            for key in keys_to_remove:
                del self._requests[key]

            return len(keys_to_remove)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with configurable limits per endpoint type.

    Rate Limits (requests per minute):
    - Authentication endpoints: 5 requests/min (brute force protection)
    - Unauthenticated API: 60 requests/min (abuse protection)
    - Authenticated API: 300 requests/min (generous for legitimate use)
    - Health/metrics: Unlimited (monitoring should not be rate limited)
    """

    # Rate limits: (max_requests, window_seconds)
    AUTH_LIMIT = (5, 60)  # 5 requests per minute for auth endpoints
    UNAUTH_LIMIT = (60, 60)  # 60 requests per minute for unauthenticated
    AUTH_API_LIMIT = (300, 60)  # 300 requests per minute for authenticated

    # Authentication endpoints (stricter limits)
    AUTH_ENDPOINTS = [
        "/token",
        "/users/register",
        "/password-reset/request",
        "/password-reset/reset",
    ]

    # Endpoints exempt from rate limiting
    EXEMPT_ENDPOINTS = [
        "/health",
        "/metrics",
        "/docs",
        "/openapi.json",
    ]

    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
        self.limiter = InMemoryRateLimiter()
        logger.info(f"Rate limiting {'enabled' if enabled else 'disabled'}")

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        # Check X-Forwarded-For header (for proxied requests)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take first IP in chain
            return forwarded.split(",")[0].strip()

        # Fallback to direct connection
        if request.client:
            return request.client.host

        return "unknown"

    def _is_authenticated(self, request: Request) -> bool:
        """Check if request has valid authentication token."""
        auth_header = request.headers.get("Authorization", "")
        return auth_header.startswith("Bearer ")

    def _get_rate_limit(self, request: Request) -> tuple[int, int]:
        """
        Determine rate limit for request.

        Returns:
            (max_requests, window_seconds)
        """
        path = request.url.path

        # Exempt endpoints (no limit)
        if any(path.startswith(exempt) for exempt in self.EXEMPT_ENDPOINTS):
            return (999999, 60)  # Effectively unlimited

        # Strict limit for authentication endpoints
        if any(path.startswith(auth_ep) for auth_ep in self.AUTH_ENDPOINTS):
            return self.AUTH_LIMIT

        # Authenticated requests get higher limit
        if self._is_authenticated(request):
            return self.AUTH_API_LIMIT

        # Unauthenticated requests get lower limit
        return self.UNAUTH_LIMIT

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting to request."""
        # Skip if disabled
        if not self.enabled:
            return await call_next(request)

        # Get client identifier
        client_ip = self._get_client_ip(request)

        # Get rate limit for this request
        max_requests, window_seconds = self._get_rate_limit(request)

        # Check rate limit
        rate_limit_key = f"{client_ip}:{request.url.path}"
        allowed, retry_after = self.limiter.is_allowed(
            rate_limit_key,
            max_requests,
            window_seconds
        )

        if not allowed:
            # Rate limit exceeded
            logger.warning(
                f"Rate limit exceeded for {client_ip} on {request.url.path}",
                extra={
                    "client_ip": client_ip,
                    "path": request.url.path,
                    "method": request.method,
                    "retry_after": retry_after,
                }
            )

            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Reset": str(window_seconds),
                }
            )

        # Request allowed - proceed
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max_requests - len(self.limiter._requests.get(rate_limit_key, [])))

        return response
