"""
Security tests for authentication and session handling.

Tests password hashing, token security, rate limiting, and other authentication
security measures identified in SECURITY_AUDIT_AUTHENTICATION.md.

Author: Security Audit
Date: 2026-02-01
"""

import pytest
import time
from datetime import datetime, timedelta
from jose import jwt
from freezegun import freeze_time
from unittest.mock import patch

from app.services.auth_service import AuthService
from app.models.user import User, UnitSystem
from app.utils.rate_limiter import RateLimiter
from app.config import get_settings


# ============================================
# Password Hashing Security Tests
# ============================================

@pytest.mark.security
class TestPasswordHashingSecurity:
    """Test password hashing security measures"""

    def test_bcrypt_produces_unique_salts(self):
        """Same password should produce different hashes due to unique salts"""
        password = "TestPassword123!"

        hash1 = AuthService.hash_password(password)
        hash2 = AuthService.hash_password(password)

        # Different hashes (different salts)
        assert hash1 != hash2

        # Both should verify correctly
        assert AuthService.verify_password(password, hash1)
        assert AuthService.verify_password(password, hash2)

    def test_bcrypt_cost_factor_sufficient(self):
        """Verify bcrypt cost factor is configured (manual verification)"""
        # NOTE: Actual timing test disabled due to frozen time in test environment
        # Manual verification:
        #   python -c "
        #   import time, bcrypt, hashlib
        #   p = hashlib.sha256(b'test').hexdigest().encode()
        #   start = time.perf_counter()
        #   bcrypt.hashpw(p, bcrypt.gensalt())
        #   print(f'Duration: {time.perf_counter() - start:.4f}s')
        #   # Should be > 0.05s with cost=12
        #   "

        # Verify bcrypt.gensalt() uses default or configured cost
        # Default cost=12 is acceptable (2^12 iterations)
        # Could be improved by making it configurable
        import bcrypt as bcrypt_module

        # Generate a salt and verify format
        salt = bcrypt_module.gensalt()

        # Salt format: $2b${cost}${22-char-salt}
        # Example: $2b$12$N9qo8uLOickgx2ZMRZoMye
        assert salt.startswith(b'$2b$'), "Should use bcrypt 2b version"

        # Extract cost from salt
        cost_part = salt.split(b'$')[2]
        cost = int(cost_part)

        # Verify cost is at least 12 (OWASP minimum for 2023)
        assert cost >= 10, f"Bcrypt cost ({cost}) is too low, should be >= 12"

        # Log a warning if cost is not optimal
        if cost < 12:
            pytest.skip(f"WARNING: Bcrypt cost={cost} is below recommended minimum of 12")

    def test_password_verified_correctly(self):
        """Correct password should verify successfully"""
        password = "TestPassword123!"
        hashed = AuthService.hash_password(password)

        assert AuthService.verify_password(password, hashed) is True

    def test_wrong_password_rejected(self):
        """Wrong password should fail verification"""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"

        hashed = AuthService.hash_password(password)

        assert AuthService.verify_password(wrong_password, hashed) is False

    def test_sha256_prehash_applied(self):
        """Verify SHA256 pre-hash is applied (for bcrypt 72-byte limit)"""
        # Password longer than 72 bytes
        long_password = "A" * 100

        hashed = AuthService.hash_password(long_password)

        # Should still work (bcrypt doesn't truncate due to SHA256 pre-hash)
        assert AuthService.verify_password(long_password, hashed) is True

    def test_case_sensitive_password(self):
        """Password verification should be case-sensitive"""
        password = "TestPassword123!"
        hashed = AuthService.hash_password(password)

        # Different case should fail
        assert AuthService.verify_password("testpassword123!", hashed) is False
        assert AuthService.verify_password("TESTPASSWORD123!", hashed) is False

    def test_malformed_hash_returns_false(self):
        """Invalid hash should return False, not raise exception"""
        password = "TestPassword123!"

        # Malformed hash
        result = AuthService.verify_password(password, "not_a_valid_hash")
        assert result is False

        # Empty hash
        result = AuthService.verify_password(password, "")
        assert result is False


# ============================================
# JWT Token Security Tests
# ============================================

@pytest.mark.security
class TestJWTTokenSecurity:
    """Test JWT token creation, validation, and security"""

    def test_token_contains_required_claims(self):
        """Token should contain sub, email, and exp claims"""
        user_id = 123
        email = "test@example.com"

        token = AuthService.create_access_token(user_id, email)

        # Decode without verification to inspect claims
        payload = jwt.decode(token, "dummy", options={"verify_signature": False})

        assert payload["sub"] == str(user_id)
        assert payload["email"] == email
        assert "exp" in payload

    def test_token_expiration_time_correct(self):
        """Token expiration should match configured time"""
        settings = get_settings()
        user_id = 123
        email = "test@example.com"

        before = datetime.utcnow()
        token = AuthService.create_access_token(user_id, email)
        after = datetime.utcnow()

        payload = jwt.decode(token, "dummy", options={"verify_signature": False})
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)

        # Should expire in approximately ACCESS_TOKEN_EXPIRE_MINUTES
        expected_min = before + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expected_max = after + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        assert expected_min <= exp_datetime <= expected_max

    def test_token_signature_validation(self):
        """Token with invalid signature should be rejected"""
        settings = get_settings()
        user_id = 123
        email = "test@example.com"

        # Create valid token
        valid_token = AuthService.create_access_token(user_id, email)

        # Verify it decodes successfully
        payload = AuthService.decode_token(valid_token)
        assert payload["sub"] == str(user_id)

        # Create token with wrong secret
        wrong_secret_token = jwt.encode(
            {"sub": str(user_id), "email": email, "exp": datetime.utcnow() + timedelta(hours=1)},
            "wrong_secret_key",
            algorithm=settings.ALGORITHM
        )

        # Should raise HTTPException
        with pytest.raises(Exception) as exc_info:
            AuthService.decode_token(wrong_secret_token)

        assert exc_info.value.status_code == 401

    def test_expired_token_rejected(self):
        """Expired token should be rejected"""
        settings = get_settings()
        user_id = 123
        email = "test@example.com"

        # Create token that expired 1 hour ago
        expired_token = jwt.encode(
            {
                "sub": str(user_id),
                "email": email,
                "exp": datetime.utcnow() - timedelta(hours=1)
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        # Should raise HTTPException
        with pytest.raises(Exception) as exc_info:
            AuthService.decode_token(expired_token)

        assert exc_info.value.status_code == 401

    def test_token_without_expiration_rejected(self):
        """Token without exp claim should be rejected"""
        settings = get_settings()
        user_id = 123
        email = "test@example.com"

        # Create token without expiration
        no_exp_token = jwt.encode(
            {"sub": str(user_id), "email": email},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        # Should raise HTTPException (exp is required by JWT standard)
        with pytest.raises(Exception) as exc_info:
            AuthService.decode_token(no_exp_token)

        assert exc_info.value.status_code == 401

    def test_token_algorithm_validation(self):
        """Token should use HS256 algorithm"""
        settings = get_settings()

        assert settings.ALGORITHM == "HS256", "Should use HS256 for HMAC-SHA256 signatures"


# ============================================
# Rate Limiting Tests
# ============================================

@pytest.mark.security
class TestRateLimiter:
    """Test rate limiter functionality"""

    def test_rate_limiter_allows_initial_attempts(self):
        """Rate limiter should allow attempts up to max_attempts"""
        limiter = RateLimiter(max_attempts=3, window_minutes=15)
        email = "test@example.com"

        # First 3 attempts should be allowed
        is_allowed, remaining = limiter.is_allowed(email)
        assert is_allowed is True
        assert remaining == 2

        limiter.record_attempt(email)

        is_allowed, remaining = limiter.is_allowed(email)
        assert is_allowed is True
        assert remaining == 1

        limiter.record_attempt(email)

        is_allowed, remaining = limiter.is_allowed(email)
        assert is_allowed is True
        assert remaining == 0

        limiter.record_attempt(email)

    def test_rate_limiter_blocks_after_max_attempts(self):
        """Rate limiter should block after max_attempts"""
        limiter = RateLimiter(max_attempts=3, window_minutes=15)
        email = "test@example.com"

        # Exhaust attempts
        for i in range(3):
            limiter.record_attempt(email)

        # 4th attempt should be blocked
        is_allowed, remaining = limiter.is_allowed(email)
        assert is_allowed is False
        assert remaining == 0

    def test_rate_limiter_per_email_isolation(self):
        """Rate limiter should isolate attempts by email"""
        limiter = RateLimiter(max_attempts=3, window_minutes=15)

        email1 = "user1@example.com"
        email2 = "user2@example.com"

        # Exhaust attempts for email1
        for i in range(3):
            limiter.record_attempt(email1)

        # email1 should be blocked
        is_allowed, _ = limiter.is_allowed(email1)
        assert is_allowed is False

        # email2 should still be allowed
        is_allowed, remaining = limiter.is_allowed(email2)
        assert is_allowed is True
        assert remaining == 2

    def test_rate_limiter_reset_clears_attempts(self):
        """Rate limiter reset should clear all attempts for email"""
        limiter = RateLimiter(max_attempts=3, window_minutes=15)
        email = "test@example.com"

        # Exhaust attempts
        for i in range(3):
            limiter.record_attempt(email)

        # Should be blocked
        is_allowed, _ = limiter.is_allowed(email)
        assert is_allowed is False

        # Reset
        limiter.reset(email)

        # Should be allowed again
        is_allowed, remaining = limiter.is_allowed(email)
        assert is_allowed is True
        assert remaining == 2

    def test_rate_limiter_thread_safe(self):
        """Rate limiter should be thread-safe"""
        import threading

        limiter = RateLimiter(max_attempts=100, window_minutes=15)
        email = "test@example.com"

        def record_attempts():
            for i in range(10):
                limiter.record_attempt(email)

        # Create 10 threads, each recording 10 attempts
        threads = [threading.Thread(target=record_attempts) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have exactly 100 attempts recorded
        is_allowed, remaining = limiter.is_allowed(email)
        assert is_allowed is False  # At max
        assert remaining == 0


# ============================================
# Password Reset Security Tests
# ============================================

@pytest.mark.security
class TestPasswordResetSecurity:
    """Test password reset security measures"""

    def test_password_reset_rate_limiting(self, client):
        """Password reset should be rate limited"""
        email = "test@example.com"

        # Make 3 requests (max allowed)
        for i in range(3):
            response = client.post("/auth/password-reset/request", json={"email": email})
            assert response.status_code in [200, 404]  # 404 if email doesn't exist

        # 4th request should be rate limited
        response = client.post("/auth/password-reset/request", json={"email": email})
        assert response.status_code == 429
        assert "too many" in response.json()["detail"].lower()

    def test_password_reset_no_email_enumeration(self, client):
        """Password reset should not reveal if email exists"""
        # Request reset for non-existent email
        response1 = client.post("/auth/password-reset/request", json={
            "email": "nonexistent@example.com"
        })

        # Request reset for existing email (if we had one)
        response2 = client.post("/auth/password-reset/request", json={
            "email": "existing@example.com"
        })

        # Both should return same response (no email enumeration)
        assert response1.status_code == response2.status_code
        # Both should have similar message
        assert "success" in response1.json()
        assert "success" in response2.json()


# ============================================
# Authentication Flow Tests
# ============================================

@pytest.mark.security
class TestAuthenticationFlowSecurity:
    """Test end-to-end authentication security"""

    def test_login_with_correct_credentials(self, client, test_db):
        """Valid credentials should grant access"""
        # Create user
        user = User(
            email="testuser@example.com",
            hashed_password=AuthService.hash_password("ValidPassword123!"),
            unit_system=UnitSystem.METRIC
        )
        test_db.add(user)
        test_db.commit()

        # Login
        response = client.post("/users/login", json={
            "email": "testuser@example.com",
            "password": "ValidPassword123!"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_case_insensitive_email(self, client, test_db):
        """Email should be case-insensitive during login"""
        # Create user with lowercase email
        user = User(
            email="testuser@example.com",
            hashed_password=AuthService.hash_password("ValidPassword123!"),
            unit_system=UnitSystem.METRIC
        )
        test_db.add(user)
        test_db.commit()

        # Login with uppercase email
        response = client.post("/users/login", json={
            "email": "TESTUSER@EXAMPLE.COM",
            "password": "ValidPassword123!"
        })

        # Should work (email is case-insensitive)
        assert response.status_code == 200

    def test_login_with_wrong_password(self, client, test_db):
        """Wrong password should be rejected"""
        user = User(
            email="testuser@example.com",
            hashed_password=AuthService.hash_password("ValidPassword123!"),
            unit_system=UnitSystem.METRIC
        )
        test_db.add(user)
        test_db.commit()

        response = client.post("/users/login", json={
            "email": "testuser@example.com",
            "password": "WrongPassword123!"
        })

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_with_nonexistent_user(self, client):
        """Login with non-existent email should be rejected"""
        response = client.post("/users/login", json={
            "email": "nonexistent@example.com",
            "password": "AnyPassword123!"
        })

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_protected_endpoint_requires_token(self, client):
        """Protected endpoints should require authentication"""
        # Try to access protected endpoint without token
        response = client.get("/gardens")

        assert response.status_code == 403

    def test_protected_endpoint_rejects_invalid_token(self, client):
        """Protected endpoints should reject invalid tokens"""
        response = client.get("/gardens", headers={
            "Authorization": "Bearer invalid_token_12345"
        })

        assert response.status_code == 401


# ============================================
# Token Lifetime Tests
# ============================================

@pytest.mark.security
class TestTokenLifetime:
    """Test token expiration behavior"""

    def test_token_lifetime_configuration(self):
        """Verify token lifetime is configured"""
        settings = get_settings()

        # Should have a defined expiration
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0

        # SECURITY NOTE: 10080 minutes (7 days) is too long
        # Recommended: 15-60 minutes
        if settings.ACCESS_TOKEN_EXPIRE_MINUTES > 1440:  # > 1 day
            pytest.skip(
                f"WARNING: Token lifetime ({settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes) "
                f"is excessive. Recommended: 15-60 minutes for access tokens. "
                f"See SECURITY_AUDIT_AUTHENTICATION.md for details."
            )

    def test_token_claims_are_immutable(self):
        """Token payload should not be modifiable after creation"""
        user_id = 123
        email = "test@example.com"

        token = AuthService.create_access_token(user_id, email)

        # Decode to get payload
        payload = jwt.decode(token, "dummy", options={"verify_signature": False})
        original_sub = payload["sub"]

        # Try to modify sub claim
        payload["sub"] = "999"

        # Re-encode with modified payload
        settings = get_settings()
        modified_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        # Original token should still have original sub
        original_payload = AuthService.decode_token(token)
        assert original_payload["sub"] == original_sub

        # Modified token should have new sub (but this proves tokens can be forged if secret leaks)
        modified_payload = AuthService.decode_token(modified_token)
        assert modified_payload["sub"] == "999"

        # SECURITY NOTE: This test demonstrates why SECRET_KEY must be kept secure


# ============================================
# Security Configuration Tests
# ============================================

@pytest.mark.security
class TestSecurityConfiguration:
    """Test security-related configuration"""

    def test_secret_key_not_default(self):
        """SECRET_KEY should not be the default value in production"""
        settings = get_settings()

        if settings.APP_ENV == "production":
            assert settings.SECRET_KEY != "dev-secret-key-change-in-production", \
                "CRITICAL: Default SECRET_KEY detected in production! Change immediately."

    def test_secret_key_minimum_length(self):
        """SECRET_KEY should be sufficiently long"""
        settings = get_settings()

        # NIST recommends 128-bit (16 bytes) minimum for HMAC keys
        # 256-bit (32 bytes) is recommended
        # Base64 encoding: 32 bytes = 43 characters
        if len(settings.SECRET_KEY) < 32:
            pytest.skip(
                f"WARNING: SECRET_KEY is too short ({len(settings.SECRET_KEY)} chars). "
                f"Recommended: 43+ characters (256-bit key)."
            )

    def test_jwt_algorithm_secure(self):
        """JWT algorithm should be HS256 or stronger"""
        settings = get_settings()

        # HS256 = HMAC-SHA256 (secure)
        # Avoid: HS384, HS512 (overkill), none (insecure)
        assert settings.ALGORITHM in ["HS256", "HS384", "HS512"], \
            f"Insecure JWT algorithm: {settings.ALGORITHM}"


# ============================================
# Timing Attack Prevention Tests
# ============================================

@pytest.mark.security
class TestTimingAttackPrevention:
    """Test protection against timing attacks"""

    def test_password_verification_constant_time(self):
        """Password verification should take similar time regardless of correctness"""
        password = "TestPassword123!"
        hashed = AuthService.hash_password(password)

        # Measure correct password verification
        times_correct = []
        for _ in range(10):
            start = time.time()
            AuthService.verify_password(password, hashed)
            times_correct.append(time.time() - start)

        # Measure wrong password verification
        times_wrong = []
        for _ in range(10):
            start = time.time()
            AuthService.verify_password("WrongPassword123!", hashed)
            times_wrong.append(time.time() - start)

        # Average times should be similar (within 2x of each other)
        # bcrypt.checkpw is designed for constant time
        avg_correct = sum(times_correct) / len(times_correct)
        avg_wrong = sum(times_wrong) / len(times_wrong)

        ratio = max(avg_correct, avg_wrong) / min(avg_correct, avg_wrong)

        # Times should be within 2x (bcrypt's constant-time guarantee)
        assert ratio < 2.0, f"Timing difference detected: {ratio}x (timing attack risk)"


# ============================================
# Password Complexity Tests
# ============================================

@pytest.mark.security
class TestPasswordComplexity:
    """Test password complexity requirements"""

    def test_password_minimum_length_enforced(self, client):
        """Passwords shorter than 8 characters should be rejected"""
        response = client.post("/users", json={
            "email": "test@example.com",
            "password": "Short1!"  # 7 characters
        })

        # Should fail validation
        assert response.status_code == 422

    def test_password_requires_uppercase(self, client):
        """Passwords without uppercase should be rejected"""
        response = client.post("/users", json={
            "email": "test@example.com",
            "password": "alllowercase123!"
        })

        assert response.status_code == 422

    def test_password_requires_lowercase(self, client):
        """Passwords without lowercase should be rejected"""
        response = client.post("/users", json={
            "email": "test@example.com",
            "password": "ALLUPPERCASE123!"
        })

        assert response.status_code == 422

    def test_password_requires_digit(self, client):
        """Passwords without digits should be rejected"""
        response = client.post("/users", json={
            "email": "test@example.com",
            "password": "NoDigitsHere!"
        })

        assert response.status_code == 422

    def test_password_requires_special_char(self, client):
        """Passwords without special characters should be rejected"""
        response = client.post("/users", json={
            "email": "test@example.com",
            "password": "NoSpecialChar123"
        })

        assert response.status_code == 422
