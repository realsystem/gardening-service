"""Grid configuration and snapping utilities for layout system

This module defines the grid resolution and provides utilities for snapping
coordinates to the grid. The grid is used only for visualization and placement
assistance - actual positions are stored in real-world units (meters/feet).
"""

# Grid resolution in units
# 1 unit is divided into 10 grid cells for fine-grained placement
GRID_RESOLUTION = 0.1  # 0.1 units per grid cell

# Inverse for faster calculations
GRID_CELLS_PER_UNIT = int(1.0 / GRID_RESOLUTION)  # 10 cells per unit


def snap_to_grid(value: float, grid_resolution: float = GRID_RESOLUTION) -> float:
    """
    Snap a coordinate value to the nearest grid intersection.

    Args:
        value: Coordinate value in real-world units
        grid_resolution: Grid cell size (default: 0.1 units)

    Returns:
        Snapped coordinate value

    Examples:
        >>> snap_to_grid(1.23)
        1.2
        >>> snap_to_grid(1.27)
        1.3
        >>> snap_to_grid(0.04)
        0.0
        >>> snap_to_grid(0.05)
        0.1
    """
    return round(value / grid_resolution) * grid_resolution


def snap_rectangle_to_grid(
    x: float,
    y: float,
    width: float,
    height: float,
    grid_resolution: float = GRID_RESOLUTION
) -> tuple[float, float, float, float]:
    """
    Snap all rectangle coordinates to grid.

    Args:
        x, y: Top-left corner coordinates
        width, height: Rectangle dimensions
        grid_resolution: Grid cell size (default: 0.1 units)

    Returns:
        Tuple of (snapped_x, snapped_y, snapped_width, snapped_height)

    Note:
        Dimensions are snapped independently to maintain size as much as possible.
    """
    snapped_x = snap_to_grid(x, grid_resolution)
    snapped_y = snap_to_grid(y, grid_resolution)
    snapped_width = snap_to_grid(width, grid_resolution)
    snapped_height = snap_to_grid(height, grid_resolution)

    return snapped_x, snapped_y, snapped_width, snapped_height


def validate_grid_aligned(value: float, grid_resolution: float = GRID_RESOLUTION, tolerance: float = 1e-9) -> bool:
    """
    Check if a value is aligned to the grid.

    Args:
        value: Coordinate value to check
        grid_resolution: Grid cell size (default: 0.1 units)
        tolerance: Floating-point comparison tolerance

    Returns:
        True if value is grid-aligned, False otherwise

    Examples:
        >>> validate_grid_aligned(1.0)
        True
        >>> validate_grid_aligned(1.2)
        True
        >>> validate_grid_aligned(1.234)
        False
    """
    if grid_resolution == 0:
        return True  # No grid, all values valid

    remainder = abs(value % grid_resolution)
    # Check if remainder is very close to 0 or very close to grid_resolution
    return remainder < tolerance or abs(remainder - grid_resolution) < tolerance


def get_grid_info(grid_resolution: float = GRID_RESOLUTION) -> dict:
    """
    Get grid configuration information.

    Args:
        grid_resolution: Grid cell size (default: 0.1 units)

    Returns:
        Dictionary with grid configuration details
    """
    return {
        "grid_resolution": grid_resolution,
        "cells_per_unit": int(1.0 / grid_resolution) if grid_resolution > 0 else None,
        "description": f"1 unit = {int(1.0 / grid_resolution)} grid cells" if grid_resolution > 0 else "No grid",
    }
