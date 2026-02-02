"""Security headers middleware for production security hardening.

Implements security headers to protect against:
- XSS (Cross-Site Scripting)
- Clickjacking
- MIME type sniffing
- Information leakage

References:
- OWASP Secure Headers Project
- Mozilla Web Security Guidelines
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all HTTP responses.

    Headers added:
    - X-Content-Type-Options: nosniff (prevent MIME sniffing)
    - X-Frame-Options: DENY (prevent clickjacking)
    - X-XSS-Protection: 1; mode=block (legacy XSS protection)
    - Strict-Transport-Security: enforce HTTPS (production only)
    - Content-Security-Policy: prevent XSS attacks
    - Referrer-Policy: control referrer information
    - Permissions-Policy: control browser features
    """

    def __init__(self, app, env: str = "local"):
        super().__init__(app)
        self.env = env
        self.is_production = env in ("production", "staging")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # X-Content-Type-Options: Prevent MIME type sniffing
        # Ensures browsers respect the Content-Type header
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: Prevent clickjacking attacks
        # DENY prevents the page from being displayed in a frame/iframe
        response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection: Legacy XSS filter (for older browsers)
        # Modern browsers use CSP instead, but this provides defense-in-depth
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Strict-Transport-Security (HSTS): Force HTTPS
        # Only add in production/staging (requires HTTPS to be meaningful)
        if self.is_production:
            # max-age=31536000 = 1 year
            # includeSubDomains applies to all subdomains
            # preload allows inclusion in browser HSTS preload lists
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Content-Security-Policy (CSP): Prevent XSS and data injection
        # This is a strict policy for an API-only service
        csp_directives = [
            "default-src 'none'",  # Block all content by default
            "frame-ancestors 'none'",  # Prevent embedding (redundant with X-Frame-Options)
            "base-uri 'none'",  # Prevent <base> tag injection
            "form-action 'none'",  # API doesn't serve forms
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Referrer-Policy: Control referrer information leakage
        # no-referrer prevents leaking URL information to external sites
        response.headers["Referrer-Policy"] = "no-referrer"

        # Permissions-Policy (formerly Feature-Policy): Control browser features
        # Disable all features that an API doesn't need
        permissions = [
            "geolocation=()",  # No geolocation
            "microphone=()",   # No microphone access
            "camera=()",       # No camera access
            "payment=()",      # No payment API
            "usb=()",          # No USB access
            "magnetometer=()", # No magnetometer
            "gyroscope=()",    # No gyroscope
            "accelerometer=()",# No accelerometer
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions)

        # Remove server header to avoid information disclosure
        # Many frameworks add this by default
        if "Server" in response.headers:
            del response.headers["Server"]

        # Log security headers application in production
        if self.is_production and request.url.path not in ["/health", "/metrics"]:
            logger.debug(
                f"Security headers applied to {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client": request.client.host if request.client else None,
                }
            )

        return response
