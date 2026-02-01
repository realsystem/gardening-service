"""Functional tests for admin access control

Tests admin-only endpoints and privilege escalation prevention.
All tests in this file are marked with @pytest.mark.admin_access for easy filtering.
"""
import pytest
import httpx
from app.services.auth_service import AuthService


pytestmark = pytest.mark.admin_access


class TestRegistrationAdminPrevention:
    """Test that registration cannot set admin privileges"""

    def test_register_with_is_admin_true_ignored(self, http_client: httpx.Client):
        """Registration should ignore is_admin=true in request body"""
        response = http_client.post(
            "/users",
            json={
                "email": "attacker@example.com",
                "password": "Password123!",
                "is_admin": True  # Attempt to set admin via registration
            }
        )

        assert response.status_code == 201
        user_data = response.json()
        # is_admin should be False (default) despite the request
        assert user_data.get("is_admin") is False

    def test_register_with_is_admin_in_extra_fields_ignored(self, http_client: httpx.Client):
        """Registration should ignore is_admin even if passed in various ways"""
        response = http_client.post(
            "/users",
            json={
                "email": "attacker2@example.com",
                "password": "Password123!",
                "display_name": "Attacker",
                "is_admin": "true",  # Try as string
            }
        )

        assert response.status_code == 201
        user_data = response.json()
        assert user_data.get("is_admin") is False


class TestProfileUpdateAdminPrevention:
    """Test that profile updates cannot set admin privileges"""

    def test_update_profile_with_is_admin_ignored(
        self,
        authenticated_client: httpx.Client,
        registered_user: dict
    ):
        """Profile update should ignore is_admin field"""
        # Attempt to set is_admin via profile update
        response = authenticated_client.put(
            "/users/me",
            json={
                "display_name": "New Name",
                "is_admin": True  # Attempt privilege escalation
            }
        )

        # Update should succeed but is_admin should remain False
        assert response.status_code == 200
        user_data = response.json()
        assert user_data.get("is_admin") is False
        assert user_data.get("display_name") == "New Name"

    def test_update_profile_cannot_escalate_privileges(
        self,
        authenticated_client: httpx.Client
    ):
        """Multiple update attempts should not grant admin access"""
        # First update attempt
        authenticated_client.put(
            "/users/me",
            json={"is_admin": True, "city": "Portland"}
        )

        # Second update attempt
        authenticated_client.put(
            "/users/me",
            json={"is_admin": "true"}
        )

        # Verify user is still not admin
        response = authenticated_client.get("/users/me")
        assert response.status_code == 200
        user_data = response.json()
        assert user_data.get("is_admin") is False


class TestAdminEndpointAuthorization:
    """Test admin-only endpoints require admin privileges"""

    def test_system_stats_requires_admin(
        self,
        authenticated_client: httpx.Client
    ):
        """Non-admin users cannot access system stats"""
        response = authenticated_client.get("/system/stats")

        assert response.status_code == 403
        error_data = response.json()
        assert "admin" in error_data.get("detail", "").lower()

    def test_promote_user_requires_admin(
        self,
        authenticated_client: httpx.Client,
        registered_user: dict
    ):
        """Non-admin users cannot promote other users"""
        response = authenticated_client.post(
            f"/admin/users/{registered_user['user_id']}/promote"
        )

        assert response.status_code == 403
        error_data = response.json()
        assert "admin" in error_data.get("detail", "").lower()

    def test_revoke_admin_requires_admin(
        self,
        authenticated_client: httpx.Client,
        registered_user: dict
    ):
        """Non-admin users cannot revoke admin privileges"""
        response = authenticated_client.post(
            f"/admin/users/{registered_user['user_id']}/revoke"
        )

        assert response.status_code == 403
        error_data = response.json()
        assert "admin" in error_data.get("detail", "").lower()

    def test_unauthenticated_cannot_access_system_stats(
        self,
        http_client: httpx.Client
    ):
        """Unauthenticated requests to admin endpoints fail"""
        response = http_client.get("/system/stats")

        # Should be 403 (not authenticated) or 401 (invalid token)
        assert response.status_code in [401, 403]


@pytest.fixture
def admin_user(http_client: httpx.Client):
    """Create an admin user for testing

    Note: In production, admin users must be created via the secure
    admin assignment script, not through the API.

    For functional tests, we assume there's a test admin user or we create
    one through the test database setup.
    """
    import uuid
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.user import User
    from app.database import Base
    import os

    # Get database URL from environment or use test database
    db_url = os.getenv("DATABASE_URL", "sqlite:///./gardening.db")

    # Create engine and session
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Create admin user directly in database
        unique_id = str(uuid.uuid4())[:8]
        email = f"testadmin_{unique_id}@example.com"
        password = "AdminPass123!"

        admin = User(
            email=email,
            hashed_password=AuthService.hash_password(password),
            is_admin=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        admin_id = admin.id

        # Login to get token
        response = http_client.post(
            "/users/login",
            json={
                "email": email,
                "password": password
            }
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        token_data = response.json()

        return {
            "user_id": admin_id,
            "email": email,
            "token": token_data["access_token"]
        }
    finally:
        db.close()


@pytest.fixture
def admin_client(http_client: httpx.Client, admin_user: dict) -> httpx.Client:
    """Return an HTTP client authenticated as admin"""
    http_client.headers.update({
        "Authorization": f"Bearer {admin_user['token']}"
    })
    return http_client


class TestAdminFunctionality:
    """Test admin endpoints when called by actual admin users"""

    def test_admin_can_access_system_stats(self, admin_client: httpx.Client):
        """Admin users can access system stats"""
        response = admin_client.get("/system/stats")

        assert response.status_code == 200
        stats = response.json()
        assert "total_users" in stats
        assert "active_users_24h" in stats
        assert "total_gardens" in stats
        assert "total_lands" in stats
        assert "timestamp" in stats

    def test_admin_can_promote_user(
        self,
        admin_client: httpx.Client,
        http_client: httpx.Client
    ):
        """Admin users can promote other users to admin"""
        # Create a regular user
        regular_user_response = http_client.post(
            "/users",
            json={
                "email": "regular@example.com",
                "password": "Password123!"
            }
        )
        assert regular_user_response.status_code == 201
        regular_user = regular_user_response.json()
        user_id = regular_user["id"]

        # Promote the user
        response = admin_client.post(f"/admin/users/{user_id}/promote")

        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] is True
        assert data["user_id"] == user_id
        assert "promoted_by" in data
        assert "promoted_at" in data

    def test_admin_can_revoke_privileges(
        self,
        admin_client: httpx.Client,
        http_client: httpx.Client
    ):
        """Admin users can revoke admin privileges from other users"""
        # Create and promote a user
        user_response = http_client.post(
            "/users",
            json={
                "email": "target@example.com",
                "password": "Password123!"
            }
        )
        user_id = user_response.json()["id"]

        # Promote first
        admin_client.post(f"/admin/users/{user_id}/promote")

        # Then revoke
        response = admin_client.post(f"/admin/users/{user_id}/revoke")

        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] is False
        assert data["user_id"] == user_id
        assert "revoked_by" in data
        assert "revoked_at" in data

    def test_admin_cannot_revoke_own_privileges(
        self,
        admin_client: httpx.Client,
        admin_user: dict
    ):
        """Admin users cannot revoke their own admin privileges"""
        response = admin_client.post(
            f"/admin/users/{admin_user['user_id']}/revoke"
        )

        assert response.status_code == 400
        error_data = response.json()
        assert "own" in error_data.get("detail", "").lower()

    def test_promote_already_admin_is_idempotent(
        self,
        admin_client: httpx.Client,
        http_client: httpx.Client
    ):
        """Promoting an already-admin user is a no-op"""
        # Create and promote a user
        user_response = http_client.post(
            "/users",
            json={
                "email": "idempotent@example.com",
                "password": "Password123!"
            }
        )
        user_id = user_response.json()["id"]

        # First promotion
        response1 = admin_client.post(f"/admin/users/{user_id}/promote")
        assert response1.status_code == 200

        # Second promotion (idempotent)
        response2 = admin_client.post(f"/admin/users/{user_id}/promote")
        assert response2.status_code == 200
        data = response2.json()
        assert data["is_admin"] is True
        assert "already" in data["message"].lower()

    def test_revoke_non_admin_is_idempotent(
        self,
        admin_client: httpx.Client,
        http_client: httpx.Client
    ):
        """Revoking from a non-admin user is a no-op"""
        # Create a regular user (not admin)
        user_response = http_client.post(
            "/users",
            json={
                "email": "noadmin@example.com",
                "password": "Password123!"
            }
        )
        user_id = user_response.json()["id"]

        # Attempt revoke on non-admin
        response = admin_client.post(f"/admin/users/{user_id}/revoke")

        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] is False
        assert "not" in data["message"].lower()

    def test_promote_nonexistent_user_fails(self, admin_client: httpx.Client):
        """Promoting a non-existent user returns 404"""
        response = admin_client.post("/admin/users/999999/promote")

        assert response.status_code == 404
        error_data = response.json()
        assert "not found" in error_data.get("detail", "").lower()

    def test_revoke_nonexistent_user_fails(self, admin_client: httpx.Client):
        """Revoking from a non-existent user returns 404"""
        response = admin_client.post("/admin/users/999999/revoke")

        assert response.status_code == 404
        error_data = response.json()
        assert "not found" in error_data.get("detail", "").lower()
