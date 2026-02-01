"""
Functional tests for tree shading feature

Tests the complete tree shading workflow:
- Tree CRUD operations
- Shading impact calculations via API
- Multi-user isolation
- Overlapping trees scenarios

Uses pytest markers for selective test execution:
- pytest -m tree_shading
- pytest -m tree_shading_integration
"""
import pytest
import httpx


pytestmark = pytest.mark.tree_shading


class TestTreeCRUD:
    """Test tree Create, Read, Update, Delete operations"""

    def test_create_tree_success(self, authenticated_client: httpx.Client, test_land: dict):
        """Create a tree on user's land"""
        tree_data = {
            "land_id": test_land["id"],
            "name": "Oak in Backyard",
            "species_id": None,  # Optional
            "x": 5.0,
            "y": 5.0,
            "canopy_radius": 3.0,
            "height": 15.0
        }

        response = authenticated_client.post("/trees", json=tree_data)

        assert response.status_code == 201
        tree = response.json()
        assert tree["name"] == "Oak in Backyard"
        assert tree["x"] == 5.0
        assert tree["y"] == 5.0
        assert tree["canopy_radius"] == 3.0
        assert tree["land_id"] == test_land["id"]

    def test_create_tree_on_nonexistent_land_fails(self, authenticated_client: httpx.Client):
        """Cannot create tree on land that doesn't exist"""
        tree_data = {
            "land_id": 99999,  # Non-existent
            "name": "Tree",
            "x": 0,
            "y": 0,
            "canopy_radius": 1
        }

        response = authenticated_client.post("/trees", json=tree_data)
        assert response.status_code == 404

    def test_list_user_trees(self, authenticated_client: httpx.Client, test_land: dict):
        """List all trees for current user"""
        # Create two trees
        for i in range(2):
            tree_data = {
                "land_id": test_land["id"],
                "name": f"Tree {i}",
                "x": float(i * 5),
                "y": float(i * 5),
                "canopy_radius": 2.0
            }
            authenticated_client.post("/trees", json=tree_data)

        response = authenticated_client.get("/trees")
        assert response.status_code == 200
        trees = response.json()
        assert len(trees) >= 2

    def test_get_land_trees(self, authenticated_client: httpx.Client, test_land: dict):
        """Get all trees on a specific land plot"""
        # Create tree
        tree_data = {
            "land_id": test_land["id"],
            "name": "Pine Tree",
            "x": 10.0,
            "y": 10.0,
            "canopy_radius": 4.0
        }
        create_response = authenticated_client.post("/trees", json=tree_data)
        assert create_response.status_code == 201

        # Get trees on land
        response = authenticated_client.get(f"/trees/land/{test_land['id']}")
        assert response.status_code == 200
        trees = response.json()
        assert len(trees) >= 1
        assert any(t["name"] == "Pine Tree" for t in trees)

    def test_update_tree(self, authenticated_client: httpx.Client, test_land: dict):
        """Update tree properties"""
        # Create tree
        tree_data = {
            "land_id": test_land["id"],
            "name": "Young Oak",
            "x": 5.0,
            "y": 5.0,
            "canopy_radius": 2.0
        }
        create_response = authenticated_client.post("/trees", json=tree_data)
        tree_id = create_response.json()["id"]

        # Update tree (simulate growth)
        update_data = {
            "name": "Mature Oak",
            "canopy_radius": 5.0
        }
        response = authenticated_client.patch(f"/trees/{tree_id}", json=update_data)

        assert response.status_code == 200
        updated_tree = response.json()
        assert updated_tree["name"] == "Mature Oak"
        assert updated_tree["canopy_radius"] == 5.0
        assert updated_tree["x"] == 5.0  # Unchanged

    def test_delete_tree(self, authenticated_client: httpx.Client, test_land: dict):
        """Delete a tree"""
        # Create tree
        tree_data = {
            "land_id": test_land["id"],
            "name": "Dead Tree",
            "x": 0,
            "y": 0,
            "canopy_radius": 1
        }
        create_response = authenticated_client.post("/trees", json=tree_data)
        tree_id = create_response.json()["id"]

        # Delete tree
        response = authenticated_client.delete(f"/trees/{tree_id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = authenticated_client.get(f"/trees/{tree_id}")
        assert get_response.status_code == 404


@pytest.mark.tree_shading_integration
class TestShadingCalculations:
    """Test shading impact calculations"""

    def test_garden_shading_no_trees(self, authenticated_client: httpx.Client, test_land: dict):
        """Garden with no trees has full sun exposure"""
        # Create garden with spatial layout
        garden_data = {
            "name": "Sunny Garden",
            "land_id": test_land["id"],
            "x": 0,
            "y": 0,
            "width": 10,
            "height": 10
        }
        garden_response = authenticated_client.post("/gardens", json=garden_data)
        garden_id = garden_response.json()["id"]

        # Get shading info
        response = authenticated_client.get(f"/gardens/{garden_id}/shading")

        assert response.status_code == 200
        shading = response.json()
        assert shading["sun_exposure_score"] == 1.0
        assert shading["sun_exposure_category"] == "full_sun"
        assert shading["total_shade_factor"] == 0.0
        assert len(shading["contributing_trees"]) == 0

    def test_garden_shading_with_tree(self, authenticated_client: httpx.Client, test_land: dict):
        """Tree creates shade on nearby garden"""
        # Create garden
        garden_data = {
            "name": "Shaded Garden",
            "land_id": test_land["id"],
            "x": 0,
            "y": 0,
            "width": 10,
            "height": 10
        }
        garden_response = authenticated_client.post("/gardens", json=garden_data)
        garden_id = garden_response.json()["id"]

        # Create tree overlapping garden
        tree_data = {
            "land_id": test_land["id"],
            "name": "Large Oak",
            "x": 5,  # Center of garden
            "y": 5,
            "canopy_radius": 6  # Covers most of garden
        }
        authenticated_client.post("/trees", json=tree_data)

        # Get shading info
        response = authenticated_client.get(f"/gardens/{garden_id}/shading")

        assert response.status_code == 200
        shading = response.json()

        # Should have significant shade
        assert shading["sun_exposure_score"] < 0.8
        assert shading["sun_exposure_category"] in ["partial_sun", "shade"]
        assert shading["total_shade_factor"] > 0.2
        assert len(shading["contributing_trees"]) == 1
        assert shading["contributing_trees"][0]["tree_name"] == "Large Oak"

    def test_garden_shading_multiple_trees(self, authenticated_client: httpx.Client, test_land: dict):
        """Multiple trees create cumulative shading"""
        # Create garden
        garden_data = {
            "name": "Heavily Shaded Garden",
            "land_id": test_land["id"],
            "x": 0,
            "y": 0,
            "width": 10,
            "height": 10
        }
        garden_response = authenticated_client.post("/gardens", json=garden_data)
        garden_id = garden_response.json()["id"]

        # Create multiple trees around garden
        trees = [
            {"name": "Oak NW", "x": 2, "y": 2, "canopy_radius": 3},
            {"name": "Oak NE", "x": 8, "y": 2, "canopy_radius": 3},
            {"name": "Oak SW", "x": 2, "y": 8, "canopy_radius": 3},
        ]

        for tree_data in trees:
            tree_data["land_id"] = test_land["id"]
            authenticated_client.post("/trees", json=tree_data)

        # Get shading info
        response = authenticated_client.get(f"/gardens/{garden_id}/shading")

        assert response.status_code == 200
        shading = response.json()

        # Should have significant cumulative shade
        assert shading["total_shade_factor"] > 0.3
        assert len(shading["contributing_trees"]) == 3

    def test_garden_without_layout_fails(self, authenticated_client: httpx.Client):
        """Cannot calculate shading for garden without spatial layout"""
        # Create garden without land_id/spatial data
        garden_data = {
            "name": "Indoor Garden"
        }
        garden_response = authenticated_client.post("/gardens", json=garden_data)
        garden_id = garden_response.json()["id"]

        # Try to get shading
        response = authenticated_client.get(f"/gardens/{garden_id}/shading")

        assert response.status_code == 400
        assert "spatial layout" in response.json()["detail"].lower()

    def test_tree_far_from_garden_no_impact(self, authenticated_client: httpx.Client, test_land: dict):
        """Distant tree doesn't affect garden"""
        # Create garden at origin
        garden_data = {
            "name": "Garden",
            "land_id": test_land["id"],
            "x": 0,
            "y": 0,
            "width": 5,
            "height": 5
        }
        garden_response = authenticated_client.post("/gardens", json=garden_data)
        garden_id = garden_response.json()["id"]

        # Create tree far away
        tree_data = {
            "land_id": test_land["id"],
            "name": "Distant Tree",
            "x": 100,  # Far from garden
            "y": 100,
            "canopy_radius": 5
        }
        authenticated_client.post("/trees", json=tree_data)

        # Get shading
        response = authenticated_client.get(f"/gardens/{garden_id}/shading")

        shading = response.json()
        assert shading["sun_exposure_score"] == 1.0
        assert len(shading["contributing_trees"]) == 0


@pytest.mark.tree_shading_isolation
class TestMultiUserIsolation:
    """Test that tree shading respects user boundaries"""

    def test_users_only_see_own_trees(self, http_client: httpx.Client, test_land: dict):
        """Users can only see and manage their own trees"""
        # Register two users
        user1 = {
            "email": "user1@example.com",
            "password": "Password123!"
        }
        user2 = {
            "email": "user2@example.com",
            "password": "Password123!"
        }

        http_client.post("/users/register", json=user1)
        http_client.post("/users/register", json=user2)

        # Login as user1
        login1_response = http_client.post("/users/login", json=user1)
        token1 = login1_response.json()["access_token"]

        # Create land and tree for user1
        land1_response = http_client.post(
            "/lands",
            headers={"Authorization": f"Bearer {token1}"},
            json={"name": "User1 Land", "width": 100, "height": 100}
        )
        land1_id = land1_response.json()["id"]

        tree_response = http_client.post(
            "/trees",
            headers={"Authorization": f"Bearer {token1}"},
            json={
                "land_id": land1_id,
                "name": "User1 Tree",
                "x": 5,
                "y": 5,
                "canopy_radius": 3
            }
        )
        tree_id = tree_response.json()["id"]

        # Login as user2
        login2_response = http_client.post("/users/login", json=user2)
        token2 = login2_response.json()["access_token"]

        # User2 cannot access user1's tree
        get_response = http_client.get(
            f"/trees/{tree_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert get_response.status_code == 403

        # User2's tree list is empty
        list_response = http_client.get(
            "/trees",
            headers={"Authorization": f"Bearer {token2}"}
        )
        user2_trees = list_response.json()
        assert len([t for t in user2_trees if t["name"] == "User1 Tree"]) == 0


@pytest.mark.tree_shading_scale
class TestShadingAtScale:
    """Test shading calculations with many trees and gardens"""

    def test_many_trees_on_one_garden(self, authenticated_client: httpx.Client, test_land: dict):
        """Garden can handle shading from many trees"""
        # Create garden
        garden_data = {
            "name": "Test Garden",
            "land_id": test_land["id"],
            "x": 40,
            "y": 40,
            "width": 20,
            "height": 20
        }
        garden_response = authenticated_client.post("/gardens", json=garden_data)
        garden_id = garden_response.json()["id"]

        # Create 10 trees around garden
        for i in range(10):
            tree_data = {
                "land_id": test_land["id"],
                "name": f"Tree {i}",
                "x": 40 + (i % 5) * 10,
                "y": 40 + (i // 5) * 10,
                "canopy_radius": 5
            }
            authenticated_client.post("/trees", json=tree_data)

        # Calculate shading (should not timeout or error)
        response = authenticated_client.get(f"/gardens/{garden_id}/shading")

        assert response.status_code == 200
        shading = response.json()
        assert shading["total_shade_factor"] >= 0
        assert shading["total_shade_factor"] <= 1.0
        # Should detect multiple contributing trees
        assert len(shading["contributing_trees"]) > 0
