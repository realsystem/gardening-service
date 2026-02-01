"""Functional tests for garden endpoints

These tests verify garden creation, listing, updating, and deletion.
"""
import pytest
import httpx


class TestGardenCreation:
    """Test garden creation endpoint"""

    def test_create_outdoor_garden_success(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Successfully create an outdoor garden"""
        garden_data = {
            "name": "Test Vegetable Garden",
            "description": "A test garden for veggies",
            "garden_type": "outdoor"
        }

        response = authenticated_client.post("/gardens", json=garden_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == garden_data["name"]
        assert data["garden_type"] == "outdoor"
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data

        cleanup_gardens.append(data["id"])

    def test_create_indoor_garden_with_details(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Create indoor garden with full configuration"""
        garden_data = {
            "name": "Indoor Herb Garden",
            "garden_type": "indoor",
            "location": "Kitchen Window",
            "light_source_type": "led",
            "light_hours_per_day": 16.0,
            "temp_min_f": 65.0,
            "temp_max_f": 75.0,
            "humidity_min_percent": 40.0,
            "humidity_max_percent": 60.0,
            "container_type": "Pots",
            "grow_medium": "Potting mix"
        }

        response = authenticated_client.post("/gardens", json=garden_data)

        assert response.status_code == 201
        data = response.json()
        assert data["garden_type"] == "indoor"
        assert data["light_source_type"] == "led"
        assert data["light_hours_per_day"] == 16.0

        cleanup_gardens.append(data["id"])

    def test_create_hydroponic_garden(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Create hydroponic garden with system details"""
        garden_data = {
            "name": "Hydroponic Lettuce",
            "garden_type": "indoor",
            "is_hydroponic": True,
            "hydro_system_type": "nft",
            "reservoir_size_liters": 50.0,
            "ph_min": 5.5,
            "ph_max": 6.5,
            "ec_min": 1.2,
            "ec_max": 1.8
        }

        response = authenticated_client.post("/gardens", json=garden_data)

        assert response.status_code == 201
        data = response.json()
        assert data["is_hydroponic"] is True
        assert data["hydro_system_type"] == "nft"

        cleanup_gardens.append(data["id"])

    def test_create_garden_requires_authentication(self, http_client: httpx.Client):
        """Cannot create garden without authentication"""
        response = http_client.post(
            "/gardens",
            json={"name": "Unauthorized Garden", "garden_type": "outdoor"}
        )

        assert response.status_code == 401


class TestGardenListing:
    """Test garden listing endpoint"""

    def test_list_gardens_empty(self, authenticated_client: httpx.Client):
        """List gardens returns empty array when user has no gardens"""
        response = authenticated_client.get("/gardens")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_gardens_returns_user_gardens_only(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """List gardens returns only current user's gardens"""
        # Create 2 gardens
        garden1 = authenticated_client.post(
            "/gardens",
            json={"name": "Garden 1", "garden_type": "outdoor"}
        ).json()
        garden2 = authenticated_client.post(
            "/gardens",
            json={"name": "Garden 2", "garden_type": "indoor"}
        ).json()

        cleanup_gardens.extend([garden1["id"], garden2["id"]])

        # List gardens
        response = authenticated_client.get("/gardens")

        assert response.status_code == 200
        gardens = response.json()
        assert len(gardens) == 2
        assert any(g["name"] == "Garden 1" for g in gardens)
        assert any(g["name"] == "Garden 2" for g in gardens)


class TestGardenRetrieval:
    """Test individual garden retrieval"""

    def test_get_garden_by_id_success(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Successfully retrieve garden by ID"""
        # Create garden
        create_response = authenticated_client.post(
            "/gardens",
            json={"name": "Test Garden", "garden_type": "outdoor"}
        )
        garden_id = create_response.json()["id"]
        cleanup_gardens.append(garden_id)

        # Retrieve garden
        response = authenticated_client.get(f"/gardens/{garden_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == garden_id
        assert data["name"] == "Test Garden"

    def test_get_nonexistent_garden_fails(self, authenticated_client: httpx.Client):
        """Cannot retrieve garden that doesn't exist"""
        response = authenticated_client.get("/gardens/99999")

        assert response.status_code == 404

    def test_get_other_user_garden_fails(
        self,
        http_client: httpx.Client,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Cannot retrieve another user's garden"""
        # Create garden as user 1
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "User 1 Garden", "garden_type": "outdoor"}
        )
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        # Register and login as different user
        user2_email = "user2@example.com"
        http_client.post(
            "/users",
            json={"email": user2_email, "password": "Password123!"}
        )
        token_response = http_client.post(
            "/users/login",
            json={"email": user2_email, "password": "Password123!"}
        )
        user2_token = token_response.json()["access_token"]

        # Try to access user 1's garden as user 2
        response = http_client.get(
            f"/gardens/{garden_id}",
            headers={"Authorization": f"Bearer {user2_token}"}
        )

        assert response.status_code == 403


class TestGardenUpdate:
    """Test garden update endpoint"""

    def test_update_garden_success(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Successfully update garden properties"""
        # Create garden
        garden = authenticated_client.post(
            "/gardens",
            json={"name": "Original Name", "garden_type": "outdoor"}
        ).json()
        cleanup_gardens.append(garden["id"])

        # Update garden
        update_data = {
            "name": "Updated Name",
            "description": "New description"
        }
        response = authenticated_client.patch(
            f"/gardens/{garden['id']}",
            json=update_data
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["name"] == "Updated Name"
        assert updated["description"] == "New description"

    def test_update_nonexistent_garden_fails(self, authenticated_client: httpx.Client):
        """Cannot update garden that doesn't exist"""
        response = authenticated_client.patch(
            "/gardens/99999",
            json={"name": "New Name"}
        )

        assert response.status_code == 404


class TestGardenDeletion:
    """Test garden deletion endpoint"""

    def test_delete_garden_success(
        self,
        authenticated_client: httpx.Client
    ):
        """Successfully delete a garden"""
        # Create garden
        garden = authenticated_client.post(
            "/gardens",
            json={"name": "Garden to Delete", "garden_type": "outdoor"}
        ).json()

        # Delete garden
        response = authenticated_client.delete(f"/gardens/{garden['id']}")

        assert response.status_code == 204

        # Verify deletion
        get_response = authenticated_client.get(f"/gardens/{garden['id']}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_garden_fails(self, authenticated_client: httpx.Client):
        """Cannot delete garden that doesn't exist"""
        response = authenticated_client.delete("/gardens/99999")

        assert response.status_code == 404

    def test_delete_other_user_garden_fails(
        self,
        http_client: httpx.Client,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Cannot delete another user's garden"""
        # Create garden as user 1
        garden = authenticated_client.post(
            "/gardens",
            json={"name": "User 1 Garden", "garden_type": "outdoor"}
        ).json()
        cleanup_gardens.append(garden["id"])

        # Register and login as different user
        http_client.post(
            "/users",
            json={"email": "deleter@example.com", "password": "Password123!"}
        )
        token_response = http_client.post(
            "/users/login",
            json={"email": "deleter@example.com", "password": "Password123!"}
        )
        user2_token = token_response.json()["access_token"]

        # Try to delete user 1's garden as user 2
        response = http_client.delete(
            f"/gardens/{garden['id']}",
            headers={"Authorization": f"Bearer {user2_token}"}
        )

        assert response.status_code == 403
