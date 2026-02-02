"""Production metrics collection using Prometheus format.

Provides:
- Request metrics (count, latency, error rate)
- Rule engine execution timing
- Compliance block counts
- Minimal performance impact (async counters, sampling)

Metrics are exposed at /metrics endpoint for scraping by Prometheus.
"""
import time
from typing import Callable, Optional
from functools import wraps
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
)
from starlette.responses import Response
from app.middleware.correlation_id import get_correlation_id


# Create a custom registry to avoid conflicts with other libraries
registry = CollectorRegistry()

# ============================================
# Request Metrics
# ============================================

# Total HTTP requests received
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

# HTTP request duration in seconds
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
    registry=registry
)

# HTTP requests currently in progress
http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently being processed',
    ['method', 'endpoint'],
    registry=registry
)

# HTTP errors by type
http_errors_total = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type'],
    registry=registry
)

# ============================================
# Rule Engine Metrics
# ============================================

# Rule evaluations performed
rule_evaluations_total = Counter(
    'rule_evaluations_total',
    'Total rule evaluations',
    ['rule_id', 'triggered'],
    registry=registry
)

# Rule execution time in seconds
rule_execution_duration_seconds = Histogram(
    'rule_execution_duration_seconds',
    'Rule execution time',
    ['rule_id'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=registry
)

# Rule engine batch execution time
rule_engine_batch_duration_seconds = Histogram(
    'rule_engine_batch_duration_seconds',
    'Rule engine batch execution time (all rules for a context)',
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    registry=registry
)

# Rules triggered (resulted in task/alert)
rules_triggered_total = Counter(
    'rules_triggered_total',
    'Total rules that triggered',
    ['rule_id', 'severity'],
    registry=registry
)

# ============================================
# Compliance Metrics
# ============================================

# Compliance checks performed
compliance_checks_total = Counter(
    'compliance_checks_total',
    'Total compliance checks',
    ['check_type', 'result'],
    registry=registry
)

# Compliance violations detected
compliance_violations_total = Counter(
    'compliance_violations_total',
    'Total compliance violations',
    ['violation_type', 'endpoint'],
    registry=registry
)

# Users flagged for compliance violations
compliance_users_flagged_total = Counter(
    'compliance_users_flagged_total',
    'Total users flagged for compliance violations',
    registry=registry
)

# Compliance blocks (403 responses)
compliance_blocks_total = Counter(
    'compliance_blocks_total',
    'Total requests blocked by compliance',
    ['endpoint'],
    registry=registry
)

# ============================================
# Database Metrics
# ============================================

# Database queries executed
db_queries_total = Counter(
    'db_queries_total',
    'Total database queries',
    ['operation'],  # SELECT, INSERT, UPDATE, DELETE
    registry=registry
)

# Database query duration
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query execution time',
    ['operation'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=registry
)

# ============================================
# Authentication Metrics
# ============================================

# Authentication attempts
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['result'],  # success, failure
    registry=registry
)

# Token validations
token_validations_total = Counter(
    'token_validations_total',
    'Total token validations',
    ['result'],  # valid, invalid, expired
    registry=registry
)

# ============================================
# Helper Functions
# ============================================

class MetricsCollector:
    """Helper class for collecting metrics with minimal performance impact."""

    @staticmethod
    def track_request(method: str, endpoint: str, status_code: int, duration: float):
        """Track HTTP request metrics.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: Endpoint path
            status_code: Response status code
            duration: Request duration in seconds
        """
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()

        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        # Track errors
        if status_code >= 400:
            error_type = 'client_error' if status_code < 500 else 'server_error'
            http_errors_total.labels(
                method=method,
                endpoint=endpoint,
                error_type=error_type
            ).inc()

    @staticmethod
    def track_rule_evaluation(rule_id: str, triggered: bool, duration: float, severity: Optional[str] = None):
        """Track rule evaluation metrics.

        Args:
            rule_id: Rule identifier
            triggered: Whether rule triggered
            duration: Execution duration in seconds
            severity: Rule severity if triggered
        """
        rule_evaluations_total.labels(
            rule_id=rule_id,
            triggered=str(triggered)
        ).inc()

        rule_execution_duration_seconds.labels(
            rule_id=rule_id
        ).observe(duration)

        if triggered and severity:
            rules_triggered_total.labels(
                rule_id=rule_id,
                severity=severity
            ).inc()

    @staticmethod
    def track_rule_engine_batch(duration: float):
        """Track rule engine batch execution.

        Args:
            duration: Batch execution duration in seconds
        """
        rule_engine_batch_duration_seconds.observe(duration)

    @staticmethod
    def track_compliance_check(check_type: str, blocked: bool):
        """Track compliance check.

        Args:
            check_type: Type of check (plant_name, notes, etc.)
            blocked: Whether request was blocked
        """
        result = 'blocked' if blocked else 'allowed'
        compliance_checks_total.labels(
            check_type=check_type,
            result=result
        ).inc()

    @staticmethod
    def track_compliance_violation(violation_type: str, endpoint: str):
        """Track compliance violation.

        Args:
            violation_type: Type of violation
            endpoint: Endpoint where violation occurred
        """
        compliance_violations_total.labels(
            violation_type=violation_type,
            endpoint=endpoint
        ).inc()

    @staticmethod
    def track_compliance_block(endpoint: str):
        """Track compliance block (403 response).

        Args:
            endpoint: Endpoint where block occurred
        """
        compliance_blocks_total.labels(
            endpoint=endpoint
        ).inc()

    @staticmethod
    def track_user_flagged():
        """Track user flagged for compliance violation."""
        compliance_users_flagged_total.inc()

    @staticmethod
    def track_db_query(operation: str, duration: float):
        """Track database query.

        Args:
            operation: SQL operation (SELECT, INSERT, UPDATE, DELETE)
            duration: Query duration in seconds
        """
        db_queries_total.labels(operation=operation).inc()
        db_query_duration_seconds.labels(operation=operation).observe(duration)

    @staticmethod
    def track_auth_attempt(success: bool):
        """Track authentication attempt.

        Args:
            success: Whether authentication succeeded
        """
        result = 'success' if success else 'failure'
        auth_attempts_total.labels(result=result).inc()

    @staticmethod
    def track_token_validation(result: str):
        """Track token validation.

        Args:
            result: Validation result (valid, invalid, expired)
        """
        token_validations_total.labels(result=result).inc()


def timing_metric(metric: Histogram, labels: Optional[dict] = None):
    """Decorator to measure function execution time.

    Args:
        metric: Histogram metric to record to
        labels: Optional labels for the metric

    Returns:
        Decorated function

    Example:
        @timing_metric(rule_execution_duration_seconds, {'rule_id': 'WATER_001'})
        def evaluate_rule(context):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)
        return wrapper
    return decorator


def get_metrics() -> Response:
    """Get current metrics in Prometheus format.

    Returns:
        Response with metrics in Prometheus text format
    """
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )
