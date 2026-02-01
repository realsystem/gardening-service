"""Unit tests for layout service snap-to-grid functionality

Tests the apply_snap_to_grid function and its integration with layout validation.
"""
import pytest
from app.services.layout_service import apply_snap_to_grid, check_bounds, check_overlap
from app.models.land import Land


class TestApplySnapToGrid:
    """Test snap-to-grid application in layout service"""

    def test_snap_enabled_snaps_all_coordinates(self):
        """When snap is enabled, all coordinates should be snapped"""
        x, y, w, h = apply_snap_to_grid(1.234, 2.567, 3.149, 4.298, snap_enabled=True)
        assert x == pytest.approx(1.2)
        assert y == pytest.approx(2.6)
        assert w == pytest.approx(3.1)
        assert h == pytest.approx(4.3)

    def test_snap_disabled_preserves_exact_values(self):
        """When snap is disabled, coordinates should remain unchanged"""
        x, y, w, h = apply_snap_to_grid(1.234, 2.567, 3.149, 4.298, snap_enabled=False)
        assert x == 1.234
        assert y == 2.567
        assert w == 3.149
        assert h == 4.298

    def test_snap_enabled_by_default(self):
        """Snap should be enabled by default"""
        x, y, w, h = apply_snap_to_grid(1.234, 2.567, 3.149, 4.298)
        # Should be snapped (default is True)
        assert x == pytest.approx(1.2)
        assert y == pytest.approx(2.6)

    def test_snap_zero_coordinates(self):
        """Should handle zero coordinates correctly"""
        x, y, w, h = apply_snap_to_grid(0.0, 0.0, 0.0, 0.0, snap_enabled=True)
        assert x == 0.0
        assert y == 0.0
        assert w == 0.0
        assert h == 0.0


class TestBoundsWithSnapping:
    """Test boundary checks work correctly with snapped coordinates"""

    def setup_method(self):
        """Create a test land for boundary tests"""
        self.land = Land(id=1, user_id=1, name="Test Land", width=10.0, height=10.0)

    def test_snapped_garden_within_bounds(self):
        """Snapped garden coordinates should respect land boundaries"""
        # Garden that will snap to (1.2, 1.3, 2.0, 2.0)
        x, y, w, h = apply_snap_to_grid(1.234, 1.267, 2.04, 1.96, snap_enabled=True)
        garden = {'x': x, 'y': y, 'width': w, 'height': h}
        assert check_bounds(garden, self.land) is True

    def test_snapped_garden_at_origin(self):
        """Snapped garden at origin should be valid"""
        x, y, w, h = apply_snap_to_grid(0.01, 0.02, 1.0, 1.0, snap_enabled=True)
        garden = {'x': x, 'y': y, 'width': w, 'height': h}
        # Should snap to (0.0, 0.0, 1.0, 1.0)
        assert garden['x'] == 0.0
        assert garden['y'] == 0.0
        assert check_bounds(garden, self.land) is True

    def test_snapped_garden_at_edge(self):
        """Snapped garden at land edge should be valid"""
        # Garden that fits exactly at the edge after snapping
        x, y, w, h = apply_snap_to_grid(7.99, 7.98, 2.01, 2.02, snap_enabled=True)
        garden = {'x': x, 'y': y, 'width': w, 'height': h}
        # Should snap to (8.0, 8.0, 2.0, 2.0) which fits in 10×10 land
        assert check_bounds(garden, self.land) is True

    def test_snapped_garden_exceeds_bounds(self):
        """Garden that exceeds bounds after snapping should be invalid"""
        # This will snap to coordinates that exceed the land
        x, y, w, h = apply_snap_to_grid(8.1, 8.1, 2.1, 2.1, snap_enabled=True)
        garden = {'x': x, 'y': y, 'width': w, 'height': h}
        # Should snap to (8.1, 8.1, 2.1, 2.1) which exceeds 10×10 land
        assert check_bounds(garden, self.land) is False


class TestOverlapWithSnapping:
    """Test overlap detection works correctly with snapped coordinates"""

    def test_snapped_gardens_touching_edges_no_overlap(self):
        """Gardens touching at edges after snapping should not overlap"""
        # Garden 1 at (0.0, 0.0) with size (2.0, 2.0)
        x1, y1, w1, h1 = apply_snap_to_grid(0.01, 0.02, 1.99, 1.98, snap_enabled=True)
        garden1 = {'x': x1, 'y': y1, 'width': w1, 'height': h1}

        # Garden 2 starts where Garden 1 ends
        x2, y2, w2, h2 = apply_snap_to_grid(2.01, 0.02, 1.99, 1.98, snap_enabled=True)
        garden2 = {'x': x2, 'y': y2, 'width': w2, 'height': h2}

        # Should snap to (2.0, 0.0) which is adjacent to garden1 ending at x=2.0
        assert not check_overlap(garden1, garden2)

    def test_snapped_gardens_overlapping(self):
        """Gardens that overlap after snapping should be detected"""
        # Garden 1
        x1, y1, w1, h1 = apply_snap_to_grid(0.0, 0.0, 2.0, 2.0, snap_enabled=True)
        garden1 = {'x': x1, 'y': y1, 'width': w1, 'height': h1}

        # Garden 2 overlaps with Garden 1
        x2, y2, w2, h2 = apply_snap_to_grid(1.0, 1.0, 2.0, 2.0, snap_enabled=True)
        garden2 = {'x': x2, 'y': y2, 'width': w2, 'height': h2}

        assert check_overlap(garden1, garden2)

    def test_snapped_gardens_separated_no_overlap(self):
        """Separated gardens after snapping should not overlap"""
        # Garden 1
        x1, y1, w1, h1 = apply_snap_to_grid(0.0, 0.0, 2.0, 2.0, snap_enabled=True)
        garden1 = {'x': x1, 'y': y1, 'width': w1, 'height': h1}

        # Garden 2 with gap
        x2, y2, w2, h2 = apply_snap_to_grid(3.0, 3.0, 2.0, 2.0, snap_enabled=True)
        garden2 = {'x': x2, 'y': y2, 'width': w2, 'height': h2}

        assert not check_overlap(garden1, garden2)

    def test_unsnapped_gardens_might_overlap_differently(self):
        """Unsnapped gardens might have different overlap behavior"""
        # Without snapping, these might be very close but not overlapping
        x1, y1, w1, h1 = apply_snap_to_grid(0.0, 0.0, 1.99, 1.99, snap_enabled=False)
        garden1 = {'x': x1, 'y': y1, 'width': w1, 'height': h1}

        x2, y2, w2, h2 = apply_snap_to_grid(2.0, 0.0, 2.0, 2.0, snap_enabled=False)
        garden2 = {'x': x2, 'y': y2, 'width': w2, 'height': h2}

        # 0.0 + 1.99 = 1.99 which is < 2.0, so no overlap
        assert not check_overlap(garden1, garden2)

        # With snapping, garden1 becomes 2.0 wide, creating adjacent gardens
        x1_snap, y1_snap, w1_snap, h1_snap = apply_snap_to_grid(0.0, 0.0, 1.99, 1.99, snap_enabled=True)
        garden1_snap = {'x': x1_snap, 'y': y1_snap, 'width': w1_snap, 'height': h1_snap}
        # garden1_snap should snap to width=2.0, making it touch garden2 at x=2.0
        assert not check_overlap(garden1_snap, garden2)  # Still no overlap, just touching


class TestSnapConsistency:
    """Test that snapping behavior is consistent across multiple operations"""

    def test_snap_is_idempotent(self):
        """Snapping twice should give same result as snapping once"""
        x1, y1, w1, h1 = apply_snap_to_grid(1.234, 2.567, 3.149, 4.298, snap_enabled=True)
        x2, y2, w2, h2 = apply_snap_to_grid(x1, y1, w1, h1, snap_enabled=True)

        assert x1 == x2
        assert y1 == y2
        assert w1 == w2
        assert h1 == h2

    def test_snap_with_already_aligned_values(self):
        """Already aligned values should remain unchanged"""
        x, y, w, h = apply_snap_to_grid(1.0, 2.0, 3.0, 4.0, snap_enabled=True)
        assert x == 1.0
        assert y == 2.0
        assert w == 3.0
        assert h == 4.0
