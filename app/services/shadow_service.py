"""Shadow projection service for calculating tree shadows on gardens

This service projects 2D shadows from tall objects (trees, structures)
and calculates their impact on garden areas.

Design:
- Simple rectangular shadow projections
- No ray tracing or complex geometry
- Seasonal shadow calculation
- Area intersection for shading percentage
"""

from typing import List, Dict, Tuple, Optional
from app.utils.sun_model import (
    Season,
    get_hemisphere,
    get_sun_altitude,
    calculate_shadow_length,
    project_shadow_endpoint
)


class ShadowRectangle:
    """Represents a rectangular shadow projection"""

    def __init__(self, x: float, y: float, width: float, height: float):
        """
        Create a shadow rectangle.

        Args:
            x: Left x-coordinate
            y: Top y-coordinate
            width: Width of shadow
            height: Height of shadow
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }

    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get bounding box coordinates"""
        return (
            self.x,
            self.y,
            self.x + self.width,
            self.y + self.height
        )

    def intersects(self, other: 'ShadowRectangle') -> bool:
        """Check if this rectangle intersects with another"""
        x1_min, y1_min, x1_max, y1_max = self.get_bounds()
        x2_min, y2_min, x2_max, y2_max = other.get_bounds()

        # Check for no overlap (then negate)
        no_overlap = (
            x1_max <= x2_min or
            x2_max <= x1_min or
            y1_max <= y2_min or
            y2_max <= y1_min
        )

        return not no_overlap

    def intersection_area(self, other: 'ShadowRectangle') -> float:
        """Calculate intersection area with another rectangle"""
        if not self.intersects(other):
            return 0.0

        x1_min, y1_min, x1_max, y1_max = self.get_bounds()
        x2_min, y2_min, x2_max, y2_max = other.get_bounds()

        # Calculate intersection bounds
        x_overlap = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))
        y_overlap = max(0, min(y1_max, y2_max) - max(y1_min, y2_min))

        return x_overlap * y_overlap


def project_tree_shadow(
    tree_x: float,
    tree_y: float,
    tree_height: float,
    canopy_radius: float,
    latitude: float,
    season: Season
) -> ShadowRectangle:
    """
    Project shadow from a tree for given season and latitude.

    Simplification: Model tree + shadow as rectangle extending in shadow direction.

    Args:
        tree_x: Tree center x-coordinate
        tree_y: Tree center y-coordinate
        tree_height: Tree height in meters
        canopy_radius: Tree canopy radius in meters
        latitude: Land latitude
        season: Season for sun calculation

    Returns:
        ShadowRectangle representing the shadow projection
    """
    # Get sun parameters
    hemisphere = get_hemisphere(latitude)
    sun_altitude = get_sun_altitude(latitude, season)

    # Calculate shadow length from tree height
    shadow_length = calculate_shadow_length(tree_height, sun_altitude)

    # Get shadow endpoint
    shadow_end_x, shadow_end_y = project_shadow_endpoint(
        tree_x, tree_y, shadow_length, hemisphere
    )

    # Create shadow rectangle
    # Width is the canopy diameter (shadow width matches tree width)
    shadow_width = canopy_radius * 2

    # Determine rectangle bounds based on shadow direction
    if hemisphere.value == "northern":
        # Shadow extends north (positive Y)
        shadow_rect = ShadowRectangle(
            x=tree_x - canopy_radius,
            y=tree_y - canopy_radius,
            width=shadow_width,
            height=shadow_length + canopy_radius * 2
        )
    else:
        # Shadow extends south (negative Y)
        shadow_rect = ShadowRectangle(
            x=tree_x - canopy_radius,
            y=shadow_end_y - canopy_radius,
            width=shadow_width,
            height=shadow_length + canopy_radius * 2
        )

    return shadow_rect


def calculate_garden_shading(
    garden_x: float,
    garden_y: float,
    garden_width: float,
    garden_height: float,
    shadows: List[ShadowRectangle]
) -> Dict[str, any]:
    """
    Calculate shading impact on a garden from multiple shadows.

    Args:
        garden_x: Garden x-coordinate
        garden_y: Garden y-coordinate
        garden_width: Garden width
        garden_height: Garden height
        shadows: List of ShadowRectangle objects

    Returns:
        Dictionary with:
        - total_shaded_area: Total area of garden in shadow (m²)
        - shaded_percentage: Percentage of garden in shadow (0-100)
        - affected_by_count: Number of shadows affecting this garden
    """
    garden_rect = ShadowRectangle(garden_x, garden_y, garden_width, garden_height)
    garden_area = garden_width * garden_height

    if garden_area == 0:
        return {
            "total_shaded_area": 0.0,
            "shaded_percentage": 0.0,
            "affected_by_count": 0
        }

    # Calculate total shaded area
    # Note: Simple approach - may double-count overlapping shadows
    # For v1, this is acceptable (conservative estimate)
    total_shaded_area = 0.0
    affected_count = 0

    for shadow in shadows:
        intersection = garden_rect.intersection_area(shadow)
        if intersection > 0:
            total_shaded_area += intersection
            affected_count += 1

    # Cap at 100% (in case of shadow overlap double-counting)
    total_shaded_area = min(total_shaded_area, garden_area)
    shaded_percentage = (total_shaded_area / garden_area) * 100

    return {
        "total_shaded_area": total_shaded_area,
        "shaded_percentage": shaded_percentage,
        "affected_by_count": affected_count
    }


def calculate_seasonal_garden_shading(
    garden_x: float,
    garden_y: float,
    garden_width: float,
    garden_height: float,
    trees: List[dict],
    latitude: float
) -> Dict[Season, dict]:
    """
    Calculate garden shading for all seasons.

    Args:
        garden_x: Garden x-coordinate
        garden_y: Garden y-coordinate
        garden_width: Garden width
        garden_height: Garden height
        trees: List of tree dictionaries with keys: x, y, height, canopy_radius
        latitude: Land latitude

    Returns:
        Dictionary mapping Season to shading info
    """
    seasonal_shading = {}

    for season in Season:
        # Project shadows from all trees for this season
        shadows = []
        for tree in trees:
            shadow = project_tree_shadow(
                tree_x=tree['x'],
                tree_y=tree['y'],
                tree_height=tree['height'],
                canopy_radius=tree['canopy_radius'],
                latitude=latitude,
                season=season
            )
            shadows.append(shadow)

        # Calculate shading impact
        shading_info = calculate_garden_shading(
            garden_x, garden_y, garden_width, garden_height, shadows
        )

        seasonal_shading[season] = shading_info

    return seasonal_shading


def get_exposure_category(shaded_percentage: float) -> str:
    """
    Categorize sun exposure based on shaded percentage.

    Categories:
    - Full Sun: 0-25% shaded (>75% sun)
    - Partial Sun: 25-60% shaded (40-75% sun)
    - Shade: 60-100% shaded (<40% sun)

    Args:
        shaded_percentage: Percentage of area shaded (0-100)

    Returns:
        Exposure category string
    """
    if shaded_percentage < 25:
        return "Full Sun"
    elif shaded_percentage < 60:
        return "Partial Sun"
    else:
        return "Shade"


def calculate_seasonal_exposure_score(seasonal_shading: Dict[Season, dict]) -> float:
    """
    Calculate overall seasonal exposure score (0-1).

    Higher score = more sun exposure.
    Averages sun exposure across all seasons.

    Args:
        seasonal_shading: Dictionary mapping Season to shading info

    Returns:
        Exposure score from 0.0 (full shade) to 1.0 (full sun)
    """
    total_sun_exposure = 0.0

    for season, shading_info in seasonal_shading.items():
        # Convert shaded percentage to sun exposure percentage
        sun_percentage = 100 - shading_info['shaded_percentage']
        total_sun_exposure += sun_percentage / 100.0

    # Average across seasons
    avg_exposure = total_sun_exposure / len(Season)

    return avg_exposure
