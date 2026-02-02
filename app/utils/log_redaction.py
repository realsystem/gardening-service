"""Log redaction utilities to prevent sensitive data leakage.

Filters and redacts sensitive information from logs including:
- Email addresses
- JWT tokens
- Passwords
- API keys
- Plant variety names (compliance requirement)
- User IDs in certain contexts
"""
import re
import logging
from typing import Any, Dict


class SensitiveDataRedactor:
    """Redacts sensitive information from log messages and extra data."""

    # Patterns for sensitive data detection
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    JWT_PATTERN = re.compile(r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}')
    UUID_PATTERN = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.IGNORECASE)
    API_KEY_PATTERN = re.compile(r'(api[_-]?key|secret|token)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})', re.IGNORECASE)

    # Sensitive field names that should be redacted
    SENSITIVE_FIELDS = {
        'password',
        'hashed_password',
        'access_token',
        'refresh_token',
        'token',
        'secret',
        'api_key',
        'authorization',
        'cookie',
        'session',
        'csrf_token',
        'common_name',  # Plant names (compliance)
        'scientific_name',  # Plant names (compliance)
        'plant_notes',  # May contain plant names
        'notes',  # May contain sensitive info
    }

    # Sensitive header names
    SENSITIVE_HEADERS = {
        'authorization',
        'cookie',
        'x-api-key',
        'x-auth-token',
    }

    @staticmethod
    def redact_string(value: str) -> str:
        """Redact sensitive patterns from a string.

        Args:
            value: String to redact

        Returns:
            Redacted string with sensitive data replaced
        """
        if not isinstance(value, str):
            return value

        # Redact emails
        value = SensitiveDataRedactor.EMAIL_PATTERN.sub('[EMAIL_REDACTED]', value)

        # Redact JWT tokens
        value = SensitiveDataRedactor.JWT_PATTERN.sub('[TOKEN_REDACTED]', value)

        # Redact API keys in key=value format
        value = SensitiveDataRedactor.API_KEY_PATTERN.sub(r'\1=[KEY_REDACTED]', value)

        return value

    @staticmethod
    def redact_dict(data: Dict[str, Any], redact_uuids: bool = False) -> Dict[str, Any]:
        """Redact sensitive fields from a dictionary.

        Args:
            data: Dictionary to redact
            redact_uuids: Whether to redact UUIDs (False for correlation IDs)

        Returns:
            New dictionary with sensitive fields redacted
        """
        if not isinstance(data, dict):
            return data

        redacted = {}
        for key, value in data.items():
            key_lower = key.lower()

            # Redact known sensitive fields
            if key_lower in SensitiveDataRedactor.SENSITIVE_FIELDS:
                redacted[key] = '[REDACTED]'
            # Recursively redact nested dicts
            elif isinstance(value, dict):
                redacted[key] = SensitiveDataRedactor.redact_dict(value, redact_uuids)
            # Recursively redact lists
            elif isinstance(value, list):
                redacted[key] = [
                    SensitiveDataRedactor.redact_dict(item, redact_uuids) if isinstance(item, dict)
                    else SensitiveDataRedactor.redact_string(str(item)) if isinstance(item, str)
                    else item
                    for item in value
                ]
            # Redact string values
            elif isinstance(value, str):
                redacted_value = SensitiveDataRedactor.redact_string(value)
                # Optionally redact UUIDs (but not correlation IDs)
                if redact_uuids and key_lower != 'correlation_id':
                    redacted_value = SensitiveDataRedactor.UUID_PATTERN.sub('[UUID_REDACTED]', redacted_value)
                redacted[key] = redacted_value
            else:
                redacted[key] = value

        return redacted

    @staticmethod
    def redact_headers(headers: Dict[str, str]) -> Dict[str, str]:
        """Redact sensitive HTTP headers.

        Args:
            headers: HTTP headers dictionary

        Returns:
            Redacted headers dictionary
        """
        redacted = {}
        for key, value in headers.items():
            if key.lower() in SensitiveDataRedactor.SENSITIVE_HEADERS:
                redacted[key] = '[REDACTED]'
            else:
                redacted[key] = value

        return redacted


class RedactionFilter(logging.Filter):
    """Logging filter to redact sensitive information from log records.

    This filter intercepts log records before they're written and:
    - Redacts sensitive patterns from the message
    - Redacts sensitive fields from extra data
    - Prevents accidental logging of PII/credentials

    Usage:
        handler = logging.StreamHandler()
        handler.addFilter(RedactionFilter())
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record to redact sensitive data.

        Args:
            record: Log record to filter

        Returns:
            True (always - we redact but don't drop logs)
        """
        # Redact message string
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = SensitiveDataRedactor.redact_string(record.msg)

        # Redact arguments
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, dict):
                record.args = SensitiveDataRedactor.redact_dict(record.args)
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(
                    SensitiveDataRedactor.redact_string(str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )

        # Redact extra fields
        for attr in list(record.__dict__.keys()):
            if attr not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                           'levelname', 'levelno', 'lineno', 'module', 'msecs',
                           'pathname', 'process', 'processName', 'relativeCreated',
                           'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
                           'correlation_id']:  # Don't redact correlation ID
                value = getattr(record, attr)
                if isinstance(value, str):
                    setattr(record, attr, SensitiveDataRedactor.redact_string(value))
                elif isinstance(value, dict):
                    setattr(record, attr, SensitiveDataRedactor.redact_dict(value))

        return True
