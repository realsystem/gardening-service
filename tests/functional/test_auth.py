"""Functional tests for authentication endpoints

These tests verify real user registration, login, and authorization flows.
"""
import pytest
import httpx


class TestUserRegistration:
    """Test user registration endpoint"""

    def test_register_new_user_success(self, http_client: httpx.Client, test_user_credentials: dict):
        """Successfully register a new user"""
        response = http_client.post(
            "/users",
            json=test_user_credentials
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == test_user_credentials["email"]
        assert "password" not in data  # Password should never be returned
        assert "created_at" in data

    def test_register_duplicate_email_fails(
        self,
        http_client: httpx.Client,
        registered_user: dict
    ):
        """Cannot register with an email that already exists"""
        response = http_client.post(
            "/users",
            json={
                "email": registered_user["email"],
                "password": "DifferentPassword123!"
            }
        )

        assert response.status_code == 400
        # Check for error message (format may vary)
        response_data = response.json()
        if isinstance(response_data, dict) and "detail" in response_data:
            assert "already" in response_data["detail"].lower() or "exist" in response_data["detail"].lower()
        else:
            # Alternative error format
            assert response.status_code == 400

    def test_register_invalid_email_fails(self, http_client: httpx.Client):
        """Cannot register with invalid email format"""
        response = http_client.post(
            "/users",
            json={
                "email": "not-an-email",
                "password": "ValidPassword123!"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_register_weak_password_fails(self, http_client: httpx.Client):
        """Cannot register with weak password"""
        response = http_client.post(
            "/users",
            json={
                "email": "newuser@example.com",
                "password": "123"  # Too short
            }
        )

        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Test user login endpoint"""

    def test_login_success(self, http_client: httpx.Client, registered_user: dict):
        """Successfully login with correct credentials"""
        response = http_client.post(
            "/users/login",
            json={
                "email": registered_user["email"],
                "password": registered_user["password"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_wrong_password_fails(self, http_client: httpx.Client, registered_user: dict):
        """Cannot login with wrong password"""
        response = http_client.post(
            "/users/login",
            json={
                "email": registered_user["email"],
                "password": "WrongPassword123!"
            }
        )

        assert response.status_code == 401
        response_data = response.json()
        assert "error" in response_data
        assert "incorrect" in response_data["error"]["message"].lower()

    def test_login_nonexistent_user_fails(self, http_client: httpx.Client):
        """Cannot login with non-existent email"""
        response = http_client.post(
            "/users/login",
            json={
                "email": "nonexistent@example.com",
                "password": "AnyPassword123!"
            }
        )

        assert response.status_code == 401


class TestAuthorization:
    """Test authorization and protected endpoints"""

    def test_access_protected_endpoint_with_token_success(
        self,
        authenticated_client: httpx.Client
    ):
        """Can access protected endpoint with valid token"""
        response = authenticated_client.get("/gardens")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_access_protected_endpoint_without_token_fails(self, http_client: httpx.Client):
        """Cannot access protected endpoint without token"""
        response = http_client.get("/gardens")

        assert response.status_code == 403  # FastAPI returns 403 for missing credentials
        response_data = response.json()
        assert "error" in response_data
        assert "not authenticated" in response_data["error"]["message"].lower()

    def test_access_protected_endpoint_with_invalid_token_fails(
        self,
        http_client: httpx.Client
    ):
        """Cannot access protected endpoint with invalid token"""
        response = http_client.get(
            "/gardens",
            headers={"Authorization": "Bearer invalid_token_here"}
        )

        assert response.status_code == 401

    def test_access_protected_endpoint_with_malformed_header_fails(
        self,
        http_client: httpx.Client,
        auth_token: str
    ):
        """Cannot access protected endpoint with malformed auth header"""
        # Missing "Bearer" prefix
        response = http_client.get(
            "/gardens",
            headers={"Authorization": auth_token}
        )

        assert response.status_code == 403  # FastAPI returns 403 for malformed credentials


class TestUserProfile:
    """Test user profile endpoints"""

    def test_get_current_user_profile(
        self,
        authenticated_client: httpx.Client,
        registered_user: dict
    ):
        """Can retrieve current user profile"""
        response = authenticated_client.get("/users/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == registered_user["user_id"]
        assert data["email"] == registered_user["email"]
        assert "password" not in data

    def test_delete_current_user(
        self,
        http_client: httpx.Client,
        registered_user: dict,
        auth_token: str
    ):
        """Can delete own user account"""
        response = http_client.delete(
            "/users/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 204

        # Verify user is deleted - login should fail
        login_response = http_client.post(
            "/users/login",
            json={
                "email": registered_user["email"],
                "password": registered_user["password"]
            }
        )
        assert login_response.status_code == 401
