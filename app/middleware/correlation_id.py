"""Correlation ID middleware for request tracing.

Adds unique correlation ID to each request for log aggregation and tracing.
"""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from contextvars import ContextVar

# Context variable to store correlation ID for the current request
correlation_id_context: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation ID to each request.

    Generates a unique UUID for each request and:
    - Stores it in context variable for access throughout request lifecycle
    - Adds it to response headers for client-side tracing
    - Makes it available for logging

    If client provides X-Correlation-ID header, that value is used instead.
    """

    async def dispatch(self, request: Request, call_next):
        # Get correlation ID from header or generate new one
        correlation_id = request.headers.get("X-Correlation-ID")

        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Set in context for access in logging
        correlation_id_context.set(correlation_id)

        # Add to request state for access in endpoints
        request.state.correlation_id = correlation_id

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response


def get_correlation_id() -> str:
    """Get the current request's correlation ID.

    Returns:
        Correlation ID string, or empty string if not in request context
    """
    return correlation_id_context.get()
