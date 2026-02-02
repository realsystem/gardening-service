"""Middleware to collect request metrics with minimal performance impact.

Tracks:
- Request count by endpoint and status code
- Request latency (p50, p95, p99)
- Requests in progress (concurrent requests)
- Error rates

Performance optimizations:
- Uses efficient Prometheus counters/histograms
- No blocking operations
- Minimal memory overhead
"""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.utils.metrics import MetricsCollector, http_requests_in_progress


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP request metrics.

    Measures request duration and tracks success/error rates.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip metrics endpoint itself to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        # Get endpoint pattern (not full path with IDs)
        endpoint = self._get_endpoint_pattern(request)
        method = request.method

        # Track in-progress requests
        http_requests_in_progress.labels(
            method=method,
            endpoint=endpoint
        ).inc()

        start_time = time.time()
        status_code = 500  # Default in case of exception

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response

        except Exception as e:
            # Track uncaught exceptions
            status_code = 500
            raise

        finally:
            # Calculate duration
            duration = time.time() - start_time

            # Decrement in-progress counter
            http_requests_in_progress.labels(
                method=method,
                endpoint=endpoint
            ).dec()

            # Track request metrics
            MetricsCollector.track_request(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration=duration
            )

    @staticmethod
    def _get_endpoint_pattern(request: Request) -> str:
        """Extract endpoint pattern from request.

        Converts /users/123 -> /users/{id}
        to avoid high cardinality in metrics.

        Args:
            request: HTTP request

        Returns:
            Endpoint pattern string
        """
        # Try to get route pattern from FastAPI
        if hasattr(request, 'scope') and 'route' in request.scope:
            route = request.scope['route']
            if hasattr(route, 'path'):
                return route.path

        # Fallback: simple pattern matching for common cases
        path = request.url.path

        # Replace numeric IDs with {id}
        import re
        path = re.sub(r'/\d+(/|$)', r'/{id}\1', path)

        # Replace UUIDs with {uuid}
        path = re.sub(
            r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(/|$)',
            r'/{uuid}\1',
            path,
            flags=re.IGNORECASE
        )

        return path
