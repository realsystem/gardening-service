"""Functional tests for land layout and garden positioning

These tests verify land creation, garden positioning, and spatial validation.
"""
import pytest
import httpx


@pytest.fixture
def test_land(authenticated_client: httpx.Client, cleanup_lands: list) -> dict:
    """Create a test land for layout tests"""
    response = authenticated_client.post(
        "/lands",
        json={
            "name": "Test Property",
            "width": 50.0,
            "height": 40.0
        }
    )
    land = response.json()
    cleanup_lands.append(land["id"])
    return land


@pytest.fixture
def test_garden(authenticated_client: httpx.Client, cleanup_gardens: list) -> dict:
    """Create a test garden for layout tests"""
    response = authenticated_client.post(
        "/gardens",
        json={"name": "Layout Test Garden", "garden_type": "outdoor"}
    )
    garden = response.json()
    cleanup_gardens.append(garden["id"])
    return garden


class TestLandCreation:
    """Test land creation endpoints"""

    def test_create_land_success(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands: list
    ):
        """Successfully create a land parcel"""
        land_data = {
            "name": "My Garden Plot",
            "width": 100.0,
            "height": 80.0
        }

        response = authenticated_client.post("/lands", json=land_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Garden Plot"
        assert data["width"] == 100.0
        assert data["height"] == 80.0
        assert "id" in data
        assert "user_id" in data

        cleanup_lands.append(data["id"])

    def test_create_land_requires_positive_dimensions(
        self,
        authenticated_client: httpx.Client
    ):
        """Cannot create land with zero or negative dimensions"""
        land_data = {
            "name": "Invalid Land",
            "width": 0.0,
            "height": 50.0
        }

        response = authenticated_client.post("/lands", json=land_data)

        assert response.status_code == 422

    def test_list_user_lands(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands: list
    ):
        """List all lands for current user"""
        # Create 2 lands
        land1 = authenticated_client.post(
            "/lands",
            json={"name": "Land 1", "width": 50.0, "height": 40.0}
        ).json()
        land2 = authenticated_client.post(
            "/lands",
            json={"name": "Land 2", "width": 60.0, "height": 50.0}
        ).json()

        cleanup_lands.extend([land1["id"], land2["id"]])

        # List lands
        response = authenticated_client.get("/lands")

        assert response.status_code == 200
        lands = response.json()
        assert len(lands) == 2

    def test_get_land_with_gardens(
        self,
        authenticated_client: httpx.Client,
        test_land: dict,
        cleanup_gardens: list
    ):
        """Retrieve land with positioned gardens"""
        # Create and position garden on land
        garden = authenticated_client.post(
            "/gardens",
            json={"name": "Positioned Garden", "garden_type": "outdoor"}
        ).json()
        cleanup_gardens.append(garden["id"])

        # Position garden on land
        authenticated_client.put(
            f"/gardens/{garden['id']}/layout",
            json={
                "land_id": test_land["id"],
                "x": 5.0,
                "y": 5.0,
                "width": 10.0,
                "height": 10.0
            }
        )

        # Get land with gardens
        response = authenticated_client.get(f"/lands/{test_land['id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_land["id"]
        assert "gardens" in data
        assert len(data["gardens"]) == 1
        assert data["gardens"][0]["id"] == garden["id"]


class TestGardenPositioning:
    """Test garden positioning on land"""

    def test_position_garden_on_land_success(
        self,
        authenticated_client: httpx.Client,
        test_land: dict,
        test_garden: dict
    ):
        """Successfully position garden on land"""
        layout_data = {
            "land_id": test_land["id"],
            "x": 10.0,
            "y": 10.0,
            "width": 20.0,
            "height": 15.0
        }

        response = authenticated_client.put(
            f"/gardens/{test_garden['id']}/layout",
            json=layout_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["land_id"] == test_land["id"]
        assert data["x"] == 10.0
        assert data["y"] == 10.0
        assert data["width"] == 20.0
        assert data["height"] == 15.0

    def test_update_garden_position(
        self,
        authenticated_client: httpx.Client,
        test_land: dict,
        test_garden: dict
    ):
        """Successfully update garden position"""
        # Initial positioning
        authenticated_client.put(
            f"/gardens/{test_garden['id']}/layout",
            json={
                "land_id": test_land["id"],
                "x": 5.0,
                "y": 5.0,
                "width": 10.0,
                "height": 10.0
            }
        )

        # Update position
        new_layout = {
            "land_id": test_land["id"],
            "x": 15.0,
            "y": 15.0,
            "width": 10.0,
            "height": 10.0
        }

        response = authenticated_client.put(
            f"/gardens/{test_garden['id']}/layout",
            json=new_layout
        )

        assert response.status_code == 200
        data = response.json()
        assert data["x"] == 15.0
        assert data["y"] == 15.0

    def test_remove_garden_from_land(
        self,
        authenticated_client: httpx.Client,
        test_land: dict,
        test_garden: dict
    ):
        """Successfully remove garden from land"""
        # Position garden
        authenticated_client.put(
            f"/gardens/{test_garden['id']}/layout",
            json={
                "land_id": test_land["id"],
                "x": 5.0,
                "y": 5.0,
                "width": 10.0,
                "height": 10.0
            }
        )

        # Remove from land (set all to None)
        response = authenticated_client.put(
            f"/gardens/{test_garden['id']}/layout",
            json={
                "land_id": None,
                "x": None,
                "y": None,
                "width": None,
                "height": None
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["land_id"] is None
        assert data["x"] is None


class TestSpatialValidation:
    """Test spatial validation and boundary checks"""

    def test_reject_garden_exceeding_land_bounds(
        self,
        authenticated_client: httpx.Client,
        test_land: dict,
        test_garden: dict
    ):
        """Cannot position garden outside land boundaries"""
        # Test land is 50x40, try to position 20x15 garden at (45, 30)
        # This would require width up to 65 and height up to 45
        layout_data = {
            "land_id": test_land["id"],
            "x": 45.0,
            "y": 30.0,
            "width": 20.0,
            "height": 15.0
        }

        response = authenticated_client.put(
            f"/gardens/{test_garden['id']}/layout",
            json=layout_data
        )

        assert response.status_code == 400
        assert "bounds" in response.json()["detail"].lower()

    def test_reject_negative_coordinates(
        self,
        authenticated_client: httpx.Client,
        test_land: dict,
        test_garden: dict
    ):
        """Cannot position garden with negative coordinates"""
        layout_data = {
            "land_id": test_land["id"],
            "x": -5.0,
            "y": 5.0,
            "width": 10.0,
            "height": 10.0
        }

        response = authenticated_client.put(
            f"/gardens/{test_garden['id']}/layout",
            json=layout_data
        )

        assert response.status_code == 422  # Validation error

    def test_reject_zero_dimensions(
        self,
        authenticated_client: httpx.Client,
        test_land: dict,
        test_garden: dict
    ):
        """Cannot position garden with zero width or height"""
        layout_data = {
            "land_id": test_land["id"],
            "x": 5.0,
            "y": 5.0,
            "width": 0.0,
            "height": 10.0
        }

        response = authenticated_client.put(
            f"/gardens/{test_garden['id']}/layout",
            json=layout_data
        )

        assert response.status_code == 422

    def test_reject_overlapping_gardens(
        self,
        authenticated_client: httpx.Client,
        test_land: dict,
        cleanup_gardens: list
    ):
        """Cannot position overlapping gardens"""
        # Create and position first garden
        garden1 = authenticated_client.post(
            "/gardens",
            json={"name": "Garden 1", "garden_type": "outdoor"}
        ).json()
        cleanup_gardens.append(garden1["id"])

        authenticated_client.put(
            f"/gardens/{garden1['id']}/layout",
            json={
                "land_id": test_land["id"],
                "x": 10.0,
                "y": 10.0,
                "width": 15.0,
                "height": 15.0
            }
        )

        # Create second garden and try to overlap
        garden2 = authenticated_client.post(
            "/gardens",
            json={"name": "Garden 2", "garden_type": "outdoor"}
        ).json()
        cleanup_gardens.append(garden2["id"])

        # Try to position with overlap (15, 15 would overlap with first garden)
        response = authenticated_client.put(
            f"/gardens/{garden2['id']}/layout",
            json={
                "land_id": test_land["id"],
                "x": 15.0,
                "y": 15.0,
                "width": 10.0,
                "height": 10.0
            }
        )

        assert response.status_code == 400
        assert "overlap" in response.json()["detail"].lower()

    def test_allow_adjacent_gardens(
        self,
        authenticated_client: httpx.Client,
        test_land: dict,
        cleanup_gardens: list
    ):
        """Allow gardens placed adjacent (touching but not overlapping)"""
        # Create and position first garden
        garden1 = authenticated_client.post(
            "/gardens",
            json={"name": "Garden 1", "garden_type": "outdoor"}
        ).json()
        cleanup_gardens.append(garden1["id"])

        authenticated_client.put(
            f"/gardens/{garden1['id']}/layout",
            json={
                "land_id": test_land["id"],
                "x": 10.0,
                "y": 10.0,
                "width": 10.0,
                "height": 10.0
            }
        )

        # Position second garden adjacent (touching edge)
        garden2 = authenticated_client.post(
            "/gardens",
            json={"name": "Garden 2", "garden_type": "outdoor"}
        ).json()
        cleanup_gardens.append(garden2["id"])

        response = authenticated_client.put(
            f"/gardens/{garden2['id']}/layout",
            json={
                "land_id": test_land["id"],
                "x": 20.0,  # Starts where garden1 ends
                "y": 10.0,
                "width": 10.0,
                "height": 10.0
            }
        )

        assert response.status_code == 200


class TestLandUpdate:
    """Test land dimension updates"""

    def test_update_land_dimensions(
        self,
        authenticated_client: httpx.Client,
        test_land: dict
    ):
        """Successfully update land dimensions"""
        update_data = {
            "width": 60.0,
            "height": 50.0
        }

        response = authenticated_client.patch(
            f"/lands/{test_land['id']}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["width"] == 60.0
        assert data["height"] == 50.0

    def test_reject_dimension_reduction_with_gardens(
        self,
        authenticated_client: httpx.Client,
        test_land: dict,
        cleanup_gardens: list
    ):
        """Cannot reduce land dimensions if gardens would be out of bounds"""
        # Position garden near edge
        garden = authenticated_client.post(
            "/gardens",
            json={"name": "Edge Garden", "garden_type": "outdoor"}
        ).json()
        cleanup_gardens.append(garden["id"])

        authenticated_client.put(
            f"/gardens/{garden['id']}/layout",
            json={
                "land_id": test_land["id"],
                "x": 35.0,
                "y": 25.0,
                "width": 10.0,
                "height": 10.0
            }
        )

        # Try to reduce land to 40x30 (would make garden out of bounds)
        response = authenticated_client.patch(
            f"/lands/{test_land['id']}",
            json={
                "width": 40.0,
                "height": 30.0
            }
        )

        assert response.status_code == 400
        assert "exceed" in response.json()["detail"].lower()


class TestLandDeletion:
    """Test land deletion"""

    def test_delete_land_success(
        self,
        authenticated_client: httpx.Client
    ):
        """Successfully delete a land"""
        land = authenticated_client.post(
            "/lands",
            json={"name": "Land to Delete", "width": 50.0, "height": 40.0}
        ).json()

        response = authenticated_client.delete(f"/lands/{land['id']}")

        assert response.status_code == 204

    def test_delete_land_orphans_gardens(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list,
        cleanup_lands: list
    ):
        """Deleting land orphans gardens (sets land_id to NULL)"""
        # Create land
        land = authenticated_client.post(
            "/lands",
            json={"name": "Temp Land", "width": 50.0, "height": 40.0}
        ).json()
        cleanup_lands.append(land["id"])

        # Create and position garden
        garden = authenticated_client.post(
            "/gardens",
            json={"name": "Garden", "garden_type": "outdoor"}
        ).json()
        cleanup_gardens.append(garden["id"])

        authenticated_client.put(
            f"/gardens/{garden['id']}/layout",
            json={
                "land_id": land["id"],
                "x": 10.0,
                "y": 10.0,
                "width": 10.0,
                "height": 10.0
            }
        )

        # Delete land
        authenticated_client.delete(f"/lands/{land['id']}")

        # Verify garden exists but is orphaned
        garden_response = authenticated_client.get(f"/gardens/{garden['id']}")
        garden_data = garden_response.json()
        assert garden_data["garden"]["land_id"] is None
