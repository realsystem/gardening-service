"""Unit tests for grid configuration and snapping utilities

Tests the grid resolution conversion, snap-to-grid math, and validation logic.
"""
import pytest
from app.utils.grid_config import (
    snap_to_grid,
    snap_rectangle_to_grid,
    validate_grid_aligned,
    get_grid_info,
    GRID_RESOLUTION,
    GRID_CELLS_PER_UNIT
)


class TestGridResolution:
    """Test grid resolution constants"""

    def test_grid_resolution_is_point_one(self):
        """Grid resolution should be 0.1 units (10× finer than 1 unit)"""
        assert GRID_RESOLUTION == 0.1

    def test_cells_per_unit_is_ten(self):
        """Should have 10 grid cells per unit"""
        assert GRID_CELLS_PER_UNIT == 10

    def test_resolution_calculation_is_consistent(self):
        """Grid resolution calculation should be consistent"""
        assert GRID_RESOLUTION * GRID_CELLS_PER_UNIT == 1.0


class TestSnapToGrid:
    """Test snap-to-grid coordinate conversion"""

    def test_snap_exact_grid_value(self):
        """Values already on grid should remain unchanged"""
        assert snap_to_grid(1.0) == pytest.approx(1.0)
        assert snap_to_grid(1.5) == pytest.approx(1.5)
        assert snap_to_grid(2.3) == pytest.approx(2.3)

    def test_snap_rounds_to_nearest(self):
        """Values should snap to nearest grid intersection"""
        # 1.23 is closer to 1.2 than 1.3
        assert snap_to_grid(1.23) == pytest.approx(1.2)
        # 1.27 is closer to 1.3 than 1.2
        assert snap_to_grid(1.27) == pytest.approx(1.3)
        # Exactly halfway - Python's round() uses "round half to even"
        # 1.25/0.1 = 12.5, rounds to 12 (even), so 12*0.1 = 1.2
        assert snap_to_grid(1.25) == pytest.approx(1.2)

    def test_snap_near_zero(self):
        """Values near zero should snap correctly"""
        assert snap_to_grid(0.04) == pytest.approx(0.0)
        # 0.05/0.1 = 0.5, rounds to 0 (even), so 0*0.1 = 0.0
        assert snap_to_grid(0.05) == pytest.approx(0.0)
        assert snap_to_grid(0.06) == pytest.approx(0.1)

    def test_snap_negative_values(self):
        """Negative values should snap correctly"""
        assert snap_to_grid(-1.23) == pytest.approx(-1.2)
        assert snap_to_grid(-1.27) == pytest.approx(-1.3)

    def test_snap_large_values(self):
        """Large values should snap correctly"""
        assert snap_to_grid(100.14) == pytest.approx(100.1)
        assert snap_to_grid(100.16) == pytest.approx(100.2)

    def test_snap_with_custom_resolution(self):
        """Should support custom grid resolution"""
        # Snap to 0.5 units
        assert snap_to_grid(1.2, 0.5) == 1.0
        assert snap_to_grid(1.3, 0.5) == 1.5
        # Snap to 1.0 units
        assert snap_to_grid(1.4, 1.0) == 1.0
        assert snap_to_grid(1.6, 1.0) == 2.0


class TestSnapRectangleToGrid:
    """Test rectangle snapping (all coordinates at once)"""

    def test_snap_all_coordinates(self):
        """All rectangle coordinates should snap independently"""
        x, y, w, h = snap_rectangle_to_grid(1.23, 2.37, 3.14, 4.28)
        assert x == pytest.approx(1.2)
        assert y == pytest.approx(2.4)
        assert w == pytest.approx(3.1)
        assert h == pytest.approx(4.3)

    def test_snap_preserves_approximate_size(self):
        """Snapping should preserve approximate rectangle size"""
        x1, y1, w1, h1 = snap_rectangle_to_grid(1.0, 2.0, 3.0, 4.0)
        # Already aligned, should not change
        assert (x1, y1, w1, h1) == (1.0, 2.0, 3.0, 4.0)

    def test_snap_near_grid_values(self):
        """Near-grid values should snap to closest grid point"""
        x, y, w, h = snap_rectangle_to_grid(0.99, 1.01, 2.04, 2.96)
        assert x == 1.0
        assert y == 1.0
        assert w == 2.0
        assert h == 3.0


class TestValidateGridAligned:
    """Test grid alignment validation"""

    def test_aligned_values_are_valid(self):
        """Values on grid intersections should be valid"""
        assert validate_grid_aligned(0.0) is True
        assert validate_grid_aligned(0.1) is True
        assert validate_grid_aligned(1.0) is True
        assert validate_grid_aligned(1.5) is True
        assert validate_grid_aligned(2.3) is True

    def test_unaligned_values_are_invalid(self):
        """Values not on grid intersections should be invalid"""
        assert validate_grid_aligned(0.11) is False
        assert validate_grid_aligned(1.234) is False
        assert validate_grid_aligned(2.05) is False

    def test_very_close_to_grid_is_valid(self):
        """Values very close to grid (within tolerance) should be valid"""
        # Floating point precision issues
        assert validate_grid_aligned(0.1 + 1e-10) is True
        assert validate_grid_aligned(1.0 - 1e-10) is True

    def test_validation_with_custom_resolution(self):
        """Should validate against custom grid resolution"""
        # 0.5 unit grid
        assert validate_grid_aligned(1.5, 0.5) is True
        assert validate_grid_aligned(1.3, 0.5) is False
        # 1.0 unit grid
        assert validate_grid_aligned(2.0, 1.0) is True
        assert validate_grid_aligned(2.5, 1.0) is False

    def test_zero_resolution_accepts_all(self):
        """Grid resolution of 0 means no grid, all values valid"""
        assert validate_grid_aligned(1.234567, 0.0) is True
        assert validate_grid_aligned(9.876543, 0.0) is True


class TestGetGridInfo:
    """Test grid information metadata"""

    def test_default_grid_info(self):
        """Should return correct grid information"""
        info = get_grid_info()
        assert info["grid_resolution"] == 0.1
        assert info["cells_per_unit"] == 10
        assert "10 grid cells" in info["description"]

    def test_custom_grid_info(self):
        """Should return info for custom grid resolution"""
        info = get_grid_info(0.5)
        assert info["grid_resolution"] == 0.5
        assert info["cells_per_unit"] == 2
        assert "2 grid cells" in info["description"]

    def test_zero_resolution_info(self):
        """Should handle zero resolution gracefully"""
        info = get_grid_info(0.0)
        assert info["grid_resolution"] == 0.0
        assert info["cells_per_unit"] is None
        assert info["description"] == "No grid"


class TestSnapEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_snap_very_small_values(self):
        """Very small values should snap correctly"""
        assert snap_to_grid(0.001) == 0.0
        assert snap_to_grid(0.049) == 0.0
        assert snap_to_grid(0.051) == 0.1

    def test_snap_precision_boundaries(self):
        """Test precision at grid boundaries"""
        # Test values at decision boundaries
        # Note: Due to floating point representation, 0.15 / 0.1 ≈ 1.4999999999999998
        # which rounds to 1, giving 0.1 (not 0.2 as one might expect)
        assert snap_to_grid(0.15) == pytest.approx(0.1)
        # Just below halfway
        assert snap_to_grid(0.14) == pytest.approx(0.1)
        # Clearly above halfway
        assert snap_to_grid(0.16) == pytest.approx(0.2)

    def test_snap_rectangle_zero_dimensions(self):
        """Should handle zero-sized rectangles"""
        x, y, w, h = snap_rectangle_to_grid(1.23, 2.34, 0.0, 0.0)
        assert x == pytest.approx(1.2)
        assert y == pytest.approx(2.3)
        assert w == pytest.approx(0.0)
        assert h == pytest.approx(0.0)

    def test_snap_rectangle_negative_dimensions(self):
        """Should snap negative dimensions (even if invalid geometrically)"""
        x, y, w, h = snap_rectangle_to_grid(1.0, 2.0, -1.23, -2.34)
        assert w == pytest.approx(-1.2)
        assert h == pytest.approx(-2.3)
