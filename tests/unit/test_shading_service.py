"""
Unit tests for shading service

Tests the geometric calculations for tree shading impact on gardens.
"""
import pytest
import math
from app.services import shading_service


class TestCircleRectangleIntersection:
    """Test circle-rectangle intersection calculations"""

    def test_no_intersection(self):
        """Circle and rectangle don't intersect"""
        # Circle at (0, 0) with radius 1, rectangle at (10, 10)
        area = shading_service.calculate_circle_rectangle_intersection_area(
            cx=0, cy=0, radius=1,
            rect_x=10, rect_y=10, rect_width=2, rect_height=2
        )
        assert area == 0.0

    def test_full_coverage(self):
        """Circle completely covers rectangle"""
        # Circle at (5, 5) with radius 10, small rectangle at (5, 5)
        area = shading_service.calculate_circle_rectangle_intersection_area(
            cx=5, cy=5, radius=10,
            rect_x=4, rect_y=4, rect_width=2, rect_height=2
        )
        # Rectangle area is 2*2 = 4, should be fully covered
        assert area > 3.9  # Allow for sampling approximation

    def test_partial_intersection(self):
        """Circle partially intersects rectangle"""
        # Circle at (0, 0) with radius 5, rectangle at (3, 0)
        area = shading_service.calculate_circle_rectangle_intersection_area(
            cx=0, cy=0, radius=5,
            rect_x=3, rect_y=0, rect_width=4, rect_height=4
        )
        # Should have some intersection but not full coverage
        assert 0 < area < 16  # Less than full rectangle area


class TestAverageShadeIntensity:
    """Test average shade intensity calculations"""

    def test_center_intensity(self):
        """Point at tree center has maximum intensity"""
        # Tree at (0, 0), rectangle very small at center
        intensity = shading_service.calculate_average_shade_intensity(
            tree_x=0, tree_y=0, canopy_radius=10,
            rect_x=-0.1, rect_y=-0.1, rect_width=0.2, rect_height=0.2
        )
        # Should be close to 1.0 (100% shade at center)
        assert intensity > 0.95

    def test_edge_intensity(self):
        """Points at canopy edge have minimal intensity"""
        # Tree at (0, 0) with radius 10, rectangle at edge
        intensity = shading_service.calculate_average_shade_intensity(
            tree_x=0, tree_y=0, canopy_radius=10,
            rect_x=9.5, rect_y=0, rect_width=0.5, rect_height=1
        )
        # Should be close to 0.0 (minimal shade at edge)
        assert intensity < 0.15

    def test_no_intersection_zero_intensity(self):
        """No intersection results in zero intensity"""
        intensity = shading_service.calculate_average_shade_intensity(
            tree_x=0, tree_y=0, canopy_radius=5,
            rect_x=20, rect_y=20, rect_width=2, rect_height=2
        )
        assert intensity == 0.0


class TestGardenShading:
    """Test complete garden shading calculations"""

    def test_no_trees_full_sun(self):
        """Garden with no trees has full sun exposure"""
        shading = shading_service.calculate_garden_shading(
            garden_x=0, garden_y=0, garden_width=10, garden_height=10,
            trees=[],
            baseline_sun_exposure=1.0
        )
        assert shading.sun_exposure_score == 1.0
        assert shading.sun_exposure_category == "full_sun"
        assert shading.total_shade_factor == 0.0
        assert len(shading.contributing_trees) == 0

    def test_single_tree_centered_on_garden(self):
        """Tree centered on garden creates significant shade"""
        trees = [{
            'id': 1,
            'name': 'Oak',
            'x': 5,  # Center of 10x10 garden
            'y': 5,
            'canopy_radius': 8,  # Covers most of garden
            'garden_id': 1
        }]

        shading = shading_service.calculate_garden_shading(
            garden_x=0, garden_y=0, garden_width=10, garden_height=10,
            trees=trees,
            baseline_sun_exposure=1.0
        )

        # Should have significant shade
        assert shading.sun_exposure_score < 0.5
        assert shading.sun_exposure_category in ["partial_sun", "shade"]
        assert shading.total_shade_factor > 0.5
        assert len(shading.contributing_trees) == 1
        assert shading.contributing_trees[0]['tree_id'] == 1

    def test_tree_far_from_garden(self):
        """Tree far from garden doesn't affect sun exposure"""
        trees = [{
            'id': 1,
            'name': 'Oak',
            'x': 100,  # Far from garden
            'y': 100,
            'canopy_radius': 5,
            'garden_id': 1
        }]

        shading = shading_service.calculate_garden_shading(
            garden_x=0, garden_y=0, garden_width=10, garden_height=10,
            trees=trees,
            baseline_sun_exposure=1.0
        )

        assert shading.sun_exposure_score == 1.0
        assert shading.sun_exposure_category == "full_sun"
        assert len(shading.contributing_trees) == 0

    def test_multiple_trees_cumulative_shade(self):
        """Multiple trees create cumulative shading effect"""
        trees = [
            {
                'id': 1,
                'name': 'Oak 1',
                'x': 3,
                'y': 3,
                'canopy_radius': 4,
                'garden_id': 1
            },
            {
                'id': 2,
                'name': 'Oak 2',
                'x': 7,
                'y': 7,
                'canopy_radius': 4,
                'garden_id': 1
            }
        ]

        shading = shading_service.calculate_garden_shading(
            garden_x=0, garden_y=0, garden_width=10, garden_height=10,
            trees=trees,
            baseline_sun_exposure=1.0
        )

        # Should have more shade than single tree
        assert shading.total_shade_factor > 0.3
        assert len(shading.contributing_trees) == 2

    def test_partial_overlap(self):
        """Tree partially overlaps garden corner"""
        trees = [{
            'id': 1,
            'name': 'Small Tree',
            'x': 0,  # Just touching garden corner
            'y': 0,
            'canopy_radius': 3,
            'garden_id': 1
        }]

        shading = shading_service.calculate_garden_shading(
            garden_x=0, garden_y=0, garden_width=10, garden_height=10,
            trees=trees,
            baseline_sun_exposure=1.0
        )

        # Should have partial shade
        assert 0 < shading.total_shade_factor < 0.5
        assert 0.5 < shading.sun_exposure_score < 1.0
        assert len(shading.contributing_trees) == 1


class TestSunExposureCategorization:
    """Test sun exposure category mapping"""

    def test_full_sun_category(self):
        """High scores map to full_sun"""
        assert shading_service._categorize_sun_exposure(1.0) == "full_sun"
        assert shading_service._categorize_sun_exposure(0.9) == "full_sun"
        assert shading_service._categorize_sun_exposure(0.75) == "full_sun"

    def test_partial_sun_category(self):
        """Medium scores map to partial_sun"""
        assert shading_service._categorize_sun_exposure(0.7) == "partial_sun"
        assert shading_service._categorize_sun_exposure(0.5) == "partial_sun"
        assert shading_service._categorize_sun_exposure(0.4) == "partial_sun"

    def test_shade_category(self):
        """Low scores map to shade"""
        assert shading_service._categorize_sun_exposure(0.3) == "shade"
        assert shading_service._categorize_sun_exposure(0.1) == "shade"
        assert shading_service._categorize_sun_exposure(0.0) == "shade"


class TestTreeCoverageArea:
    """Test tree canopy area calculations"""

    def test_canopy_area(self):
        """Calculate correct canopy area"""
        area = shading_service.calculate_tree_coverage_area(canopy_radius=5)
        expected = math.pi * 25  # π * r²
        assert abs(area - expected) < 0.01

    def test_small_canopy(self):
        """Small radius gives small area"""
        area = shading_service.calculate_tree_coverage_area(canopy_radius=1)
        assert abs(area - math.pi) < 0.01

    def test_large_canopy(self):
        """Large radius gives large area"""
        area = shading_service.calculate_tree_coverage_area(canopy_radius=10)
        expected = math.pi * 100
        assert abs(area - expected) < 0.01
