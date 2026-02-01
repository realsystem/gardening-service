"""
Unit tests for companion planting logic.

Tests core companion planting analysis functions without database dependencies.
"""

import pytest
import math
from app.api.companion_analysis import (
    calculate_distance,
    normalize_plant_pair
)


class TestDistanceCalculation:
    """Test distance calculation between plants."""

    def test_distance_same_point(self):
        """Distance between same point should be 0."""
        assert calculate_distance(0, 0, 0, 0) == 0.0
        assert calculate_distance(5.5, 3.2, 5.5, 3.2) == 0.0

    def test_distance_horizontal(self):
        """Distance along x-axis only."""
        assert calculate_distance(0, 0, 3, 0) == 3.0
        assert calculate_distance(2, 5, 7, 5) == 5.0

    def test_distance_vertical(self):
        """Distance along y-axis only."""
        assert calculate_distance(0, 0, 0, 4) == 4.0
        assert calculate_distance(3, 2, 3, 8) == 6.0

    def test_distance_diagonal(self):
        """Distance along diagonal (Pythagorean theorem)."""
        # 3-4-5 triangle
        assert calculate_distance(0, 0, 3, 4) == 5.0
        # 5-12-13 triangle
        assert calculate_distance(0, 0, 5, 12) == 13.0

    def test_distance_negative_coordinates(self):
        """Distance calculation handles negative coordinates."""
        assert calculate_distance(-3, -4, 0, 0) == 5.0
        assert calculate_distance(-2, 5, 3, 1) == pytest.approx(6.4031, rel=1e-3)

    def test_distance_floating_point(self):
        """Distance calculation with floating point coordinates."""
        d = calculate_distance(1.5, 2.5, 4.5, 6.5)
        expected = math.sqrt((4.5-1.5)**2 + (6.5-2.5)**2)
        assert d == pytest.approx(expected, rel=1e-10)


class TestPlantPairNormalization:
    """Test plant pair normalization for bidirectional relationships."""

    def test_normalize_already_ordered(self):
        """Pairs already in order (a < b) remain unchanged."""
        assert normalize_plant_pair(1, 2) == (1, 2)
        assert normalize_plant_pair(5, 10) == (5, 10)
        assert normalize_plant_pair(100, 101) == (100, 101)

    def test_normalize_reverse_order(self):
        """Pairs in reverse order (a > b) are swapped."""
        assert normalize_plant_pair(2, 1) == (1, 2)
        assert normalize_plant_pair(10, 5) == (5, 10)
        assert normalize_plant_pair(101, 100) == (100, 101)

    def test_normalize_same_id(self):
        """Same ID returns same pair (edge case, shouldn't occur in practice)."""
        assert normalize_plant_pair(5, 5) == (5, 5)

    def test_normalize_large_ids(self):
        """Normalization works with large ID values."""
        assert normalize_plant_pair(999999, 1000000) == (999999, 1000000)
        assert normalize_plant_pair(1000000, 999999) == (999999, 1000000)

    def test_normalize_consistency(self):
        """Normalizing the same pair multiple times gives same result."""
        pair1 = normalize_plant_pair(42, 17)
        pair2 = normalize_plant_pair(42, 17)
        pair3 = normalize_plant_pair(17, 42)
        assert pair1 == pair2 == pair3 == (17, 42)


@pytest.mark.companion_planting
class TestCompanionPlantingLogic:
    """Integration tests for companion planting logic (marked for easy filtering)."""

    def test_effective_distance_calculation(self):
        """Test if plants are within effective distance."""
        # Plants 1.5m apart, effective distance is 2.0m
        distance = calculate_distance(0, 0, 1.5, 0)
        assert distance <= 2.0  # Within effective range

        # Plants 2.5m apart, effective distance is 2.0m
        distance = calculate_distance(0, 0, 2.5, 0)
        assert distance > 2.0  # Outside effective range

    def test_optimal_distance_calculation(self):
        """Test if plants are within optimal distance."""
        # Plants 0.4m apart, optimal distance is 0.5m
        distance = calculate_distance(0, 0, 0.4, 0)
        assert distance <= 0.5  # Within optimal range

        # Plants 0.6m apart, optimal distance is 0.5m
        distance = calculate_distance(0, 0, 0.6, 0)
        assert distance > 0.5  # Outside optimal range


# Marker for pytest
pytestmark = pytest.mark.companion_planting
