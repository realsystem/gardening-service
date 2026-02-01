"""
Complex Layout Stress Tests

Tests land layout system with complex scenarios:
- Many gardens on one land plot
- Edge-touching layouts
- Overlap detection at scale
- Mixed irrigation zones
"""
import pytest
import httpx


class TestDenseLayouts:
    """Test many gardens on single land plot"""

    def test_10_gardens_on_land_plot(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands: list,
        cleanup_gardens: list
    ):
        """Place 10 gardens on a large land plot"""
        # Create large land plot (200x200 feet)
        land_response = authenticated_client.post(
            "/lands",
            json={
                "name": "Large Property",
                "width_feet": 200,
                "length_feet": 200
            }
        )
        land_id = land_response.json()["id"]
        cleanup_lands.append(land_id)

        # Create 10 gardens
        garden_ids = []
        for i in range(10):
            garden_response = authenticated_client.post(
                "/gardens",
                json={"name": f"Plot {i+1}", "garden_type": "outdoor"}
            )
            garden_id = garden_response.json()["id"]
            garden_ids.append(garden_id)
            cleanup_gardens.append(garden_id)

        # Place gardens in grid pattern (5x2 grid, each 30x30)
        placed_count = 0
        for i, garden_id in enumerate(garden_ids):
            row = i // 5
            col = i % 5

            x = col * 40  # 30 feet wide + 10 feet spacing
            y = row * 40

            response = authenticated_client.post(
                f"/lands/{land_id}/gardens",
                json={
                    "garden_id": garden_id,
                    "x_offset": x,
                    "y_offset": y,
                    "width": 30,
                    "length": 30
                }
            )
            if response.status_code in [200, 201]:
                placed_count += 1

        assert placed_count >= 9, f"Only placed {placed_count}/10 gardens"


class TestOverlapDetection:
    """Test overlap detection at scale"""

    def test_reject_overlapping_gardens(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands: list,
        cleanup_gardens: list
    ):
        """System should reject overlapping garden placements"""
        # Create land
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "Test Land", "width_feet": 100, "length_feet": 100}
        )
        land_id = land_response.json()["id"]
        cleanup_lands.append(land_id)

        # Create 2 gardens
        garden_ids = []
        for i in range(2):
            response = authenticated_client.post(
                "/gardens",
                json={"name": f"Garden {i+1}", "garden_type": "outdoor"}
            )
            garden_ids.append(response.json()["id"])
            cleanup_gardens.append(response.json()["id"])

        # Place first garden
        response1 = authenticated_client.post(
            f"/lands/{land_id}/gardens",
            json={
                "garden_id": garden_ids[0],
                "x_offset": 10,
                "y_offset": 10,
                "width": 30,
                "length": 30
            }
        )
        assert response1.status_code in [200, 201]

        # Try to place second garden overlapping
        response2 = authenticated_client.post(
            f"/lands/{land_id}/gardens",
            json={
                "garden_id": garden_ids[1],
                "x_offset": 20,  # Overlaps with first garden
                "y_offset": 20,
                "width": 30,
                "length": 30
            }
        )

        # Should be rejected
        assert response2.status_code in [400, 409], \
            "Overlapping garden should be rejected"


class TestEdgeCases:
    """Test edge cases in layout"""

    def test_adjacent_gardens_no_overlap(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands: list,
        cleanup_gardens: list
    ):
        """Adjacent gardens (touching edges) should be allowed"""
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "Edge Test Land", "width_feet": 100, "length_feet": 50}
        )
        land_id = land_response.json()["id"]
        cleanup_lands.append(land_id)

        # Create 2 gardens
        garden_ids = []
        for i in range(2):
            response = authenticated_client.post(
                "/gardens",
                json={"name": f"Adjacent {i+1}", "garden_type": "outdoor"}
            )
            garden_ids.append(response.json()["id"])
            cleanup_gardens.append(response.json()["id"])

        # Place gardens side-by-side (touching but not overlapping)
        response1 = authenticated_client.post(
            f"/lands/{land_id}/gardens",
            json={
                "garden_id": garden_ids[0],
                "x_offset": 0,
                "y_offset": 0,
                "width": 30,
                "length": 20
            }
        )

        response2 = authenticated_client.post(
            f"/lands/{land_id}/gardens",
            json={
                "garden_id": garden_ids[1],
                "x_offset": 30,  # Exactly adjacent
                "y_offset": 0,
                "width": 30,
                "length": 20
            }
        )

        # Both should succeed (touching edges is OK)
        assert response1.status_code in [200, 201]
        assert response2.status_code in [200, 201]


class TestBoundsChecking:
    """Test gardens stay within land bounds"""

    def test_reject_out_of_bounds(
        self,
        authenticated_client: httpx.Client,
        cleanup_lands: list,
        cleanup_gardens: list
    ):
        """Garden extending beyond land should be rejected"""
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "Small Land", "width_feet": 50, "length_feet": 50}
        )
        land_id = land_response.json()["id"]
        cleanup_lands.append(land_id)

        garden_response = authenticated_client.post(
            "/gardens",
            json={"name": "Too Big", "garden_type": "outdoor"}
        )
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        # Try to place garden that extends beyond land
        response = authenticated_client.post(
            f"/lands/{land_id}/gardens",
            json={
                "garden_id": garden_id,
                "x_offset": 40,
                "y_offset": 40,
                "width": 30,  # Would extend to x=70 (beyond 50)
                "length": 30   # Would extend to y=70 (beyond 50)
            }
        )

        # Should be rejected
        assert response.status_code in [400, 422], \
            "Out-of-bounds garden should be rejected"
