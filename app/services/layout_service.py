"""Layout validation service for garden spatial placement"""
from typing import List, Optional, Dict, Tuple
from app.models.garden import Garden
from app.models.land import Land
from app.schemas.garden_layout import LayoutValidationError
from app.utils.grid_config import snap_to_grid, snap_rectangle_to_grid, validate_grid_aligned, GRID_RESOLUTION


def apply_snap_to_grid(
    x: float,
    y: float,
    width: float,
    height: float,
    snap_enabled: bool = True
) -> Tuple[float, float, float, float]:
    """
    Apply snap-to-grid to coordinates if enabled.

    Args:
        x, y: Top-left corner coordinates
        width, height: Rectangle dimensions
        snap_enabled: Whether to apply snapping (default: True)

    Returns:
        Tuple of (x, y, width, height), snapped if enabled
    """
    if snap_enabled:
        return snap_rectangle_to_grid(x, y, width, height)
    return x, y, width, height


def check_overlap(garden1: Dict[str, float], garden2: Dict[str, float], tolerance: float = 0.01) -> bool:
    """
    Check if two rectangular gardens overlap using AABB (Axis-Aligned Bounding Box) algorithm.

    Two rectangles do NOT overlap if:
    - Rectangle 1 is completely to the left of Rectangle 2, OR
    - Rectangle 1 is completely to the right of Rectangle 2, OR
    - Rectangle 1 is completely above Rectangle 2, OR
    - Rectangle 1 is completely below Rectangle 2

    Args:
        garden1: dict with keys 'x', 'y', 'width', 'height'
        garden2: dict with keys 'x', 'y', 'width', 'height'
        tolerance: Small epsilon value to handle floating-point precision errors (default: 0.01 units)

    Returns:
        True if gardens overlap, False otherwise

    Note: Gardens touching at edges/corners do NOT count as overlapping.
          A small tolerance is used to handle floating-point precision issues with snap-to-grid.
    """
    # Check if gardens do NOT overlap (negation gives us overlap)
    # Add tolerance to account for floating-point precision errors
    no_overlap = (
        garden1['x'] + garden1['width'] <= garden2['x'] + tolerance or   # g1 left of g2
        garden2['x'] + garden2['width'] <= garden1['x'] + tolerance or   # g1 right of g2
        garden1['y'] + garden1['height'] <= garden2['y'] + tolerance or  # g1 above g2
        garden2['y'] + garden2['height'] <= garden1['y'] + tolerance     # g1 below g2
    )
    return not no_overlap


def check_bounds(garden: Dict[str, float], land: Land) -> bool:
    """
    Check if garden fits within land boundaries.

    Args:
        garden: dict with keys 'x', 'y', 'width', 'height'
        land: Land model instance with width and height

    Returns:
        True if garden fits within bounds, False otherwise
    """
    return (
        garden['x'] >= 0 and
        garden['y'] >= 0 and
        garden['x'] + garden['width'] <= land.width and
        garden['y'] + garden['height'] <= land.height
    )


def validate_garden_placement(
    garden_id: int,
    land: Land,
    x: float,
    y: float,
    width: float,
    height: float,
    existing_gardens: List[Garden]
) -> Optional[LayoutValidationError]:
    """
    Comprehensive validation for garden placement on land.

    Validates:
    1. Garden fits within land boundaries
    2. Garden doesn't overlap with other gardens (excluding itself)

    Args:
        garden_id: ID of garden being placed (to exclude from overlap check)
        land: Land model instance
        x, y: Top-left coordinates of garden
        width, height: Garden dimensions
        existing_gardens: List of all gardens on the land

    Returns:
        LayoutValidationError if invalid, None if valid
    """
    new_garden = {'x': x, 'y': y, 'width': width, 'height': height}

    # Check bounds
    if not check_bounds(new_garden, land):
        return LayoutValidationError(
            error_type="out_of_bounds",
            message=(
                f"Garden exceeds land boundaries. "
                f"Garden: (x={x}, y={y}, width={width}, height={height}), "
                f"Land: (width={land.width}, height={land.height})"
            )
        )

    # Check overlaps with other gardens (excluding self)
    conflicting_ids = []
    for existing_garden in existing_gardens:
        # Skip self (when updating existing garden's position)
        if existing_garden.id == garden_id:
            continue

        # Skip gardens without complete spatial data
        if (existing_garden.x is None or existing_garden.y is None or
                existing_garden.width is None or existing_garden.height is None):
            continue

        existing_rect = {
            'x': existing_garden.x,
            'y': existing_garden.y,
            'width': existing_garden.width,
            'height': existing_garden.height
        }

        if check_overlap(new_garden, existing_rect):
            conflicting_ids.append(existing_garden.id)

    if conflicting_ids:
        return LayoutValidationError(
            error_type="overlap",
            message=(
                f"Garden overlaps with {len(conflicting_ids)} existing garden(s). "
                f"Conflicting garden IDs: {conflicting_ids}"
            ),
            conflicting_garden_ids=conflicting_ids
        )

    # All validations passed
    return None


def validate_spatial_data_complete(
    land_id: Optional[int],
    x: Optional[float],
    y: Optional[float],
    width: Optional[float],
    height: Optional[float]
) -> Optional[LayoutValidationError]:
    """
    Validate that spatial data is complete (all-or-nothing).

    Either all spatial fields must be provided (to place garden),
    or all must be None (to remove garden from layout).

    Args:
        land_id, x, y, width, height: Spatial field values

    Returns:
        LayoutValidationError if incomplete, None if valid
    """
    spatial_fields = [land_id, x, y, width, height]
    some_provided = any(f is not None for f in spatial_fields)
    all_provided = all(f is not None for f in spatial_fields)

    if some_provided and not all_provided:
        provided = []
        if land_id is not None:
            provided.append('land_id')
        if x is not None:
            provided.append('x')
        if y is not None:
            provided.append('y')
        if width is not None:
            provided.append('width')
        if height is not None:
            provided.append('height')

        return LayoutValidationError(
            error_type="incomplete_data",
            message=(
                f"All spatial fields (land_id, x, y, width, height) must be provided together. "
                f"Provided: {provided}. Missing fields must also be set."
            )
        )

    return None
