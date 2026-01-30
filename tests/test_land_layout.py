"""Tests for land layout functionality"""
import pytest
from app.models.land import Land
from app.models.garden import Garden
from app.services.layout_service import (
    check_overlap,
    check_bounds,
    validate_garden_placement,
    validate_spatial_data_complete
)


class TestOverlapDetection:
    """Test rectangle overlap detection logic"""

    def test_no_overlap_separate_gardens(self):
        """Gardens far apart should not overlap"""
        garden1 = {'x': 0, 'y': 0, 'width': 2, 'height': 2}
        garden2 = {'x': 5, 'y': 5, 'width': 2, 'height': 2}
        assert not check_overlap(garden1, garden2)

    def test_overlap_partial(self):
        """Partially overlapping gardens should be detected"""
        garden1 = {'x': 0, 'y': 0, 'width': 3, 'height': 3}
        garden2 = {'x': 2, 'y': 2, 'width': 3, 'height': 3}
        assert check_overlap(garden1, garden2)

    def test_overlap_fully_contained(self):
        """Garden fully inside another should overlap"""
        garden1 = {'x': 0, 'y': 0, 'width': 10, 'height': 10}
        garden2 = {'x': 2, 'y': 2, 'width': 2, 'height': 2}
        assert check_overlap(garden1, garden2)

    def test_no_overlap_touching_edges(self):
        """Gardens touching at edges should NOT overlap (boundary condition)"""
        garden1 = {'x': 0, 'y': 0, 'width': 2, 'height': 2}
        garden2 = {'x': 2, 'y': 0, 'width': 2, 'height': 2}
        assert not check_overlap(garden1, garden2)

    def test_no_overlap_touching_corners(self):
        """Gardens touching at corners should NOT overlap"""
        garden1 = {'x': 0, 'y': 0, 'width': 2, 'height': 2}
        garden2 = {'x': 2, 'y': 2, 'width': 2, 'height': 2}
        assert not check_overlap(garden1, garden2)

    def test_overlap_one_pixel(self):
        """Gardens overlapping by one pixel should be detected"""
        garden1 = {'x': 0, 'y': 0, 'width': 2.5, 'height': 2.5}
        garden2 = {'x': 2, 'y': 2, 'width': 2, 'height': 2}
        assert check_overlap(garden1, garden2)


class TestBoundsChecking:
    """Test land boundary validation"""

    def test_garden_within_bounds(self):
        """Garden that fits within land should pass"""
        land = Land(id=1, user_id=1, name="Test", width=10, height=10)
        garden = {'x': 1, 'y': 1, 'width': 3, 'height': 3}
        assert check_bounds(garden, land)

    def test_garden_at_origin(self):
        """Garden at (0,0) should be valid"""
        land = Land(id=1, user_id=1, name="Test", width=10, height=10)
        garden = {'x': 0, 'y': 0, 'width': 2, 'height': 2}
        assert check_bounds(garden, land)

    def test_garden_at_far_corner(self):
        """Garden at far corner should be valid"""
        land = Land(id=1, user_id=1, name="Test", width=10, height=10)
        garden = {'x': 8, 'y': 8, 'width': 2, 'height': 2}
        assert check_bounds(garden, land)

    def test_garden_exceeds_width(self):
        """Garden extending beyond width should fail"""
        land = Land(id=1, user_id=1, name="Test", width=10, height=10)
        garden = {'x': 8, 'y': 0, 'width': 3, 'height': 2}
        assert not check_bounds(garden, land)

    def test_garden_exceeds_height(self):
        """Garden extending beyond height should fail"""
        land = Land(id=1, user_id=1, name="Test", width=10, height=10)
        garden = {'x': 0, 'y': 8, 'width': 2, 'height': 3}
        assert not check_bounds(garden, land)

    def test_garden_negative_x(self):
        """Garden with negative x should fail"""
        land = Land(id=1, user_id=1, name="Test", width=10, height=10)
        garden = {'x': -1, 'y': 0, 'width': 2, 'height': 2}
        assert not check_bounds(garden, land)

    def test_garden_negative_y(self):
        """Garden with negative y should fail"""
        land = Land(id=1, user_id=1, name="Test", width=10, height=10)
        garden = {'x': 0, 'y': -1, 'width': 2, 'height': 2}
        assert not check_bounds(garden, land)

    def test_garden_exact_fit(self):
        """Garden exactly fitting land should pass"""
        land = Land(id=1, user_id=1, name="Test", width=10, height=10)
        garden = {'x': 0, 'y': 0, 'width': 10, 'height': 10}
        assert check_bounds(garden, land)


class TestGardenPlacement:
    """Test comprehensive garden placement validation"""

    def test_valid_placement_empty_land(self):
        """Placing garden on empty land should succeed"""
        land = Land(id=1, user_id=1, name="Test", width=10, height=10)
        land.gardens = []

        error = validate_garden_placement(
            garden_id=1,
            land=land,
            x=2,
            y=2,
            width=3,
            height=3,
            existing_gardens=[]
        )
        assert error is None

    def test_invalid_placement_out_of_bounds(self):
        """Placing garden out of bounds should fail"""
        land = Land(id=1, user_id=1, name="Test", width=10, height=10)

        error = validate_garden_placement(
            garden_id=1,
            land=land,
            x=8,
            y=8,
            width=5,
            height=5,
            existing_gardens=[]
        )
        assert error is not None
        assert error.error_type == "out_of_bounds"
        assert "exceeds land boundaries" in error.message

    def test_invalid_placement_overlaps_existing(self):
        """Placing garden that overlaps existing garden should fail"""
        land = Land(id=1, user_id=1, name="Test", width=10, height=10)

        # Create existing garden
        existing = Garden(
            id=2,
            user_id=1,
            name="Existing",
            garden_type="outdoor",
            is_hydroponic=False,
            land_id=1,
            x=2,
            y=2,
            width=3,
            height=3
        )

        # Try to place new garden that overlaps
        error = validate_garden_placement(
            garden_id=1,
            land=land,
            x=3,
            y=3,
            width=3,
            height=3,
            existing_gardens=[existing]
        )
        assert error is not None
        assert error.error_type == "overlap"
        assert "overlaps" in error.message.lower()
        assert error.conflicting_garden_ids == [2]

    def test_valid_placement_update_same_garden(self):
        """Updating a garden's position should not conflict with itself"""
        land = Land(id=1, user_id=1, name="Test", width=10, height=10)

        # Create existing garden
        existing = Garden(
            id=1,
            user_id=1,
            name="Garden1",
            garden_type="outdoor",
            is_hydroponic=False,
            land_id=1,
            x=2,
            y=2,
            width=3,
            height=3
        )

        # Update same garden (should not conflict with itself)
        error = validate_garden_placement(
            garden_id=1,
            land=land,
            x=3,
            y=3,
            width=3,
            height=3,
            existing_gardens=[existing]
        )
        assert error is None

    def test_valid_placement_adjacent_gardens(self):
        """Adjacent gardens (touching edges) should be allowed"""
        land = Land(id=1, user_id=1, name="Test", width=10, height=10)

        existing = Garden(
            id=2,
            user_id=1,
            name="Existing",
            garden_type="outdoor",
            is_hydroponic=False,
            land_id=1,
            x=0,
            y=0,
            width=3,
            height=3
        )

        # Place garden right next to existing (touching edge)
        error = validate_garden_placement(
            garden_id=1,
            land=land,
            x=3,
            y=0,
            width=3,
            height=3,
            existing_gardens=[existing]
        )
        assert error is None

    def test_ignore_gardens_without_spatial_data(self):
        """Gardens without complete spatial data should be ignored"""
        land = Land(id=1, user_id=1, name="Test", width=10, height=10)

        # Garden without spatial data
        incomplete = Garden(
            id=2,
            user_id=1,
            name="Incomplete",
            garden_type="outdoor",
            is_hydroponic=False
        )

        error = validate_garden_placement(
            garden_id=1,
            land=land,
            x=2,
            y=2,
            width=3,
            height=3,
            existing_gardens=[incomplete]
        )
        assert error is None


class TestSpatialDataValidation:
    """Test all-or-nothing spatial data validation"""

    def test_all_fields_provided(self):
        """All fields provided should pass"""
        error = validate_spatial_data_complete(
            land_id=1,
            x=2.0,
            y=3.0,
            width=4.0,
            height=5.0
        )
        assert error is None

    def test_all_fields_none(self):
        """All fields None should pass (removal)"""
        error = validate_spatial_data_complete(
            land_id=None,
            x=None,
            y=None,
            width=None,
            height=None
        )
        assert error is None

    def test_incomplete_missing_land_id(self):
        """Missing land_id should fail"""
        error = validate_spatial_data_complete(
            land_id=None,
            x=2.0,
            y=3.0,
            width=4.0,
            height=5.0
        )
        assert error is not None
        assert error.error_type == "incomplete_data"

    def test_incomplete_missing_x(self):
        """Missing x should fail"""
        error = validate_spatial_data_complete(
            land_id=1,
            x=None,
            y=3.0,
            width=4.0,
            height=5.0
        )
        assert error is not None
        assert error.error_type == "incomplete_data"

    def test_incomplete_missing_multiple(self):
        """Missing multiple fields should fail"""
        error = validate_spatial_data_complete(
            land_id=1,
            x=2.0,
            y=None,
            width=None,
            height=5.0
        )
        assert error is not None
        assert error.error_type == "incomplete_data"
        assert "y" in error.message
