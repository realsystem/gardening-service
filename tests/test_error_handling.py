"""Tests for error handling and failure modes"""
import pytest
from fastapi import HTTPException
from app.services.auth_service import AuthService


class TestErrorHandling:
    """Test graceful error handling"""

    def test_invalid_jwt_token(self):
        """Verify invalid JWT tokens are rejected gracefully"""
        invalid_token = "invalid.jwt.token"

        with pytest.raises(HTTPException) as exc_info:
            AuthService.decode_token(invalid_token)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    def test_expired_token_handling(self):
        """Verify expired tokens are handled (structure test)"""
        # Create a token that's already expired
        from datetime import datetime, timedelta
        from jose import jwt
        from app.config import get_settings

        settings = get_settings()
        expired_time = datetime.utcnow() - timedelta(minutes=10)  # 10 minutes ago

        expired_token = jwt.encode(
            {"sub": "1", "email": "test@example.com", "exp": expired_time},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        with pytest.raises(HTTPException) as exc_info:
            AuthService.decode_token(expired_token)

        assert exc_info.value.status_code == 401

    def test_password_verification_failure(self, test_db):
        """Verify wrong password returns None"""
        result = AuthService.authenticate_user(
            test_db,
            email="nonexistent@example.com",
            password="wrongpassword"
        )
        assert result is None
