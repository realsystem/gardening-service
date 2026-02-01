"""Unit tests for sun path model

Tests the deterministic sun angle calculations and shadow projection math.
"""
import pytest
import math
from app.utils.sun_model import (
    Season,
    Hemisphere,
    get_hemisphere,
    get_latitude_band,
    get_sun_altitude,
    calculate_shadow_length,
    get_shadow_direction,
    project_shadow_endpoint,
    get_seasonal_sun_info,
    SUN_ALTITUDES
)


class TestHemisphere:
    """Test hemisphere determination"""

    def test_northern_hemisphere_positive_latitude(self):
        """Positive latitudes are in Northern Hemisphere"""
        assert get_hemisphere(40.0) == Hemisphere.NORTHERN
        assert get_hemisphere(0.1) == Hemisphere.NORTHERN

    def test_southern_hemisphere_negative_latitude(self):
        """Negative latitudes are in Southern Hemisphere"""
        assert get_hemisphere(-40.0) == Hemisphere.SOUTHERN
        assert get_hemisphere(-0.1) == Hemisphere.SOUTHERN

    def test_equator_is_northern(self):
        """Equator (0°) is considered Northern Hemisphere"""
        assert get_hemisphere(0.0) == Hemisphere.NORTHERN


class TestLatitudeBand:
    """Test latitude band classification"""

    def test_tropical_band(self):
        """Latitudes 0-15° map to tropical band"""
        assert get_latitude_band(0.0) == "0-15"
        assert get_latitude_band(10.0) == "0-15"
        assert get_latitude_band(14.9) == "0-15"
        assert get_latitude_band(-10.0) == "0-15"

    def test_subtropical_band(self):
        """Latitudes 15-30° map to subtropical band"""
        assert get_latitude_band(15.0) == "15-30"
        assert get_latitude_band(20.0) == "15-30"
        assert get_latitude_band(29.9) == "15-30"
        assert get_latitude_band(-20.0) == "15-30"

    def test_temperate_band(self):
        """Latitudes 30-45° map to temperate band"""
        assert get_latitude_band(30.0) == "30-45"
        assert get_latitude_band(40.0) == "30-45"
        assert get_latitude_band(44.9) == "30-45"
        assert get_latitude_band(-35.0) == "30-45"

    def test_cool_temperate_band(self):
        """Latitudes 45-60° map to cool temperate band"""
        assert get_latitude_band(45.0) == "45-60"
        assert get_latitude_band(50.0) == "45-60"
        assert get_latitude_band(59.9) == "45-60"

    def test_subpolar_band(self):
        """Latitudes 60-75° map to subpolar band"""
        assert get_latitude_band(60.0) == "60-75"
        assert get_latitude_band(70.0) == "60-75"
        assert get_latitude_band(75.0) == "60-75"


class TestSunAltitude:
    """Test sun altitude angle retrieval"""

    def test_temperate_winter_altitude(self):
        """Temperate zone has low winter sun"""
        altitude = get_sun_altitude(40.0, Season.WINTER)
        assert altitude == 30
        assert altitude < get_sun_altitude(40.0, Season.EQUINOX)

    def test_temperate_summer_altitude(self):
        """Temperate zone has high summer sun"""
        altitude = get_sun_altitude(40.0, Season.SUMMER)
        assert altitude == 65
        assert altitude > get_sun_altitude(40.0, Season.EQUINOX)

    def test_tropical_minimal_variation(self):
        """Tropical zones have less seasonal variation"""
        lat = 10.0
        winter = get_sun_altitude(lat, Season.WINTER)
        summer = get_sun_altitude(lat, Season.SUMMER)
        variation = summer - winter
        assert variation < 30  # Less than 30° variation

    def test_subpolar_large_variation(self):
        """Subpolar zones have large seasonal variation"""
        lat = 65.0
        winter = get_sun_altitude(lat, Season.WINTER)
        summer = get_sun_altitude(lat, Season.SUMMER)
        variation = summer - winter
        assert variation >= 40  # At least 40° variation

    def test_altitude_constants_are_valid(self):
        """All sun altitude constants are valid angles"""
        for lat_band, seasons in SUN_ALTITUDES.items():
            for season, altitude in seasons.items():
                assert 0 < altitude < 90, f"Invalid altitude {altitude} for {lat_band}, {season}"


class TestShadowLength:
    """Test shadow length calculation"""

    def test_high_sun_short_shadow(self):
        """High sun altitude produces short shadows"""
        # 60° sun altitude
        height = 10.0
        shadow = calculate_shadow_length(height, 60)
        # tan(60°) ≈ 1.732, so shadow ≈ 10/1.732 ≈ 5.77
        assert shadow == pytest.approx(5.77, abs=0.01)
        assert shadow < height

    def test_low_sun_long_shadow(self):
        """Low sun altitude produces long shadows"""
        # 15° sun altitude
        height = 10.0
        shadow = calculate_shadow_length(height, 15)
        # tan(15°) ≈ 0.268, so shadow ≈ 10/0.268 ≈ 37.3
        assert shadow == pytest.approx(37.3, abs=0.1)
        assert shadow > 3 * height

    def test_medium_sun_medium_shadow(self):
        """45° sun produces shadow equal to height"""
        # tan(45°) = 1
        height = 10.0
        shadow = calculate_shadow_length(height, 45)
        assert shadow == pytest.approx(height, abs=0.01)

    def test_near_overhead_sun(self):
        """Nearly overhead sun produces minimal shadow"""
        height = 10.0
        shadow = calculate_shadow_length(height, 85)
        assert shadow < 1.0  # Very short shadow

    def test_zero_sun_altitude_raises_error(self):
        """Sun at horizon should raise error"""
        with pytest.raises(ValueError):
            calculate_shadow_length(10.0, 0)

    def test_negative_sun_altitude_raises_error(self):
        """Negative sun altitude should raise error"""
        with pytest.raises(ValueError):
            calculate_shadow_length(10.0, -10)

    def test_overhead_sun_zero_shadow(self):
        """Sun directly overhead produces no shadow"""
        shadow = calculate_shadow_length(10.0, 90)
        assert shadow == 0.0

    def test_different_heights_proportional_shadows(self):
        """Shadow length is proportional to height"""
        altitude = 30
        shadow_10m = calculate_shadow_length(10.0, altitude)
        shadow_20m = calculate_shadow_length(20.0, altitude)
        assert shadow_20m == pytest.approx(2 * shadow_10m, rel=0.01)


class TestShadowDirection:
    """Test shadow direction vectors"""

    def test_northern_hemisphere_north_shadow(self):
        """Northern hemisphere shadows point north"""
        dx, dy = get_shadow_direction(Hemisphere.NORTHERN)
        assert dx == 0.0
        assert dy == 1.0  # Positive Y is north

    def test_southern_hemisphere_south_shadow(self):
        """Southern hemisphere shadows point south"""
        dx, dy = get_shadow_direction(Hemisphere.SOUTHERN)
        assert dx == 0.0
        assert dy == -1.0  # Negative Y is south

    def test_direction_is_normalized(self):
        """Direction vectors should be unit vectors"""
        north_dx, north_dy = get_shadow_direction(Hemisphere.NORTHERN)
        north_magnitude = math.sqrt(north_dx**2 + north_dy**2)
        assert north_magnitude == pytest.approx(1.0)

        south_dx, south_dy = get_shadow_direction(Hemisphere.SOUTHERN)
        south_magnitude = math.sqrt(south_dx**2 + south_dy**2)
        assert south_magnitude == pytest.approx(1.0)


class TestShadowProjection:
    """Test shadow endpoint projection"""

    def test_northern_hemisphere_projection(self):
        """Shadow projects northward in Northern Hemisphere"""
        tree_x, tree_y = 10.0, 20.0
        shadow_length = 5.0

        shadow_x, shadow_y = project_shadow_endpoint(
            tree_x, tree_y, shadow_length, Hemisphere.NORTHERN
        )

        assert shadow_x == tree_x  # No east-west movement
        assert shadow_y == tree_y + shadow_length  # North (positive Y)

    def test_southern_hemisphere_projection(self):
        """Shadow projects southward in Southern Hemisphere"""
        tree_x, tree_y = 10.0, 20.0
        shadow_length = 5.0

        shadow_x, shadow_y = project_shadow_endpoint(
            tree_x, tree_y, shadow_length, Hemisphere.SOUTHERN
        )

        assert shadow_x == tree_x  # No east-west movement
        assert shadow_y == tree_y - shadow_length  # South (negative Y)

    def test_zero_shadow_length(self):
        """Zero shadow length gives same position"""
        tree_x, tree_y = 10.0, 20.0

        shadow_x, shadow_y = project_shadow_endpoint(
            tree_x, tree_y, 0.0, Hemisphere.NORTHERN
        )

        assert shadow_x == tree_x
        assert shadow_y == tree_y


class TestSeasonalSunInfo:
    """Test comprehensive seasonal sun information"""

    def test_info_contains_all_seasons(self):
        """Seasonal info includes all three seasons"""
        info = get_seasonal_sun_info(40.0)

        assert "winter" in info["seasons"]
        assert "equinox" in info["seasons"]
        assert "summer" in info["seasons"]

    def test_info_contains_metadata(self):
        """Info includes latitude and hemisphere"""
        info = get_seasonal_sun_info(40.0)

        assert info["latitude"] == 40.0
        assert info["hemisphere"] == "northern"
        assert info["latitude_band"] == "30-45"

    def test_season_data_structure(self):
        """Each season has complete data"""
        info = get_seasonal_sun_info(40.0)

        for season_name, season_data in info["seasons"].items():
            assert "sun_altitude_degrees" in season_data
            assert "shadow_direction" in season_data
            assert "shadow_multiplier" in season_data

            # Shadow multiplier should be positive
            assert season_data["shadow_multiplier"] > 0

    def test_winter_longest_shadows(self):
        """Winter should have largest shadow multiplier (longest shadows)"""
        info = get_seasonal_sun_info(40.0)

        winter_mult = info["seasons"]["winter"]["shadow_multiplier"]
        equinox_mult = info["seasons"]["equinox"]["shadow_multiplier"]
        summer_mult = info["seasons"]["summer"]["shadow_multiplier"]

        assert winter_mult > equinox_mult
        assert winter_mult > summer_mult

    def test_different_latitudes_different_angles(self):
        """Different latitudes produce different sun angles"""
        tropical_info = get_seasonal_sun_info(10.0)
        temperate_info = get_seasonal_sun_info(40.0)

        tropical_winter = tropical_info["seasons"]["winter"]["sun_altitude_degrees"]
        temperate_winter = temperate_info["seasons"]["winter"]["sun_altitude_degrees"]

        # Tropical has higher winter sun than temperate
        assert tropical_winter > temperate_winter


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_equator_latitude(self):
        """Equator should work correctly"""
        info = get_seasonal_sun_info(0.0)
        assert info["hemisphere"] == "northern"
        assert info["latitude_band"] == "0-15"

    def test_extreme_northern_latitude(self):
        """High northern latitude should work"""
        info = get_seasonal_sun_info(70.0)
        assert info["hemisphere"] == "northern"
        assert info["latitude_band"] == "60-75"

    def test_extreme_southern_latitude(self):
        """High southern latitude should work"""
        info = get_seasonal_sun_info(-70.0)
        assert info["hemisphere"] == "southern"
        assert info["latitude_band"] == "60-75"

    def test_very_short_tree(self):
        """Very short object still casts shadow"""
        height = 0.5
        shadow = calculate_shadow_length(height, 30)
        assert shadow > 0
        assert shadow == pytest.approx(height / math.tan(math.radians(30)), rel=0.01)

    def test_very_tall_tree(self):
        """Very tall object casts proportionally long shadow"""
        height = 30.0
        shadow = calculate_shadow_length(height, 15)
        assert shadow > 100  # Very long shadow at low sun angle
