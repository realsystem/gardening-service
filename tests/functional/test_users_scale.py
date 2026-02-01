"""
Multi-User Scale Tests

Tests system behavior with multiple concurrent users:
- User isolation
- Authorization enforcement
- Data segregation
- No cross-user leakage

Simulates 5-10 users with realistic workloads.
"""
import pytest
import httpx
from typing import List, Dict


class TestUserIsolation:
    """Test that users cannot access each other's data"""

    def test_multiple_users_isolation(
        self,
        http_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Verify 5 users with separate gardens - no cross-access"""
        users = []

        # Create 5 users
        for i in range(5):
            email = f"scale_user_{i}@test.com"
            password = f"TestPass{i}123!"

            # Register
            reg_response = http_client.post(
                "/users",
                json={"email": email, "password": password}
            )
            assert reg_response.status_code == 201

            # Login
            login_response = http_client.post(
                "/users/login",
                json={"email": email, "password": password}
            )
            assert login_response.status_code == 200
            token = login_response.json()["access_token"]

            # Create garden for this user
            garden_response = http_client.post(
                "/gardens",
                json={
                    "name": f"User {i} Garden",
                    "garden_type": "outdoor"
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            assert garden_response.status_code == 201
            garden = garden_response.json()
            cleanup_gardens.append(garden["id"])

            users.append({
                "email": email,
                "password": password,
                "token": token,
                "garden_id": garden["id"]
            })

        # Verify isolation: each user should only see their own garden
        for i, user in enumerate(users):
            response = http_client.get(
                "/gardens",
                headers={"Authorization": f"Bearer {user['token']}"}
            )
            assert response.status_code == 200
            gardens = response.json()

            # Should only see 1 garden (their own)
            assert len(gardens) == 1, f"User {i} sees {len(gardens)} gardens, expected 1"
            assert gardens[0]["id"] == user["garden_id"]
            assert gardens[0]["name"] == f"User {i} Garden"

        # Verify no cross-user access: user 0 cannot access user 1's garden
        response = http_client.get(
            f"/gardens/{users[1]['garden_id']}",
            headers={"Authorization": f"Bearer {users[0]['token']}"}
        )
        assert response.status_code == 403, "Should not access other user's garden"


    def test_concurrent_garden_creation(
        self,
        http_client: httpx.Client,
        cleanup_gardens: list
    ):
        """10 users each create 3 gardens - verify isolation"""
        num_users = 10
        gardens_per_user = 3

        all_user_data = []

        # Phase 1: Create users and their gardens
        for user_idx in range(num_users):
            email = f"concurrent_user_{user_idx}@test.com"
            password = f"Pass{user_idx}123!"

            # Register
            http_client.post("/users", json={"email": email, "password": password})

            # Login
            token_response = http_client.post(
                "/users/login",
                json={"email": email, "password": password}
            )
            token = token_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            user_gardens = []
            for garden_idx in range(gardens_per_user):
                garden_response = http_client.post(
                    "/gardens",
                    json={
                        "name": f"User{user_idx}_Garden{garden_idx}",
                        "garden_type": "outdoor"
                    },
                    headers=headers
                )
                assert garden_response.status_code == 201
                garden = garden_response.json()
                user_gardens.append(garden["id"])
                cleanup_gardens.append(garden["id"])

            all_user_data.append({
                "email": email,
                "token": token,
                "garden_ids": user_gardens
            })

        # Phase 2: Verify each user only sees their own gardens
        for user_idx, user_data in enumerate(all_user_data):
            response = http_client.get(
                "/gardens",
                headers={"Authorization": f"Bearer {user_data['token']}"}
            )
            assert response.status_code == 200
            gardens = response.json()

            # Should see exactly gardens_per_user gardens
            assert len(gardens) == gardens_per_user, \
                f"User {user_idx} sees {len(gardens)} gardens, expected {gardens_per_user}"

            # Verify all garden IDs match
            garden_ids = {g["id"] for g in gardens}
            expected_ids = set(user_data["garden_ids"])
            assert garden_ids == expected_ids, \
                f"User {user_idx} garden IDs mismatch"


    def test_user_deletion_cascades(
        self,
        http_client: httpx.Client
    ):
        """When user is deleted, all their data is removed"""
        email = "deleteme@test.com"
        password = "DeletePass123!"

        # Register and login
        http_client.post("/users", json={"email": email, "password": password})
        token_response = http_client.post(
            "/users/login",
            json={"email": email, "password": password}
        )
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create 3 gardens
        garden_ids = []
        for i in range(3):
            garden_response = http_client.post(
                "/gardens",
                json={"name": f"Garden {i}", "garden_type": "outdoor"},
                headers=headers
            )
            garden_ids.append(garden_response.json()["id"])

        # Verify gardens exist
        response = http_client.get("/gardens", headers=headers)
        assert len(response.json()) == 3

        # Delete user
        delete_response = http_client.delete("/users/me", headers=headers)
        assert delete_response.status_code == 204

        # Verify cannot login
        login_attempt = http_client.post(
            "/users/login",
            json={"email": email, "password": password}
        )
        assert login_attempt.status_code == 401

        # Gardens should be inaccessible (cascade delete)
        for garden_id in garden_ids:
            # Try to access with a different user
            other_email = "other@test.com"
            http_client.post("/users", json={"email": other_email, "password": "Pass123!"})
            other_token_response = http_client.post(
                "/users/login",
                json={"email": other_email, "password": "Pass123!"}
            )
            other_token = other_token_response.json()["access_token"]

            response = http_client.get(
                f"/gardens/{garden_id}",
                headers={"Authorization": f"Bearer {other_token}"}
            )
            # Should be either 404 (deleted) or 403 (not yours)
            assert response.status_code in [403, 404]


class TestScaleAuthorization:
    """Test authorization at scale"""

    def test_no_unauthorized_access_at_scale(
        self,
        http_client: httpx.Client,
        cleanup_gardens: list
    ):
        """100 access attempts - all blocked correctly"""
        # Create 2 users
        users = []
        for i in range(2):
            email = f"authtest{i}@test.com"
            password = f"Pass{i}123!"
            http_client.post("/users", json={"email": email, "password": password})
            token_response = http_client.post(
                "/users/login",
                json={"email": email, "password": password}
            )
            token = token_response.json()["access_token"]

            # User 0 creates gardens, User 1 tries to access them
            if i == 0:
                garden_ids = []
                for g_idx in range(10):
                    garden_response = http_client.post(
                        "/gardens",
                        json={"name": f"G{g_idx}", "garden_type": "outdoor"},
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    garden_id = garden_response.json()["id"]
                    garden_ids.append(garden_id)
                    cleanup_gardens.append(garden_id)

                users.append({"token": token, "garden_ids": garden_ids})
            else:
                users.append({"token": token, "garden_ids": []})

        # User 1 tries to access all of User 0's gardens
        blocked_count = 0
        for garden_id in users[0]["garden_ids"]:
            response = http_client.get(
                f"/gardens/{garden_id}",
                headers={"Authorization": f"Bearer {users[1]['token']}"}
            )
            if response.status_code == 403:
                blocked_count += 1

        # All accesses should be blocked
        assert blocked_count == len(users[0]["garden_ids"]), \
            f"Expected all {len(users[0]['garden_ids'])} access attempts blocked, got {blocked_count}"


class TestUserScaling:
    """Test system behavior as user count increases"""

    def test_ten_users_full_workflow(
        self,
        http_client: httpx.Client,
        cleanup_gardens: list
    ):
        """10 users each do full workflow: register, login, create 5 gardens, list, verify"""
        num_users = 10
        gardens_per_user = 5

        successful_workflows = 0

        for user_idx in range(num_users):
            email = f"workflow_user_{user_idx}@test.com"
            password = f"Pass{user_idx}123!"

            # Step 1: Register
            reg_response = http_client.post(
                "/users",
                json={"email": email, "password": password}
            )
            if reg_response.status_code != 201:
                continue

            # Step 2: Login
            login_response = http_client.post(
                "/users/login",
                json={"email": email, "password": password}
            )
            if login_response.status_code != 200:
                continue

            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Step 3: Create gardens
            created_gardens = 0
            for g_idx in range(gardens_per_user):
                garden_response = http_client.post(
                    "/gardens",
                    json={
                        "name": f"U{user_idx}_G{g_idx}",
                        "garden_type": "outdoor",
                        "description": f"Test garden {g_idx} for user {user_idx}"
                    },
                    headers=headers
                )
                if garden_response.status_code == 201:
                    created_gardens += 1
                    cleanup_gardens.append(garden_response.json()["id"])

            # Step 4: List gardens
            list_response = http_client.get("/gardens", headers=headers)
            if list_response.status_code != 200:
                continue

            gardens = list_response.json()

            # Step 5: Verify count
            if len(gardens) == gardens_per_user:
                successful_workflows += 1

        # At least 9/10 users should complete successfully
        assert successful_workflows >= 9, \
            f"Only {successful_workflows}/10 users completed workflow successfully"
