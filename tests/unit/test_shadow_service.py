"""Unit tests for shadow projection service

Tests shadow rectangle math and garden shading calculations.
"""
import pytest
from app.services.shadow_service import (
    ShadowRectangle,
    project_tree_shadow,
    calculate_garden_shading,
    calculate_seasonal_garden_shading,
    get_exposure_category,
    calculate_seasonal_exposure_score
)
from app.utils.sun_model import Season


class TestShadowRectangle:
    """Test shadow rectangle geometry"""

    def test_rectangle_creation(self):
        """Can create shadow rectangle"""
        rect = ShadowRectangle(x=10.0, y=20.0, width=5.0, height=8.0)
        assert rect.x == 10.0
        assert rect.y == 20.0
        assert rect.width == 5.0
        assert rect.height == 8.0

    def test_get_bounds(self):
        """Rectangle bounds are calculated correctly"""
        rect = ShadowRectangle(x=10.0, y=20.0, width=5.0, height=8.0)
        x_min, y_min, x_max, y_max = rect.get_bounds()

        assert x_min == 10.0
        assert y_min == 20.0
        assert x_max == 15.0  # 10 + 5
        assert y_max == 28.0  # 20 + 8

    def test_to_dict(self):
        """Can convert to dictionary"""
        rect = ShadowRectangle(x=10.0, y=20.0, width=5.0, height=8.0)
        data = rect.to_dict()

        assert data["x"] == 10.0
        assert data["y"] == 20.0
        assert data["width"] == 5.0
        assert data["height"] == 8.0


class TestRectangleIntersection:
    """Test rectangle intersection detection"""

    def test_overlapping_rectangles(self):
        """Overlapping rectangles intersect"""
        rect1 = ShadowRectangle(x=0.0, y=0.0, width=10.0, height=10.0)
        rect2 = ShadowRectangle(x=5.0, y=5.0, width=10.0, height=10.0)

        assert rect1.intersects(rect2)
        assert rect2.intersects(rect1)  # Symmetric

    def test_touching_edges_no_intersection(self):
        """Rectangles touching at edges don't intersect"""
        rect1 = ShadowRectangle(x=0.0, y=0.0, width=10.0, height=10.0)
        rect2 = ShadowRectangle(x=10.0, y=0.0, width=10.0, height=10.0)

        assert not rect1.intersects(rect2)

    def test_separated_rectangles(self):
        """Separated rectangles don't intersect"""
        rect1 = ShadowRectangle(x=0.0, y=0.0, width=10.0, height=10.0)
        rect2 = ShadowRectangle(x=20.0, y=20.0, width=10.0, height=10.0)

        assert not rect1.intersects(rect2)

    def test_contained_rectangle(self):
        """Rectangle fully inside another intersects"""
        rect1 = ShadowRectangle(x=0.0, y=0.0, width=20.0, height=20.0)
        rect2 = ShadowRectangle(x=5.0, y=5.0, width=5.0, height=5.0)

        assert rect1.intersects(rect2)
        assert rect2.intersects(rect1)


class TestIntersectionArea:
    """Test rectangle intersection area calculation"""

    def test_no_intersection_zero_area(self):
        """Non-intersecting rectangles have zero area"""
        rect1 = ShadowRectangle(x=0.0, y=0.0, width=10.0, height=10.0)
        rect2 = ShadowRectangle(x=20.0, y=20.0, width=10.0, height=10.0)

        assert rect1.intersection_area(rect2) == 0.0

    def test_partial_overlap_area(self):
        """Partial overlap calculates correct area"""
        rect1 = ShadowRectangle(x=0.0, y=0.0, width=10.0, height=10.0)
        rect2 = ShadowRectangle(x=5.0, y=5.0, width=10.0, height=10.0)

        # Overlap is 5×5 = 25
        area = rect1.intersection_area(rect2)
        assert area == pytest.approx(25.0, rel=0.01)

    def test_full_containment_area(self):
        """Fully contained rectangle area equals smaller rectangle"""
        rect1 = ShadowRectangle(x=0.0, y=0.0, width=20.0, height=20.0)
        rect2 = ShadowRectangle(x=5.0, y=5.0, width=5.0, height=5.0)

        # Entire rect2 is inside rect1
        area = rect1.intersection_area(rect2)
        assert area == pytest.approx(25.0, rel=0.01)  # 5×5

    def test_identical_rectangles(self):
        """Identical rectangles have full overlap"""
        rect1 = ShadowRectangle(x=10.0, y=10.0, width=15.0, height=15.0)
        rect2 = ShadowRectangle(x=10.0, y=10.0, width=15.0, height=15.0)

        area = rect1.intersection_area(rect2)
        assert area == pytest.approx(225.0, rel=0.01)  # 15×15


class TestTreeShadowProjection:
    """Test tree shadow projection"""

    def test_northern_hemisphere_winter_long_shadow(self):
        """Northern winter produces long northward shadow"""
        shadow = project_tree_shadow(
            tree_x=10.0,
            tree_y=10.0,
            tree_height=10.0,
            canopy_radius=2.0,
            latitude=40.0,
            season=Season.WINTER
        )

        # Shadow should extend northward (positive Y direction)
        # Winter sun at 30° produces shadow length ≈ 10/tan(30°) ≈ 17.3m
        # Shadow rectangle should be taller than tree canopy
        assert shadow.height > 4.0  # Much taller than canopy diameter

    def test_northern_hemisphere_summer_shorter_shadow(self):
        """Northern summer produces shorter shadow"""
        winter_shadow = project_tree_shadow(
            tree_x=10.0,
            tree_y=10.0,
            tree_height=10.0,
            canopy_radius=2.0,
            latitude=40.0,
            season=Season.WINTER
        )

        summer_shadow = project_tree_shadow(
            tree_x=10.0,
            tree_y=10.0,
            tree_height=10.0,
            canopy_radius=2.0,
            latitude=40.0,
            season=Season.SUMMER
        )

        # Summer shadow should be shorter than winter
        assert summer_shadow.height < winter_shadow.height

    def test_southern_hemisphere_shadow_direction(self):
        """Southern hemisphere casts shadow southward"""
        shadow = project_tree_shadow(
            tree_x=10.0,
            tree_y=10.0,
            tree_height=10.0,
            canopy_radius=2.0,
            latitude=-40.0,
            season=Season.WINTER
        )

        # In southern hemisphere, shadow extends south (negative Y)
        # Shadow rectangle should have Y < tree Y
        assert shadow.y < 10.0

    def test_shadow_width_matches_canopy(self):
        """Shadow width matches tree canopy diameter"""
        canopy_radius = 3.0
        shadow = project_tree_shadow(
            tree_x=10.0,
            tree_y=10.0,
            tree_height=10.0,
            canopy_radius=canopy_radius,
            latitude=40.0,
            season=Season.WINTER
        )

        # Shadow width should equal canopy diameter
        assert shadow.width == pytest.approx(canopy_radius * 2, rel=0.01)


class TestGardenShading:
    """Test garden shading calculation"""

    def test_no_shadows_zero_shading(self):
        """Garden with no shadows has 0% shading"""
        result = calculate_garden_shading(
            garden_x=0.0,
            garden_y=0.0,
            garden_width=10.0,
            garden_height=10.0,
            shadows=[]
        )

        assert result["total_shaded_area"] == 0.0
        assert result["shaded_percentage"] == 0.0
        assert result["affected_by_count"] == 0

    def test_full_coverage_shadow(self):
        """Shadow covering entire garden gives 100% shading"""
        garden_shadow = ShadowRectangle(x=0.0, y=0.0, width=10.0, height=10.0)

        result = calculate_garden_shading(
            garden_x=0.0,
            garden_y=0.0,
            garden_width=10.0,
            garden_height=10.0,
            shadows=[garden_shadow]
        )

        assert result["shaded_percentage"] == pytest.approx(100.0, rel=0.01)
        assert result["affected_by_count"] == 1

    def test_partial_coverage_shadow(self):
        """Partial shadow gives proportional shading"""
        # Garden is 10×10 = 100 m²
        # Shadow covers half (0-5, 0-10) = 50 m²
        half_shadow = ShadowRectangle(x=0.0, y=0.0, width=5.0, height=10.0)

        result = calculate_garden_shading(
            garden_x=0.0,
            garden_y=0.0,
            garden_width=10.0,
            garden_height=10.0,
            shadows=[half_shadow]
        )

        assert result["shaded_percentage"] == pytest.approx(50.0, rel=0.01)

    def test_multiple_shadows(self):
        """Multiple shadows combine shading"""
        shadow1 = ShadowRectangle(x=0.0, y=0.0, width=5.0, height=5.0)
        shadow2 = ShadowRectangle(x=5.0, y=5.0, width=5.0, height=5.0)

        result = calculate_garden_shading(
            garden_x=0.0,
            garden_y=0.0,
            garden_width=10.0,
            garden_height=10.0,
            shadows=[shadow1, shadow2]
        )

        # Two 5×5 shadows = 50 m² total (25 each)
        assert result["shaded_percentage"] == pytest.approx(50.0, rel=0.01)
        assert result["affected_by_count"] == 2

    def test_zero_area_garden(self):
        """Zero-area garden handled gracefully"""
        shadow = ShadowRectangle(x=0.0, y=0.0, width=10.0, height=10.0)

        result = calculate_garden_shading(
            garden_x=0.0,
            garden_y=0.0,
            garden_width=0.0,
            garden_height=10.0,
            shadows=[shadow]
        )

        assert result["shaded_percentage"] == 0.0


class TestSeasonalGardenShading:
    """Test seasonal garden shading calculation"""

    def test_all_seasons_calculated(self):
        """Shading calculated for all three seasons"""
        trees = [{
            'x': 10.0,
            'y': 5.0,  # South of garden (northern hemisphere)
            'height': 10.0,
            'canopy_radius': 2.0
        }]

        result = calculate_seasonal_garden_shading(
            garden_x=10.0,
            garden_y=15.0,
            garden_width=5.0,
            garden_height=5.0,
            trees=trees,
            latitude=40.0
        )

        assert Season.WINTER in result
        assert Season.EQUINOX in result
        assert Season.SUMMER in result

    def test_winter_more_shading_than_summer(self):
        """Winter typically has more shading due to longer shadows"""
        trees = [{
            'x': 10.0,
            'y': 5.0,
            'height': 10.0,
            'canopy_radius': 2.0
        }]

        result = calculate_seasonal_garden_shading(
            garden_x=10.0,
            garden_y=15.0,
            garden_width=5.0,
            garden_height=5.0,
            trees=trees,
            latitude=40.0
        )

        winter_pct = result[Season.WINTER]["shaded_percentage"]
        summer_pct = result[Season.SUMMER]["shaded_percentage"]

        # Winter shadows are longer, so should shade more
        assert winter_pct >= summer_pct

    def test_no_trees_no_shading(self):
        """No trees means no shading in any season"""
        result = calculate_seasonal_garden_shading(
            garden_x=10.0,
            garden_y=10.0,
            garden_width=5.0,
            garden_height=5.0,
            trees=[],
            latitude=40.0
        )

        for season, data in result.items():
            assert data["shaded_percentage"] == 0.0
            assert data["affected_by_count"] == 0


class TestExposureCategory:
    """Test sun exposure categorization"""

    def test_full_sun_category(self):
        """0-25% shading is Full Sun"""
        assert get_exposure_category(0.0) == "Full Sun"
        assert get_exposure_category(10.0) == "Full Sun"
        assert get_exposure_category(24.9) == "Full Sun"

    def test_partial_sun_category(self):
        """25-60% shading is Partial Sun"""
        assert get_exposure_category(25.0) == "Partial Sun"
        assert get_exposure_category(40.0) == "Partial Sun"
        assert get_exposure_category(59.9) == "Partial Sun"

    def test_shade_category(self):
        """60-100% shading is Shade"""
        assert get_exposure_category(60.0) == "Shade"
        assert get_exposure_category(80.0) == "Shade"
        assert get_exposure_category(100.0) == "Shade"


class TestSeasonalExposureScore:
    """Test seasonal exposure score calculation"""

    def test_no_shading_perfect_score(self):
        """No shading gives score of 1.0"""
        seasonal_shading = {
            Season.WINTER: {"shaded_percentage": 0.0},
            Season.EQUINOX: {"shaded_percentage": 0.0},
            Season.SUMMER: {"shaded_percentage": 0.0}
        }

        score = calculate_seasonal_exposure_score(seasonal_shading)
        assert score == pytest.approx(1.0, rel=0.01)

    def test_full_shading_zero_score(self):
        """Full shading gives score of 0.0"""
        seasonal_shading = {
            Season.WINTER: {"shaded_percentage": 100.0},
            Season.EQUINOX: {"shaded_percentage": 100.0},
            Season.SUMMER: {"shaded_percentage": 100.0}
        }

        score = calculate_seasonal_exposure_score(seasonal_shading)
        assert score == pytest.approx(0.0, rel=0.01)

    def test_partial_shading_mid_score(self):
        """50% shading gives score around 0.5"""
        seasonal_shading = {
            Season.WINTER: {"shaded_percentage": 50.0},
            Season.EQUINOX: {"shaded_percentage": 50.0},
            Season.SUMMER: {"shaded_percentage": 50.0}
        }

        score = calculate_seasonal_exposure_score(seasonal_shading)
        assert score == pytest.approx(0.5, rel=0.01)

    def test_variable_seasonal_shading(self):
        """Variable shading averages across seasons"""
        seasonal_shading = {
            Season.WINTER: {"shaded_percentage": 75.0},  # 25% sun
            Season.EQUINOX: {"shaded_percentage": 50.0},  # 50% sun
            Season.SUMMER: {"shaded_percentage": 25.0}   # 75% sun
        }

        score = calculate_seasonal_exposure_score(seasonal_shading)
        # Average: (0.25 + 0.5 + 0.75) / 3 = 0.5
        assert score == pytest.approx(0.5, rel=0.01)
