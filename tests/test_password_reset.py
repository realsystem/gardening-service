"""Tests for password reset functionality"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.repositories.user_repository import UserRepository
from app.repositories.password_reset_repository import PasswordResetRepository
from app.services.auth_service import AuthService
from app.utils.token_generator import TokenGenerator
from app.utils.password_validator import PasswordValidator
from app.utils.rate_limiter import RateLimiter

# Note: Use the 'client' fixture from conftest.py instead of creating a module-level client


class TestPasswordResetRequest:
    """Tests for password reset request endpoint"""

    def test_request_reset_existing_email(self, client, db: Session, test_user: User):
        """Test requesting reset for existing email returns success"""
        response = client.post(
            "/auth/password-reset/request",
            json={"email": test_user.email}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reset link has been sent" in data["message"].lower()

        # Verify token was created
        reset_repo = PasswordResetRepository(db)
        token = reset_repo.get_active_token_for_user(test_user.id)
        assert token is not None
        assert token.is_valid()

    def test_request_reset_nonexistent_email(self, client, db: Session):
        """Test requesting reset for non-existent email still returns success (prevents email enumeration)"""
        from app.config import get_settings
        settings = get_settings()

        response = client.post(
            "/auth/password-reset/request",
            json={"email": "nonexistent@example.com"}
        )

        # In DEBUG mode (test/local), returns 404 with helpful message
        # In production mode, returns 200 to prevent email enumeration
        if settings.DEBUG:
            assert response.status_code == 404
            data = response.json()
            assert "error" in data
            assert "no account found" in data["error"]["message"].lower()
        else:
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "reset link has been sent" in data["message"].lower()

    def test_request_reset_invalid_email(self, client):
        """Test requesting reset with invalid email format"""
        response = client.post(
            "/auth/password-reset/request",
            json={"email": "not-an-email"}
        )

        assert response.status_code == 422  # Validation error

    def test_request_reset_rate_limiting(self, client, db: Session, test_user: User):
        """Test rate limiting prevents too many requests"""
        from app.utils.rate_limiter import password_reset_rate_limiter

        # Clear any existing rate limit state for this email
        password_reset_rate_limiter.reset(test_user.email)

        # Make 3 requests (should all succeed)
        for _ in range(3):
            response = client.post(
                "/auth/password-reset/request",
                json={"email": test_user.email}
            )
            assert response.status_code == 200

        # 4th request should be rate limited
        response = client.post(
            "/auth/password-reset/request",
            json={"email": test_user.email}
        )
        assert response.status_code == 429  # Too many requests


class TestPasswordResetConfirm:
    """Tests for password reset confirmation endpoint"""

    def test_confirm_reset_valid_token(self, client, db: Session, test_user: User):
        """Test confirming password reset with valid token"""
        # Create a reset token
        raw_token, token_hash = TokenGenerator.generate_and_hash()
        reset_repo = PasswordResetRepository(db)
        expires_at = PasswordResetToken.get_expiration_time(hours=1)
        reset_repo.create_token(test_user, token_hash, expires_at)

        # Confirm reset with new password
        new_password = "NewStrongPass123!"
        response = client.post(
            "/auth/password-reset/confirm",
            json={
                "token": raw_token,
                "new_password": new_password
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reset successfully" in data["message"].lower()

        # Verify password was changed
        db.refresh(test_user)
        assert AuthService.verify_password(new_password, test_user.hashed_password)

        # Verify old password no longer works
        assert not AuthService.verify_password("oldpassword", test_user.hashed_password)

        # Verify token was marked as used
        token = reset_repo.get_token_by_hash(token_hash)
        assert token.used_at is not None
        assert not token.is_valid()

    def test_confirm_reset_invalid_token(self, client):
        """Test confirming reset with invalid token"""
        response = client.post(
            "/auth/password-reset/confirm",
            json={
                "token": "invalid-token-123",
                "new_password": "NewStrongPass123!"
            }
        )

        assert response.status_code == 400
        # Response uses custom error format: {"error": {"code": "...", "message": "..."}}
        data = response.json()
        assert "error" in data
        assert "message" in data["error"]
        assert "invalid" in data["error"]["message"].lower() or "expired" in data["error"]["message"].lower()

    def test_confirm_reset_expired_token(self, client, db: Session, test_user: User):
        """Test confirming reset with expired token"""
        # Create an expired token
        raw_token, token_hash = TokenGenerator.generate_and_hash()
        reset_repo = PasswordResetRepository(db)
        expires_at = datetime.utcnow() - timedelta(hours=2)  # Expired 2 hours ago
        reset_repo.create_token(test_user, token_hash, expires_at)

        response = client.post(
            "/auth/password-reset/confirm",
            json={
                "token": raw_token,
                "new_password": "NewStrongPass123!"
            }
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "message" in data["error"]
        assert "expired" in data["error"]["message"].lower()

    def test_confirm_reset_used_token(self, client, db: Session, test_user: User):
        """Test confirming reset with already used token"""
        # Create and use a token
        raw_token, token_hash = TokenGenerator.generate_and_hash()
        reset_repo = PasswordResetRepository(db)
        expires_at = PasswordResetToken.get_expiration_time(hours=1)
        token = reset_repo.create_token(test_user, token_hash, expires_at)
        reset_repo.mark_token_as_used(token)

        response = client.post(
            "/auth/password-reset/confirm",
            json={
                "token": raw_token,
                "new_password": "NewStrongPass123!"
            }
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "already been used" in data["error"]["message"].lower()

    def test_confirm_reset_weak_password(self, client, db: Session, test_user: User):
        """Test confirming reset with weak password"""
        raw_token, token_hash = TokenGenerator.generate_and_hash()
        reset_repo = PasswordResetRepository(db)
        expires_at = PasswordResetToken.get_expiration_time(hours=1)
        reset_repo.create_token(test_user, token_hash, expires_at)

        response = client.post(
            "/auth/password-reset/confirm",
            json={
                "token": raw_token,
                "new_password": "weak"  # Too short, no uppercase, no special char
            }
        )

        assert response.status_code == 422  # Validation error

    def test_confirm_reset_reuse_attempt(self, client, db: Session, test_user: User):
        """Test attempting to reuse a token after successful reset"""
        raw_token, token_hash = TokenGenerator.generate_and_hash()
        reset_repo = PasswordResetRepository(db)
        expires_at = PasswordResetToken.get_expiration_time(hours=1)
        reset_repo.create_token(test_user, token_hash, expires_at)

        # First reset succeeds
        response1 = client.post(
            "/auth/password-reset/confirm",
            json={
                "token": raw_token,
                "new_password": "FirstPassword123!"
            }
        )
        assert response1.status_code == 200

        # Second attempt with same token fails
        response2 = client.post(
            "/auth/password-reset/confirm",
            json={
                "token": raw_token,
                "new_password": "SecondPassword123!"
            }
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "error" in data
        assert "already been used" in data["error"]["message"].lower()


class TestPasswordRequirements:
    """Tests for password requirements endpoint"""

    def test_get_password_requirements(self, client):
        """Test retrieving password requirements"""
        response = client.get("/auth/password-reset/requirements")

        assert response.status_code == 200
        data = response.json()
        assert "requirements" in data
        assert len(data["requirements"]) > 0
        assert any("8 characters" in req for req in data["requirements"])


class TestPasswordValidator:
    """Tests for password validation utility"""

    def test_valid_password(self, client):
        """Test validation of strong password"""
        is_valid, errors = PasswordValidator.validate("StrongPass123!")
        assert is_valid is True
        assert errors is None

    def test_password_too_short(self, client):
        """Test password too short"""
        is_valid, errors = PasswordValidator.validate("Short1!")
        assert is_valid is False
        assert any("8 characters" in error for error in errors)

    def test_password_no_uppercase(self, client):
        """Test password without uppercase"""
        is_valid, errors = PasswordValidator.validate("lowercase123!")
        assert is_valid is False
        assert any("uppercase" in error.lower() for error in errors)

    def test_password_no_lowercase(self, client):
        """Test password without lowercase"""
        is_valid, errors = PasswordValidator.validate("UPPERCASE123!")
        assert is_valid is False
        assert any("lowercase" in error.lower() for error in errors)

    def test_password_no_digit(self, client):
        """Test password without digit"""
        is_valid, errors = PasswordValidator.validate("NoDigits!")
        assert is_valid is False
        assert any("digit" in error.lower() for error in errors)

    def test_password_no_special_char(self, client):
        """Test password without special character"""
        is_valid, errors = PasswordValidator.validate("NoSpecial123")
        assert is_valid is False
        assert any("special" in error.lower() for error in errors)


class TestTokenGenerator:
    """Tests for token generation utility"""

    def test_generate_token(self, client):
        """Test token generation"""
        token = TokenGenerator.generate_token()
        assert len(token) > 0
        assert isinstance(token, str)

    def test_hash_token(self, client):
        """Test token hashing"""
        token = "test-token-123"
        hash1 = TokenGenerator.hash_token(token)
        hash2 = TokenGenerator.hash_token(token)

        # Same token produces same hash
        assert hash1 == hash2
        # Hash is different from original token
        assert hash1 != token
        # Hash has expected length (SHA-256 hex = 64 chars)
        assert len(hash1) == 64

    def test_verify_token(self, client):
        """Test token verification"""
        raw_token, token_hash = TokenGenerator.generate_and_hash()

        # Correct token verifies
        assert TokenGenerator.verify_token(raw_token, token_hash) is True

        # Wrong token doesn't verify
        assert TokenGenerator.verify_token("wrong-token", token_hash) is False

    def test_tokens_are_unique(self, client):
        """Test that generated tokens are unique"""
        tokens = [TokenGenerator.generate_token() for _ in range(100)]
        assert len(tokens) == len(set(tokens))  # All unique


class TestRateLimiter:
    """Tests for rate limiter utility"""

    def test_allows_requests_within_limit(self, client):
        """Test rate limiter allows requests within limit"""
        limiter = RateLimiter(max_attempts=3, window_minutes=15)
        email = "test@example.com"

        # First 3 attempts should be allowed
        for i in range(3):
            allowed, remaining = limiter.is_allowed(email)
            assert allowed is True
            assert remaining == 2 - i
            limiter.record_attempt(email)

        # 4th attempt should be blocked
        allowed, remaining = limiter.is_allowed(email)
        assert allowed is False
        assert remaining == 0

    def test_reset_clears_attempts(self, client):
        """Test reset clears rate limit attempts"""
        limiter = RateLimiter(max_attempts=2, window_minutes=15)
        email = "test@example.com"

        # Use up attempts
        limiter.record_attempt(email)
        limiter.record_attempt(email)
        assert limiter.is_allowed(email)[0] is False

        # Reset
        limiter.reset(email)

        # Should be allowed again
        assert limiter.is_allowed(email)[0] is True


class TestPasswordResetRepository:
    """Tests for password reset repository"""

    def test_create_token(self, client, db: Session, test_user: User):
        """Test creating password reset token"""
        repo = PasswordResetRepository(db)
        raw_token, token_hash = TokenGenerator.generate_and_hash()
        expires_at = PasswordResetToken.get_expiration_time(hours=1)

        token = repo.create_token(test_user, token_hash, expires_at)

        assert token.id is not None
        assert token.user_id == test_user.id
        assert token.token_hash == token_hash
        assert token.expires_at == expires_at
        assert token.used_at is None
        assert token.is_valid()

    def test_create_token_invalidates_old_tokens(self, client, db: Session, test_user: User):
        """Test creating new token invalidates old tokens"""
        repo = PasswordResetRepository(db)

        # Create first token
        _, hash1 = TokenGenerator.generate_and_hash()
        expires1 = PasswordResetToken.get_expiration_time(hours=1)
        token1 = repo.create_token(test_user, hash1, expires1)

        # Create second token
        _, hash2 = TokenGenerator.generate_and_hash()
        expires2 = PasswordResetToken.get_expiration_time(hours=1)
        token2 = repo.create_token(test_user, hash2, expires2)

        # Refresh first token
        db.refresh(token1)

        # First token should be invalidated
        assert token1.used_at is not None
        assert not token1.is_valid()

        # Second token should be valid
        assert token2.used_at is None
        assert token2.is_valid()

    def test_get_active_token_for_user(self, client, db: Session, test_user: User):
        """Test retrieving active token for user"""
        repo = PasswordResetRepository(db)
        _, token_hash = TokenGenerator.generate_and_hash()
        expires_at = PasswordResetToken.get_expiration_time(hours=1)
        created_token = repo.create_token(test_user, token_hash, expires_at)

        active_token = repo.get_active_token_for_user(test_user.id)

        assert active_token is not None
        assert active_token.id == created_token.id


class TestChangePassword:
    """Tests for change password endpoint (authenticated users)"""

    def test_change_password_success(self, client, db: Session, test_user: User):
        """Test changing password with correct current password"""
        # Login to get token
        login_response = client.post(
            "/users/login",
            json={"email": test_user.email, "password": "TestPassword123!"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Change password
        new_password = "NewStrongPassword456!"
        response = client.post(
            "/auth/password/change",
            json={
                "current_password": "TestPassword123!",
                "new_password": new_password
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "changed successfully" in data["message"].lower()

        # Verify old password no longer works
        old_login = client.post(
            "/users/login",
            json={"email": test_user.email, "password": "TestPassword123!"}
        )
        assert old_login.status_code == 401

        # Verify new password works
        new_login = client.post(
            "/users/login",
            json={"email": test_user.email, "password": new_password}
        )
        assert new_login.status_code == 200

    def test_change_password_wrong_current_password(self, client, db: Session, test_user: User):
        """Test changing password with incorrect current password"""
        # Login to get token
        login_response = client.post(
            "/users/login",
            json={"email": test_user.email, "password": "TestPassword123!"}
        )
        token = login_response.json()["access_token"]

        # Try to change with wrong current password
        response = client.post(
            "/auth/password/change",
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewPassword456!"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400
        assert "incorrect" in response.json()["error"]["message"].lower()

    def test_change_password_weak_new_password(self, client, db: Session, test_user: User):
        """Test changing password with weak new password"""
        # Login to get token
        login_response = client.post(
            "/users/login",
            json={"email": test_user.email, "password": "TestPassword123!"}
        )
        token = login_response.json()["access_token"]

        # Try to change to weak password
        response = client.post(
            "/auth/password/change",
            json={
                "current_password": "TestPassword123!",
                "new_password": "weak"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 422  # Validation error

    def test_change_password_unauthenticated(self, client):
        """Test changing password without authentication"""
        response = client.post(
            "/auth/password/change",
            json={
                "current_password": "TestPassword123!",
                "new_password": "NewPassword456!"
            }
        )

        assert response.status_code == 403  # Unauthorized

    def test_change_password_invalidates_reset_tokens(self, client, db: Session, test_user: User):
        """Test that changing password invalidates all reset tokens"""
        # Create a reset token
        raw_token, token_hash = TokenGenerator.generate_and_hash()
        reset_repo = PasswordResetRepository(db)
        expires_at = PasswordResetToken.get_expiration_time(hours=1)
        reset_repo.create_token(test_user, token_hash, expires_at)

        # Login to get token
        login_response = client.post(
            "/users/login",
            json={"email": test_user.email, "password": "TestPassword123!"}
        )
        token = login_response.json()["access_token"]

        # Change password
        response = client.post(
            "/auth/password/change",
            json={
                "current_password": "TestPassword123!",
                "new_password": "NewPassword456!"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        # Verify reset token is invalidated
        db.refresh(test_user)
        active_token = reset_repo.get_active_token_for_user(test_user.id)
        assert active_token is None


class TestRequestPasswordResetAuthenticated:
    """Tests for authenticated password reset request endpoint"""

    def test_request_reset_authenticated_success(self, client, db: Session, test_user: User):
        """Test requesting reset as authenticated user"""
        # Login to get token
        login_response = client.post(
            "/users/login",
            json={"email": test_user.email, "password": "TestPassword123!"}
        )
        token = login_response.json()["access_token"]

        # Request password reset
        response = client.post(
            "/auth/password-reset/request-authenticated",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reset link has been sent" in data["message"].lower()

        # Verify token was created
        reset_repo = PasswordResetRepository(db)
        reset_token = reset_repo.get_active_token_for_user(test_user.id)
        assert reset_token is not None
        assert reset_token.is_valid()

    def test_request_reset_authenticated_unauthenticated(self, client):
        """Test requesting reset without authentication"""
        response = client.post(
            "/auth/password-reset/request-authenticated"
        )

        assert response.status_code == 403  # Unauthorized

    def test_request_reset_authenticated_rate_limiting(self, client, db: Session, test_user: User):
        """Test rate limiting for authenticated reset requests"""
        from app.utils.rate_limiter import password_reset_rate_limiter

        # Clear any existing rate limit state for this email
        password_reset_rate_limiter.reset(test_user.email)

        # Login to get token
        login_response = client.post(
            "/users/login",
            json={"email": test_user.email, "password": "TestPassword123!"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Make 3 requests (should all succeed)
        for _ in range(3):
            response = client.post(
                "/auth/password-reset/request-authenticated",
                headers=headers
            )
            assert response.status_code == 200

        # 4th request should be rate limited
        response = client.post(
            "/auth/password-reset/request-authenticated",
            headers=headers
        )
        assert response.status_code == 429  # Too many requests


# Fixtures

@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user"""
    user_repo = UserRepository(db)

    # Clean up any existing test user
    existing = user_repo.get_by_email("test@example.com")
    if existing:
        db.delete(existing)
        db.commit()

    # Create new test user
    user = user_repo.create(
        email="test@example.com",
        hashed_password=AuthService.hash_password("TestPassword123!"),
        usda_zone="7a"
    )

    yield user

    # Cleanup
    db.delete(user)
    db.commit()
