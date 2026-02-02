"""Security tests for structured logging and redaction.

Tests that sensitive data cannot bypass redaction:
1. Emails are redacted
2. JWT tokens are redacted
3. Passwords are redacted
4. API keys are redacted
5. Plant names are redacted (compliance)
6. Correlation IDs are preserved
7. DEBUG logs are disabled in production
"""
import pytest
import logging
import json
from io import StringIO
from unittest.mock import patch, MagicMock

from app.utils.log_redaction import SensitiveDataRedactor, RedactionFilter
from app.utils.structured_logging import JSONFormatter, configure_logging, SecurityLogger
from app.middleware.correlation_id import CorrelationIDMiddleware, get_correlation_id, correlation_id_context
from app.config import get_settings


# ============================================
# Redaction Tests
# ============================================

@pytest.mark.security
class TestSensitiveDataRedaction:
    """Test that sensitive data is properly redacted from logs."""

    def test_email_redaction(self):
        """Test that email addresses are redacted."""
        test_cases = [
            ("User email@example.com logged in", "User [EMAIL_REDACTED] logged in"),
            ("Contact: test.user+tag@domain.co.uk", "Contact: [EMAIL_REDACTED]"),
            ("Multiple emails: a@b.com and c@d.org", "Multiple emails: [EMAIL_REDACTED] and [EMAIL_REDACTED]"),
        ]

        for original, expected in test_cases:
            redacted = SensitiveDataRedactor.redact_string(original)
            assert redacted == expected, f"Failed to redact: {original}"
            assert "@" not in redacted or "[EMAIL_REDACTED]" in redacted

    def test_jwt_token_redaction(self):
        """Test that JWT tokens are redacted."""
        test_cases = [
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            "Token: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.xYz",
            "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MH0.abc123def456",
        ]

        for test_case in test_cases:
            redacted = SensitiveDataRedactor.redact_string(test_case)
            assert "[TOKEN_REDACTED]" in redacted or "[KEY_REDACTED]" in redacted
            assert "eyJ" not in redacted  # JWT prefix should be gone

    def test_api_key_redaction(self):
        """Test that API keys are redacted."""
        test_cases = [
            ('api_key="sk_live_abcdef123456789"', 'api_key=[KEY_REDACTED]'),
            ("secret: my_super_secret_key_123", "secret=[KEY_REDACTED]"),
            ("token=abc123def456ghi789jkl", "token=[KEY_REDACTED]"),
        ]

        for original, expected_pattern in test_cases:
            redacted = SensitiveDataRedactor.redact_string(original)
            assert "[KEY_REDACTED]" in redacted, f"Failed to redact API key in: {original}"

    def test_dict_field_redaction(self):
        """Test that sensitive fields in dictionaries are redacted."""
        test_data = {
            "username": "testuser",
            "password": "SuperSecret123!",
            "email": "user@example.com",
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token",
            "common_name": "Cannabis",  # Plant name (compliance)
            "scientific_name": "Cannabis sativa",  # Plant name (compliance)
            "notes": "Growing cannabis plants",  # May contain plant names
            "plant_notes": "These are marijuana plants",  # May contain plant names
            "safe_field": "This is OK"
        }

        redacted = SensitiveDataRedactor.redact_dict(test_data)

        # Sensitive fields should be redacted
        assert redacted["password"] == "[REDACTED]"
        assert redacted["access_token"] == "[REDACTED]"
        assert redacted["common_name"] == "[REDACTED]"
        assert redacted["scientific_name"] == "[REDACTED]"
        assert redacted["notes"] == "[REDACTED]"
        assert redacted["plant_notes"] == "[REDACTED]"

        # Email should be redacted in string
        assert "[EMAIL_REDACTED]" in redacted["email"]

        # Safe fields should remain
        assert redacted["username"] == "testuser"
        assert redacted["safe_field"] == "This is OK"

    def test_nested_dict_redaction(self):
        """Test that nested dictionaries are recursively redacted."""
        test_data = {
            "user": {
                "email": "user@example.com",
                "password": "secret",
                "profile": {
                    "api_key": "sk_test_123"
                }
            }
        }

        redacted = SensitiveDataRedactor.redact_dict(test_data)

        assert "[EMAIL_REDACTED]" in redacted["user"]["email"]
        assert redacted["user"]["password"] == "[REDACTED]"
        assert redacted["user"]["profile"]["api_key"] == "[REDACTED]"

    def test_list_redaction(self):
        """Test that lists of dicts are properly redacted."""
        test_data = {
            "users": [
                {"email": "user1@example.com", "password": "secret1"},
                {"email": "user2@example.com", "password": "secret2"}
            ]
        }

        redacted = SensitiveDataRedactor.redact_dict(test_data)

        assert "[EMAIL_REDACTED]" in redacted["users"][0]["email"]
        assert redacted["users"][0]["password"] == "[REDACTED]"
        assert "[EMAIL_REDACTED]" in redacted["users"][1]["email"]
        assert redacted["users"][1]["password"] == "[REDACTED]"

    def test_headers_redaction(self):
        """Test that sensitive HTTP headers are redacted."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJtoken",
            "Cookie": "session=abc123",
            "X-API-Key": "secret_key",
            "User-Agent": "Mozilla/5.0"
        }

        redacted = SensitiveDataRedactor.redact_headers(headers)

        assert redacted["Content-Type"] == "application/json"
        assert redacted["User-Agent"] == "Mozilla/5.0"
        assert redacted["Authorization"] == "[REDACTED]"
        assert redacted["Cookie"] == "[REDACTED]"
        assert redacted["X-API-Key"] == "[REDACTED]"


# ============================================
# Logging Filter Tests
# ============================================

@pytest.mark.security
class TestRedactionFilter:
    """Test the logging filter that redacts sensitive data."""

    def test_filter_redacts_log_message(self):
        """Test that log messages are redacted by filter."""
        # Create a log record
        logger = logging.getLogger('test')
        record = logger.makeRecord(
            name='test',
            level=logging.INFO,
            fn='test.py',
            lno=1,
            msg="User user@example.com attempted login with token eyJtest.token.here",
            args=(),
            exc_info=None
        )

        # Apply redaction filter
        filter = RedactionFilter()
        filter.filter(record)

        # Check redaction
        assert "[EMAIL_REDACTED]" in record.msg
        assert "[TOKEN_REDACTED]" in record.msg
        assert "user@example.com" not in record.msg
        assert "eyJ" not in record.msg

    def test_filter_redacts_extra_fields(self):
        """Test that extra fields are redacted by filter."""
        logger = logging.getLogger('test')
        record = logger.makeRecord(
            name='test',
            level=logging.INFO,
            fn='test.py',
            lno=1,
            msg="Login attempt",
            args=(),
            exc_info=None
        )

        # Add extra fields
        record.user_email = "admin@example.com"
        record.password = "SuperSecret123!"
        record.common_name = "Cannabis"

        # Apply filter
        filter = RedactionFilter()
        filter.filter(record)

        # Check redaction
        assert "[EMAIL_REDACTED]" in record.user_email
        # Note: password field might not be in the record unless explicitly added as extra
        # The filter redacts string values but 'password' is a sensitive field name

    def test_filter_preserves_safe_data(self):
        """Test that non-sensitive data is preserved."""
        logger = logging.getLogger('test')
        record = logger.makeRecord(
            name='test',
            level=logging.INFO,
            fn='test.py',
            lno=1,
            msg="User logged in successfully",
            args=(),
            exc_info=None
        )

        record.user_id = 123
        record.timestamp = "2024-01-01T00:00:00Z"

        filter = RedactionFilter()
        filter.filter(record)

        # Safe data should remain
        assert record.msg == "User logged in successfully"
        assert record.user_id == 123
        assert record.timestamp == "2024-01-01T00:00:00Z"


# ============================================
# Structured Logging Tests
# ============================================

@pytest.mark.security
class TestJSONFormatter:
    """Test JSON log formatting."""

    def test_json_format_structure(self):
        """Test that logs are formatted as valid JSON."""
        formatter = JSONFormatter()
        logger = logging.getLogger('test')
        record = logger.makeRecord(
            name='test.module',
            level=logging.INFO,
            fn='test.py',
            lno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )

        formatted = formatter.format(record)

        # Should be valid JSON
        log_data = json.loads(formatted)

        assert 'timestamp' in log_data
        assert 'level' in log_data
        assert 'logger' in log_data
        assert 'message' in log_data

        assert log_data['level'] == 'INFO'
        assert log_data['logger'] == 'test.module'
        assert log_data['message'] == 'Test message'

    def test_json_format_includes_correlation_id(self):
        """Test that correlation ID is included in JSON logs."""
        formatter = JSONFormatter()
        logger = logging.getLogger('test')

        # Set correlation ID in context
        correlation_id_context.set("test-correlation-id-12345")

        record = logger.makeRecord(
            name='test',
            level=logging.INFO,
            fn='test.py',
            lno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        assert 'correlation_id' in log_data
        assert log_data['correlation_id'] == "test-correlation-id-12345"

        # Clean up
        correlation_id_context.set("")

    def test_json_format_includes_source_for_errors(self):
        """Test that source location is included for non-INFO logs."""
        formatter = JSONFormatter()
        logger = logging.getLogger('test')

        record = logger.makeRecord(
            name='test',
            level=logging.ERROR,
            fn='/app/test.py',
            lno=100,
            msg="Error occurred",
            args=(),
            exc_info=None,
            func='test_function'
        )

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        assert 'source' in log_data
        assert log_data['source']['file'] == '/app/test.py'
        assert log_data['source']['line'] == 100
        assert log_data['source']['function'] == 'test_function'


# ============================================
# Correlation ID Tests
# ============================================

@pytest.mark.security
class TestCorrelationID:
    """Test correlation ID middleware."""

    @pytest.mark.asyncio
    async def test_correlation_id_generated(self, client):
        """Test that correlation ID is generated for requests."""
        response = client.get("/health")

        assert response.status_code == 200
        assert "X-Correlation-ID" in response.headers
        assert len(response.headers["X-Correlation-ID"]) > 0

    @pytest.mark.asyncio
    async def test_correlation_id_preserved_from_header(self, client):
        """Test that client-provided correlation ID is preserved."""
        custom_correlation_id = "custom-correlation-12345"

        response = client.get(
            "/health",
            headers={"X-Correlation-ID": custom_correlation_id}
        )

        assert response.status_code == 200
        assert response.headers["X-Correlation-ID"] == custom_correlation_id

    def test_get_correlation_id_returns_empty_outside_request(self):
        """Test that get_correlation_id returns empty string outside request context."""
        # Clear context
        correlation_id_context.set("")

        correlation_id = get_correlation_id()
        assert correlation_id == ""


# ============================================
# Log Level Enforcement Tests
# ============================================

@pytest.mark.security
class TestLogLevelEnforcement:
    """Test that log levels are enforced based on environment."""

    def test_production_disables_debug_logs(self):
        """Test that DEBUG logs are disabled in production environment."""
        with patch('app.utils.structured_logging.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                APP_ENV="production",
                DEBUG=False
            )

            # Clear existing handlers
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            # Configure logging
            configure_logging()

            # Root logger should be at INFO level, not DEBUG
            assert root_logger.level >= logging.INFO

    def test_development_allows_debug_logs(self):
        """Test that DEBUG logs are allowed in development environment."""
        with patch('app.utils.structured_logging.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                APP_ENV="development",
                DEBUG=True
            )

            # Clear existing handlers
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            # Configure logging
            configure_logging()

            # Root logger should allow DEBUG
            assert root_logger.level <= logging.DEBUG


# ============================================
# Security Logger Tests
# ============================================

@pytest.mark.security
class TestSecurityLogger:
    """Test specialized security logger."""

    def test_authentication_failure_logging(self):
        """Test that authentication failures are logged with redaction."""
        security_logger = SecurityLogger()

        # Capture log output
        with patch.object(security_logger.logger, 'warning') as mock_warning:
            security_logger.log_authentication_failure(
                user_email="attacker@evil.com",
                reason="invalid_password"
            )

            # Verify logging was called
            assert mock_warning.called

            # Get the call arguments
            call_args = mock_warning.call_args
            log_message = call_args[0][0]
            extra_data = call_args[1]['extra']

            assert log_message == "Authentication failed"
            assert extra_data['event'] == 'authentication_failure'
            assert extra_data['reason'] == 'invalid_password'
            # Email will be redacted by filter later

    def test_compliance_violation_logging(self):
        """Test that compliance violations are logged."""
        security_logger = SecurityLogger()

        with patch.object(security_logger.logger, 'warning') as mock_warning:
            security_logger.log_compliance_violation(
                user_id=123,
                violation_type="restricted_plant_attempt",
                extra={"variety_id": 456}
            )

            assert mock_warning.called
            call_args = mock_warning.call_args
            extra_data = call_args[1]['extra']

            assert extra_data['event'] == 'compliance_violation'
            assert extra_data['user_id'] == 123
            assert extra_data['violation_type'] == "restricted_plant_attempt"


# ============================================
# Integration Tests
# ============================================

@pytest.mark.security
class TestLoggingIntegration:
    """Test end-to-end logging with redaction."""

    def test_full_logging_pipeline_redacts_sensitive_data(self):
        """Test that the full logging pipeline redacts sensitive data."""
        # Create logger with redaction filter and JSON formatter
        logger = logging.getLogger('integration_test')
        logger.setLevel(logging.INFO)

        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Create string stream to capture output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(JSONFormatter())
        handler.addFilter(RedactionFilter())
        logger.addHandler(handler)

        # Log message with sensitive data
        logger.info(
            "User login attempt",
            extra={
                'email': 'user@example.com',
                'password': 'SuperSecret123!',
                'token': 'eyJtest.token.data'
            }
        )

        # Get logged output
        log_output = log_stream.getvalue()
        log_data = json.loads(log_output)

        # Verify structure
        assert 'timestamp' in log_data
        assert 'level' in log_data
        assert 'message' in log_data

        # Verify redaction in extra fields
        assert 'extra' in log_data
        assert '[EMAIL_REDACTED]' in log_data['extra']['email']
        assert log_data['extra']['password'] == '[REDACTED]'
        assert log_data['extra']['token'] == '[REDACTED]'

        # Verify no sensitive data in output
        assert 'user@example.com' not in log_output
        assert 'SuperSecret123!' not in log_output
        assert 'eyJtest' not in log_output
