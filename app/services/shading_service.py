"""
Shading Service - Calculate tree shading impact on gardens

This service implements a simple, deterministic geometric model for tree shading:

1. Trees cast shade within their canopy radius
2. Shade intensity decreases linearly from trunk center to canopy edge
3. Gardens intersecting shade receive proportional sun exposure reduction
4. Sun exposure is converted to categorical levels (full/partial/shade)

Mathematical Model:
- At trunk center (distance = 0): shade_intensity = 1.0 (100% shade)
- At canopy edge (distance = radius): shade_intensity = 0.0 (0% shade)
- Linear interpolation: shade_intensity = 1.0 - (distance / radius)

Assumptions:
- 2D model (ignores sun angle, tree height effects)
- Constant shade throughout day (no time-of-day variation)
- No seasonal variation
- Circular canopy projection
- Linear intensity gradient (simplification of reality)

Future enhancements could include:
- Sun path modeling based on latitude and time of year
- Tree height and shadow length calculations
- Time-varying shade patterns
- Deciduous vs. evergreen trees
"""
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ShadingImpact:
    """Result of shading calculation for a garden"""
    garden_id: int
    sun_exposure_score: float  # 0.0 (full shade) to 1.0 (full sun)
    sun_exposure_category: str  # "full_sun", "partial_sun", "shade"
    contributing_trees: List[dict]  # List of trees contributing to shade
    total_shade_factor: float  # Overall shade reduction (0.0 to 1.0)


def calculate_circle_rectangle_intersection_area(
    cx: float, cy: float, radius: float,
    rect_x: float, rect_y: float, rect_width: float, rect_height: float
) -> float:
    """
    Calculate approximate intersection area between a circle and a rectangle.

    This is a simplified approximation that works well for typical use cases.
    For more precision, a Monte Carlo method could be used.

    Args:
        cx, cy: Circle center coordinates
        radius: Circle radius
        rect_x, rect_y: Rectangle top-left corner
        rect_width, rect_height: Rectangle dimensions

    Returns:
        Approximate intersection area
    """
    # Check if circle and rectangle intersect
    # Find closest point on rectangle to circle center
    closest_x = max(rect_x, min(cx, rect_x + rect_width))
    closest_y = max(rect_y, min(cy, rect_y + rect_height))

    distance = math.sqrt((cx - closest_x)**2 + (cy - closest_y)**2)

    if distance > radius:
        return 0.0  # No intersection

    # Simplified approximation using grid sampling
    # For better accuracy, increase sample_points
    sample_points = 20
    step_x = rect_width / sample_points
    step_y = rect_height / sample_points

    intersection_count = 0
    total_points = sample_points * sample_points

    for i in range(sample_points):
        for j in range(sample_points):
            # Sample point at center of grid cell
            px = rect_x + (i + 0.5) * step_x
            py = rect_y + (j + 0.5) * step_y

            dist_from_center = math.sqrt((px - cx)**2 + (py - cy)**2)
            if dist_from_center <= radius:
                intersection_count += 1

    # Approximate intersection area
    rect_area = rect_width * rect_height
    intersection_ratio = intersection_count / total_points
    return rect_area * intersection_ratio


def calculate_average_shade_intensity(
    tree_x: float, tree_y: float, canopy_radius: float,
    rect_x: float, rect_y: float, rect_width: float, rect_height: float
) -> float:
    """
    Calculate average shade intensity over the intersection area.

    Shade intensity decreases linearly from trunk to canopy edge:
    - At center: intensity = 1.0 (100% shade)
    - At edge: intensity = 0.0 (0% shade)

    Args:
        tree_x, tree_y: Tree trunk center coordinates
        canopy_radius: Tree canopy radius
        rect_x, rect_y: Rectangle (garden) top-left corner
        rect_width, rect_height: Rectangle dimensions

    Returns:
        Average shade intensity (0.0 to 1.0) over intersection area
    """
    # Use grid sampling to calculate average intensity
    sample_points = 20
    step_x = rect_width / sample_points
    step_y = rect_height / sample_points

    total_intensity = 0.0
    sample_count = 0

    for i in range(sample_points):
        for j in range(sample_points):
            # Sample point at center of grid cell
            px = rect_x + (i + 0.5) * step_x
            py = rect_y + (j + 0.5) * step_y

            distance = math.sqrt((px - tree_x)**2 + (py - tree_y)**2)

            if distance <= canopy_radius:
                # Point is within canopy - calculate shade intensity
                # Linear decrease: intensity = 1.0 - (distance / radius)
                intensity = 1.0 - (distance / canopy_radius)
                total_intensity += intensity
                sample_count += 1

    if sample_count == 0:
        return 0.0  # No intersection

    return total_intensity / sample_count


def calculate_garden_shading(
    garden_x: float, garden_y: float, garden_width: float, garden_height: float,
    trees: List[dict],
    baseline_sun_exposure: float = 1.0
) -> ShadingImpact:
    """
    Calculate shading impact on a garden from multiple trees.

    Args:
        garden_x, garden_y: Garden top-left corner
        garden_width, garden_height: Garden dimensions
        trees: List of tree dicts with keys: id, name, x, y, canopy_radius
        baseline_sun_exposure: Baseline sun exposure without trees (0.0 to 1.0)

    Returns:
        ShadingImpact object with calculated sun exposure and contributing trees
    """
    garden_id = trees[0].get('garden_id') if trees else None
    contributing_trees = []
    cumulative_shade = 0.0

    garden_area = garden_width * garden_height

    for tree in trees:
        tree_x = tree['x']
        tree_y = tree['y']
        canopy_radius = tree['canopy_radius']

        # Calculate intersection area
        intersection_area = calculate_circle_rectangle_intersection_area(
            tree_x, tree_y, canopy_radius,
            garden_x, garden_y, garden_width, garden_height
        )

        if intersection_area > 0:
            # Calculate average shade intensity in intersection
            avg_intensity = calculate_average_shade_intensity(
                tree_x, tree_y, canopy_radius,
                garden_x, garden_y, garden_width, garden_height
            )

            # Shade contribution = intensity * (intersection_area / garden_area)
            shade_contribution = avg_intensity * (intersection_area / garden_area)
            cumulative_shade += shade_contribution

            contributing_trees.append({
                'tree_id': tree['id'],
                'tree_name': tree['name'],
                'shade_contribution': shade_contribution,
                'intersection_area': intersection_area,
                'average_intensity': avg_intensity
            })

    # Clamp cumulative shade between 0 and 1
    cumulative_shade = min(1.0, max(0.0, cumulative_shade))

    # Calculate final sun exposure
    # Sun exposure = baseline * (1 - shade)
    sun_exposure_score = baseline_sun_exposure * (1.0 - cumulative_shade)

    # Determine categorical sun exposure
    sun_exposure_category = _categorize_sun_exposure(sun_exposure_score)

    return ShadingImpact(
        garden_id=garden_id,
        sun_exposure_score=sun_exposure_score,
        sun_exposure_category=sun_exposure_category,
        contributing_trees=contributing_trees,
        total_shade_factor=cumulative_shade
    )


def _categorize_sun_exposure(score: float) -> str:
    """
    Convert numerical sun exposure score to categorical level.

    Categories based on typical gardening definitions:
    - full_sun: 6+ hours direct sun (score >= 0.75)
    - partial_sun: 3-6 hours (score 0.4 to 0.75)
    - shade: < 3 hours (score < 0.4)

    Args:
        score: Sun exposure score (0.0 to 1.0)

    Returns:
        Category string: "full_sun", "partial_sun", or "shade"
    """
    if score >= 0.75:
        return "full_sun"
    elif score >= 0.4:
        return "partial_sun"
    else:
        return "shade"


def calculate_tree_coverage_area(canopy_radius: float) -> float:
    """
    Calculate the area covered by a tree's canopy.

    Args:
        canopy_radius: Tree canopy radius

    Returns:
        Canopy area (π * r²)
    """
    return math.pi * canopy_radius ** 2
