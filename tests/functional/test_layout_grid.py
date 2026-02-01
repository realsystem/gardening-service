"""Functional tests for layout grid system

Tests garden placement with snap-to-grid functionality via HTTP API.
All tests marked with @pytest.mark.layout_grid for easy filtering.
"""
import pytest
import httpx


pytestmark = pytest.mark.layout_grid


class TestGridSnapping:
    """Test snap-to-grid behavior via API"""

    def test_create_land_for_grid_tests(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands
    ):
        """Create a land plot for grid testing"""
        response = authenticated_client.post(
            "/lands",
            json={
                "name": "Grid Test Land",
                "width": 10.0,
                "height": 10.0
            }
        )
        assert response.status_code == 201
        land = response.json()
        cleanup_lands.append(land["id"])
        assert land["width"] == 10.0
        assert land["height"] == 10.0

    def test_place_garden_with_snap_enabled(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands,
        cleanup_gardens
    ):
        """Gardens should snap to 0.1 grid when snap_to_grid=True"""
        # Create land
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "Snap Test", "width": 10.0, "height": 10.0}
        )
        land = land_response.json()
        cleanup_lands.append(land["id"])

        # Create garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Snapped Garden", "garden_type": "outdoor"}
        )
        garden = garden_response.json()
        cleanup_gardens.append(garden["id"])

        # Place garden with unaligned coordinates and snap enabled
        layout_response = authenticated_client.put(
            f"/gardens/{garden['id']}/layout",
            json={
                "land_id": land["id"],
                "x": 1.234,  # Should snap to 1.2
                "y": 2.567,  # Should snap to 2.6
                "width": 3.149,  # Should snap to 3.1
                "height": 4.298,  # Should snap to 4.3
                "snap_to_grid": True
            }
        )

        assert layout_response.status_code == 200
        updated_garden = layout_response.json()

        # Verify coordinates were snapped to 0.1 grid
        assert updated_garden["x"] == 1.2
        assert updated_garden["y"] == 2.6
        assert updated_garden["width"] == 3.1
        assert updated_garden["height"] == 4.3

    def test_place_garden_with_snap_disabled(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands,
        cleanup_gardens
    ):
        """Gardens should preserve exact coordinates when snap_to_grid=False"""
        # Create land
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "No Snap Test", "width": 10.0, "height": 10.0}
        )
        land = land_response.json()
        cleanup_lands.append(land["id"])

        # Create garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Unsnapped Garden", "garden_type": "outdoor"}
        )
        garden = garden_response.json()
        cleanup_gardens.append(garden["id"])

        # Place garden with snap disabled
        layout_response = authenticated_client.put(
            f"/gardens/{garden['id']}/layout",
            json={
                "land_id": land["id"],
                "x": 1.234,  # Should remain 1.234
                "y": 2.567,  # Should remain 2.567
                "width": 3.149,  # Should remain 3.149
                "height": 4.298,  # Should remain 4.298
                "snap_to_grid": False
            }
        )

        assert layout_response.status_code == 200
        updated_garden = layout_response.json()

        # Verify exact coordinates were preserved
        assert updated_garden["x"] == 1.234
        assert updated_garden["y"] == 2.567
        assert updated_garden["width"] == 3.149
        assert updated_garden["height"] == 4.298

    def test_snap_defaults_to_enabled(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands,
        cleanup_gardens
    ):
        """Snapping should be enabled by default when not specified"""
        # Create land
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "Default Snap Test", "width": 10.0, "height": 10.0}
        )
        land = land_response.json()
        cleanup_lands.append(land["id"])

        # Create garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Default Snap Garden", "garden_type": "outdoor"}
        )
        garden = garden_response.json()
        cleanup_gardens.append(garden["id"])

        # Place garden without specifying snap_to_grid (should default to True)
        layout_response = authenticated_client.put(
            f"/gardens/{garden['id']}/layout",
            json={
                "land_id": land["id"],
                "x": 1.234,
                "y": 2.567,
                "width": 3.149,
                "height": 4.298
                # snap_to_grid not specified, should default to True
            }
        )

        assert layout_response.status_code == 200
        updated_garden = layout_response.json()

        # Should be snapped (default behavior)
        assert updated_garden["x"] == 1.2
        assert updated_garden["y"] == 2.6


class TestBoundaryEnforcement:
    """Test that snapped gardens respect land boundaries"""

    def test_snapped_garden_within_bounds_succeeds(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands,
        cleanup_gardens
    ):
        """Snapped garden within land boundaries should be accepted"""
        # Create 10×10 land
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "Bounds Test", "width": 10.0, "height": 10.0}
        )
        land = land_response.json()
        cleanup_lands.append(land["id"])

        # Create garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Bounded Garden", "garden_type": "outdoor"}
        )
        garden = garden_response.json()
        cleanup_gardens.append(garden["id"])

        # Place garden that fits after snapping
        layout_response = authenticated_client.put(
            f"/gardens/{garden['id']}/layout",
            json={
                "land_id": land["id"],
                "x": 7.99,  # Snaps to 8.0
                "y": 7.98,  # Snaps to 8.0
                "width": 2.01,  # Snaps to 2.0
                "height": 2.02,  # Snaps to 2.0
                "snap_to_grid": True
            }
        )

        assert layout_response.status_code == 200
        updated_garden = layout_response.json()
        # Garden at (8.0, 8.0) with size (2.0, 2.0) fits in 10×10 land
        assert updated_garden["x"] == 8.0
        assert updated_garden["y"] == 8.0

    def test_snapped_garden_exceeds_bounds_fails(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands,
        cleanup_gardens
    ):
        """Snapped garden exceeding land boundaries should be rejected"""
        # Create 10×10 land
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "Bounds Exceed Test", "width": 10.0, "height": 10.0}
        )
        land = land_response.json()
        cleanup_lands.append(land["id"])

        # Create garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Oversize Garden", "garden_type": "outdoor"}
        )
        garden = garden_response.json()
        cleanup_gardens.append(garden["id"])

        # Place garden that exceeds bounds after snapping
        layout_response = authenticated_client.put(
            f"/gardens/{garden['id']}/layout",
            json={
                "land_id": land["id"],
                "x": 8.1,  # Snaps to 8.1
                "y": 8.1,  # Snaps to 8.1
                "width": 2.1,  # Snaps to 2.1
                "height": 2.1,  # Snaps to 2.1
                "snap_to_grid": True
            }
        )

        # Should fail because 8.1 + 2.1 = 10.2 > 10.0
        assert layout_response.status_code == 400
        error = layout_response.json()
        assert "exceed" in error["detail"].lower() or "bound" in error["detail"].lower()

    def test_garden_at_grid_origin(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands,
        cleanup_gardens
    ):
        """Garden snapped to origin (0, 0) should be valid"""
        # Create land
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "Origin Test", "width": 10.0, "height": 10.0}
        )
        land = land_response.json()
        cleanup_lands.append(land["id"])

        # Create garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Origin Garden", "garden_type": "outdoor"}
        )
        garden = garden_response.json()
        cleanup_gardens.append(garden["id"])

        # Place at near-origin coordinates
        layout_response = authenticated_client.put(
            f"/gardens/{garden['id']}/layout",
            json={
                "land_id": land["id"],
                "x": 0.01,  # Snaps to 0.0
                "y": 0.02,  # Snaps to 0.0
                "width": 2.0,
                "height": 2.0,
                "snap_to_grid": True
            }
        )

        assert layout_response.status_code == 200
        updated_garden = layout_response.json()
        assert updated_garden["x"] == 0.0
        assert updated_garden["y"] == 0.0


class TestOverlapPrevention:
    """Test that snapped gardens cannot overlap"""

    def test_adjacent_snapped_gardens_no_overlap(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands,
        cleanup_gardens
    ):
        """Adjacent gardens after snapping should not overlap"""
        # Create land
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "Adjacent Test", "width": 10.0, "height": 10.0}
        )
        land = land_response.json()
        cleanup_lands.append(land["id"])

        # Create first garden
        garden1_response = authenticated_client.post(
            "/gardens",
            json={"name": "Garden 1", "garden_type": "outdoor"}
        )
        garden1 = garden1_response.json()
        cleanup_gardens.append(garden1["id"])

        # Place first garden at (0, 0) with size (2, 2)
        authenticated_client.put(
            f"/gardens/{garden1['id']}/layout",
            json={
                "land_id": land["id"],
                "x": 0.0,
                "y": 0.0,
                "width": 2.0,
                "height": 2.0,
                "snap_to_grid": True
            }
        )

        # Create second garden
        garden2_response = authenticated_client.post(
            "/gardens",
            json={"name": "Garden 2", "garden_type": "outdoor"}
        )
        garden2 = garden2_response.json()
        cleanup_gardens.append(garden2["id"])

        # Place second garden adjacent (touching but not overlapping)
        layout_response = authenticated_client.put(
            f"/gardens/{garden2['id']}/layout",
            json={
                "land_id": land["id"],
                "x": 2.0,  # Starts where garden1 ends
                "y": 0.0,
                "width": 2.0,
                "height": 2.0,
                "snap_to_grid": True
            }
        )

        # Should succeed - gardens are touching but not overlapping
        assert layout_response.status_code == 200

    def test_overlapping_snapped_gardens_rejected(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands,
        cleanup_gardens
    ):
        """Overlapping gardens after snapping should be rejected"""
        # Create land
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "Overlap Test", "width": 10.0, "height": 10.0}
        )
        land = land_response.json()
        cleanup_lands.append(land["id"])

        # Create first garden
        garden1_response = authenticated_client.post(
            "/gardens",
            json={"name": "Garden 1", "garden_type": "outdoor"}
        )
        garden1 = garden1_response.json()
        cleanup_gardens.append(garden1["id"])

        # Place first garden
        authenticated_client.put(
            f"/gardens/{garden1['id']}/layout",
            json={
                "land_id": land["id"],
                "x": 0.0,
                "y": 0.0,
                "width": 3.0,
                "height": 3.0,
                "snap_to_grid": True
            }
        )

        # Create second garden
        garden2_response = authenticated_client.post(
            "/gardens",
            json={"name": "Garden 2", "garden_type": "outdoor"}
        )
        garden2 = garden2_response.json()
        cleanup_gardens.append(garden2["id"])

        # Try to place garden that overlaps
        layout_response = authenticated_client.put(
            f"/gardens/{garden2['id']}/layout",
            json={
                "land_id": land["id"],
                "x": 1.0,  # Overlaps with garden1 (0-3)
                "y": 1.0,
                "width": 2.0,
                "height": 2.0,
                "snap_to_grid": True
            }
        )

        # Should fail due to overlap
        assert layout_response.status_code == 400
        error = layout_response.json()
        assert "overlap" in error["detail"].lower()


class TestBackwardCompatibility:
    """Test that existing layouts (created before grid feature) still work"""

    def test_existing_unsnapped_layout_remains_valid(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands,
        cleanup_gardens
    ):
        """Pre-existing gardens with unsnapped coordinates should remain valid"""
        # Create land
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "Legacy Test", "width": 10.0, "height": 10.0}
        )
        land = land_response.json()
        cleanup_lands.append(land["id"])

        # Create garden with unsnapped coordinates (simulating old layout)
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Legacy Garden", "garden_type": "outdoor"}
        )
        garden = garden_response.json()
        cleanup_gardens.append(garden["id"])

        # Place with exact coordinates (snap disabled)
        layout_response = authenticated_client.put(
            f"/gardens/{garden['id']}/layout",
            json={
                "land_id": land["id"],
                "x": 1.234567,
                "y": 2.345678,
                "width": 3.456789,
                "height": 4.567890,
                "snap_to_grid": False
            }
        )

        assert layout_response.status_code == 200
        updated_garden = layout_response.json()

        # Exact coordinates should be preserved
        assert updated_garden["x"] == 1.234567
        assert updated_garden["y"] == 2.345678

    def test_update_existing_garden_can_enable_snapping(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands,
        cleanup_gardens
    ):
        """Can update an existing unsnapped garden to use snapping"""
        # Create land
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "Update Test", "width": 10.0, "height": 10.0}
        )
        land = land_response.json()
        cleanup_lands.append(land["id"])

        # Create garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Upgradeable Garden", "garden_type": "outdoor"}
        )
        garden = garden_response.json()
        cleanup_gardens.append(garden["id"])

        # Initially place without snapping
        authenticated_client.put(
            f"/gardens/{garden['id']}/layout",
            json={
                "land_id": land["id"],
                "x": 1.234,
                "y": 2.345,
                "width": 3.456,
                "height": 4.567,
                "snap_to_grid": False
            }
        )

        # Update to use snapping
        update_response = authenticated_client.put(
            f"/gardens/{garden['id']}/layout",
            json={
                "land_id": land["id"],
                "x": 1.234,  # Will snap to 1.2
                "y": 2.345,  # Will snap to 2.3
                "width": 3.456,  # Will snap to 3.5
                "height": 4.567,  # Will snap to 4.6
                "snap_to_grid": True
            }
        )

        assert update_response.status_code == 200
        updated_garden = update_response.json()
        # Should now be snapped
        assert updated_garden["x"] == 1.2
        assert updated_garden["y"] == 2.3


@pytest.fixture
def cleanup_gardens(authenticated_client: httpx.Client):
    """Track and cleanup gardens created during tests"""
    garden_ids = []
    yield garden_ids

    for garden_id in garden_ids:
        try:
            authenticated_client.delete(f"/gardens/{garden_id}")
        except Exception:
            pass  # Best effort cleanup
