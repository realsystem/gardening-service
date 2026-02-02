"""Structured logging configuration with JSON formatting and security controls.

Provides:
- JSON-formatted logs for easy parsing/aggregation
- Correlation ID injection
- Sensitive data redaction
- Environment-based log level enforcement
"""
import logging
import json
import sys
from typing import Any, Dict
from datetime import datetime

from app.middleware.correlation_id import get_correlation_id
from app.utils.log_redaction import RedactionFilter
from app.config import get_settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter with correlation ID and structured fields.

    Formats log records as JSON with:
    - timestamp (ISO 8601)
    - level (INFO, WARNING, ERROR, etc.)
    - logger name
    - message
    - correlation_id (for request tracing)
    - extra fields (if provided)
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        # Base log structure
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        # Add correlation ID if available
        correlation_id = get_correlation_id()
        if correlation_id:
            log_data['correlation_id'] = correlation_id

        # Add source location for non-INFO logs
        if record.levelno > logging.INFO:
            log_data['source'] = {
                'file': record.pathname,
                'line': record.lineno,
                'function': record.funcName
            }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
            }

        # Add extra fields (excluding built-in attributes)
        extra_fields = {
            k: v for k, v in record.__dict__.items()
            if k not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                        'levelname', 'levelno', 'lineno', 'module', 'msecs',
                        'pathname', 'process', 'processName', 'relativeCreated',
                        'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
                        'message', 'asctime']
        }

        if extra_fields:
            log_data['extra'] = extra_fields

        return json.dumps(log_data)


def configure_logging():
    """Configure application-wide structured logging.

    Sets up:
    - JSON formatting for all logs
    - Redaction filter for sensitive data
    - Environment-based log level (DEBUG disabled in production)
    - Correlation ID injection
    """
    settings = get_settings()

    # Determine log level based on environment
    if settings.APP_ENV == "production":
        # CRITICAL: No DEBUG logs in production
        log_level = logging.INFO
    elif settings.APP_ENV == "staging":
        log_level = logging.INFO
    else:
        # Development/testing
        log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(JSONFormatter())

    # Add redaction filter BEFORE formatting
    console_handler.addFilter(RedactionFilter())

    root_logger.addHandler(console_handler)

    # Configure third-party loggers to reduce noise
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.error').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

    # Create application logger
    app_logger = logging.getLogger('app')
    app_logger.setLevel(log_level)

    # Create compliance logger (separate for audit purposes)
    compliance_logger = logging.getLogger('compliance')
    compliance_logger.setLevel(logging.WARNING)  # Only log warnings/errors

    # Log configuration
    root_logger.info(
        "Logging configured",
        extra={
            'log_level': logging.getLevelName(log_level),
            'environment': settings.APP_ENV,
            'json_formatting': True,
            'redaction_enabled': True
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with proper configuration.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class SecurityLogger:
    """Specialized logger for security events.

    Provides methods for logging security-relevant events with
    appropriate severity levels and structured data.
    """

    def __init__(self, name: str = "security"):
        self.logger = logging.getLogger(name)

    def log_authentication_failure(
        self,
        user_email: str,
        reason: str,
        extra: Dict[str, Any] = None
    ):
        """Log authentication failure.

        Args:
            user_email: User email (will be redacted)
            reason: Failure reason
            extra: Additional context
        """
        log_data = {
            'event': 'authentication_failure',
            'user_email': user_email,  # Will be redacted by filter
            'reason': reason,
            'correlation_id': get_correlation_id()
        }

        if extra:
            log_data.update(extra)

        self.logger.warning("Authentication failed", extra=log_data)

    def log_authorization_failure(
        self,
        user_id: int,
        resource: str,
        action: str,
        extra: Dict[str, Any] = None
    ):
        """Log authorization failure.

        Args:
            user_id: User ID
            resource: Resource being accessed
            action: Action attempted
            extra: Additional context
        """
        log_data = {
            'event': 'authorization_failure',
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'correlation_id': get_correlation_id()
        }

        if extra:
            log_data.update(extra)

        self.logger.warning("Authorization failed", extra=log_data)

    def log_compliance_violation(
        self,
        user_id: int,
        violation_type: str,
        extra: Dict[str, Any] = None
    ):
        """Log compliance violation.

        Args:
            user_id: User ID
            violation_type: Type of violation
            extra: Additional context
        """
        log_data = {
            'event': 'compliance_violation',
            'user_id': user_id,
            'violation_type': violation_type,
            'correlation_id': get_correlation_id()
        }

        if extra:
            log_data.update(extra)

        self.logger.warning("Compliance violation", extra=log_data)

    def log_suspicious_activity(
        self,
        user_id: int,
        activity_type: str,
        details: str,
        extra: Dict[str, Any] = None
    ):
        """Log suspicious activity.

        Args:
            user_id: User ID
            activity_type: Type of activity
            details: Activity details
            extra: Additional context
        """
        log_data = {
            'event': 'suspicious_activity',
            'user_id': user_id,
            'activity_type': activity_type,
            'details': details,
            'correlation_id': get_correlation_id()
        }

        if extra:
            log_data.update(extra)

        self.logger.error("Suspicious activity detected", extra=log_data)
