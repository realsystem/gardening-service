"""Sun path model for seasonal shadow calculations

This module provides deterministic, testable sun position approximations
for calculating seasonal shadows cast by trees and structures.

Design principles:
- Simple, explainable formulas
- No real-time tracking or hourly simulation
- Season-based buckets (Winter, Equinox, Summer)
- Latitude-band approximations
- 2D projection only

Assumptions:
- Northern Hemisphere: shadows cast northward
- Southern Hemisphere: shadows cast southward
- Midday sun position (highest altitude of the day)
- Clear sky conditions
- No terrain slope or reflections
"""

from enum import Enum
from typing import Tuple
import math


class Season(str, Enum):
    """Seasonal buckets for sun position calculation"""
    WINTER = "winter"  # December solstice
    EQUINOX = "equinox"  # March/September equinox
    SUMMER = "summer"  # June solstice


class Hemisphere(str, Enum):
    """Hemisphere determines shadow direction"""
    NORTHERN = "northern"
    SOUTHERN = "southern"


# Sun altitude angles (degrees above horizon at solar noon)
# Organized by latitude band and season
# These are approximations for midday sun during each season

SUN_ALTITUDES = {
    # Latitude band 0-15° (Tropics)
    "0-15": {
        Season.WINTER: 60,   # Still high sun
        Season.EQUINOX: 75,  # Nearly overhead
        Season.SUMMER: 80,   # Very high
    },
    # Latitude band 15-30° (Subtropics)
    "15-30": {
        Season.WINTER: 50,
        Season.EQUINOX: 65,
        Season.SUMMER: 75,
    },
    # Latitude band 30-45° (Temperate)
    "30-45": {
        Season.WINTER: 30,   # Low winter sun
        Season.EQUINOX: 50,  # Medium
        Season.SUMMER: 65,   # High summer sun
    },
    # Latitude band 45-60° (Cool Temperate)
    "45-60": {
        Season.WINTER: 15,   # Very low winter sun
        Season.EQUINOX: 40,
        Season.SUMMER: 55,
    },
    # Latitude band 60-75° (Subpolar)
    "60-75": {
        Season.WINTER: 5,    # Extreme low (near horizon)
        Season.EQUINOX: 30,
        Season.SUMMER: 45,
    },
}

# Default fallback for missing latitude
DEFAULT_LATITUDE = 40.0  # Temperate zone
DEFAULT_LATITUDE_BAND = "30-45"


def get_hemisphere(latitude: float) -> Hemisphere:
    """
    Determine hemisphere from latitude.

    Args:
        latitude: Latitude in degrees (-90 to 90)

    Returns:
        Hemisphere enum
    """
    return Hemisphere.NORTHERN if latitude >= 0 else Hemisphere.SOUTHERN


def get_latitude_band(latitude: float) -> str:
    """
    Get latitude band key for sun altitude lookup.

    Args:
        latitude: Latitude in degrees (-90 to 90)

    Returns:
        Latitude band string key (e.g., "30-45")
    """
    abs_lat = abs(latitude)

    if abs_lat < 15:
        return "0-15"
    elif abs_lat < 30:
        return "15-30"
    elif abs_lat < 45:
        return "30-45"
    elif abs_lat < 60:
        return "45-60"
    else:
        return "60-75"


def get_sun_altitude(latitude: float, season: Season) -> float:
    """
    Get sun altitude angle for given latitude and season.

    Returns midday sun altitude (highest point of the day).

    Args:
        latitude: Latitude in degrees (-90 to 90)
        season: Season enum

    Returns:
        Sun altitude in degrees above horizon (0-90)
    """
    lat_band = get_latitude_band(latitude)
    altitude = SUN_ALTITUDES[lat_band][season]
    return float(altitude)


def calculate_shadow_length(height: float, sun_altitude_degrees: float) -> float:
    """
    Calculate shadow length from object height and sun altitude.

    Formula: shadow_length = height / tan(sun_altitude)

    Args:
        height: Object height in meters
        sun_altitude_degrees: Sun altitude angle in degrees (0-90)

    Returns:
        Shadow length in meters

    Raises:
        ValueError: If sun_altitude is <= 0 or >= 90
    """
    if sun_altitude_degrees <= 0:
        raise ValueError("Sun altitude must be > 0 degrees")
    if sun_altitude_degrees >= 90:
        # Sun directly overhead, no shadow
        return 0.0

    # Convert to radians for trigonometry
    sun_altitude_rad = math.radians(sun_altitude_degrees)

    # Calculate shadow length using tangent
    shadow_length = height / math.tan(sun_altitude_rad)

    return shadow_length


def get_shadow_direction(hemisphere: Hemisphere) -> Tuple[float, float]:
    """
    Get shadow direction vector based on hemisphere.

    In Northern Hemisphere: shadows point north (negative Y in canvas coordinates)
    In Southern Hemisphere: shadows point south (positive Y in canvas coordinates)

    Canvas coordinate system: Y increases downward (south), decreases upward (north).

    Returns normalized direction vector (dx, dy).

    Args:
        hemisphere: Hemisphere enum

    Returns:
        Tuple of (dx, dy) normalized direction vector
    """
    if hemisphere == Hemisphere.NORTHERN:
        # North direction (negative Y in canvas coordinate system - upward)
        return (0.0, -1.0)
    else:
        # South direction (positive Y in canvas coordinate system - downward)
        return (0.0, 1.0)


def project_shadow_endpoint(
    x: float,
    y: float,
    shadow_length: float,
    hemisphere: Hemisphere
) -> Tuple[float, float]:
    """
    Project shadow endpoint from object position.

    Args:
        x: Object x-coordinate
        y: Object y-coordinate
        shadow_length: Shadow length in meters
        hemisphere: Hemisphere enum

    Returns:
        Tuple of (shadow_x, shadow_y) endpoint coordinates
    """
    dx, dy = get_shadow_direction(hemisphere)

    shadow_x = x + (dx * shadow_length)
    shadow_y = y + (dy * shadow_length)

    return (shadow_x, shadow_y)


def get_sun_azimuth(hour: float, hemisphere: Hemisphere) -> float:
    """
    Calculate sun azimuth angle based on time of day.

    Azimuth is measured clockwise from north (0° = north, 90° = east, 180° = south, 270° = west).

    Simplified model:
    - 6 AM: Sun rises in east (90°)
    - 12 PM: Sun at south (180°) for northern, north (0°/360°) for southern hemisphere
    - 6 PM: Sun sets in west (270°)

    Args:
        hour: Hour of day (0-24, can be decimal for minutes)
        hemisphere: Hemisphere enum

    Returns:
        Azimuth angle in degrees (0-360)
    """
    # Clamp hour to valid range
    hour = max(0, min(24, hour))

    # Sun path spans from 6 AM to 6 PM (12-hour arc)
    # Outside this range, sun is below horizon
    if hour < 6:
        hour = 6  # Before sunrise, use sunrise position
    elif hour > 18:
        hour = 18  # After sunset, use sunset position

    # Calculate sun position along its arc
    # Progress from 0 (sunrise) to 1 (sunset)
    sun_progress = (hour - 6) / 12.0

    if hemisphere == Hemisphere.NORTHERN:
        # Northern hemisphere: sun moves east -> south -> west
        # Azimuth from 90° (east) to 180° (south) to 270° (west)
        azimuth = 90 + (sun_progress * 180)
    else:
        # Southern hemisphere: sun moves east -> north -> west
        # Azimuth from 90° (east) to 0°/360° (north) to 270° (west)
        # This creates a path through the northern sky
        if sun_progress < 0.5:
            # Morning: 90° to 0° (going counter-clockwise toward north)
            azimuth = 90 - (sun_progress * 2 * 90)
        else:
            # Afternoon: 0° to 270° (continuing through north to west)
            # Map 0.5-1.0 to 0°-270° (going counter-clockwise)
            azimuth = 360 - ((sun_progress - 0.5) * 2 * 90)

    return azimuth


def get_sun_altitude_at_time(latitude: float, season: Season, hour: float) -> float:
    """
    Calculate sun altitude at a specific time of day.

    Uses a simplified sinusoidal model where altitude peaks at solar noon (12 PM).

    Args:
        latitude: Latitude in degrees
        season: Season enum
        hour: Hour of day (0-24)

    Returns:
        Sun altitude in degrees (0-90), or 0 if sun is below horizon
    """
    # Get max altitude at solar noon
    max_altitude = get_sun_altitude(latitude, season)

    # Clamp hour
    hour = max(0, min(24, hour))

    # Sun is up from ~6 AM to ~6 PM
    if hour < 6 or hour > 18:
        return 0.0  # Below horizon

    # Calculate altitude using sinusoidal curve
    # Peak at 12 PM, zero at 6 AM and 6 PM
    hours_since_sunrise = hour - 6
    sun_fraction = hours_since_sunrise / 12.0  # 0 to 1

    # Sin curve: peaks at 0.5 (noon)
    altitude = max_altitude * math.sin(sun_fraction * math.pi)

    return max(0.0, altitude)


def get_shadow_direction_at_time(hour: float, hemisphere: Hemisphere) -> Tuple[float, float]:
    """
    Get shadow direction vector based on time of day and hemisphere.

    Canvas coordinates: Y increases downward (south), X increases right (east).

    Args:
        hour: Hour of day (0-24)
        hemisphere: Hemisphere enum

    Returns:
        Tuple of (dx, dy) normalized direction vector
    """
    azimuth = get_sun_azimuth(hour, hemisphere)

    # Convert azimuth to shadow direction (opposite of sun direction)
    # Shadow points away from the sun
    # Azimuth: 0° = north, 90° = east, 180° = south, 270° = west
    # Shadow direction is 180° opposite
    shadow_azimuth = (azimuth + 180) % 360

    # Convert to radians
    shadow_azimuth_rad = math.radians(shadow_azimuth)

    # Convert to canvas coordinates (Y down = south, X right = east)
    # Azimuth 0° (north) -> (0, -1)  (up)
    # Azimuth 90° (east) -> (1, 0)   (right)
    # Azimuth 180° (south) -> (0, 1) (down)
    # Azimuth 270° (west) -> (-1, 0) (left)

    dx = math.sin(shadow_azimuth_rad)
    dy = -math.cos(shadow_azimuth_rad)  # Negative because canvas Y is inverted

    return (dx, dy)


def project_shadow_endpoint_at_time(
    x: float,
    y: float,
    shadow_length: float,
    hour: float,
    hemisphere: Hemisphere
) -> Tuple[float, float]:
    """
    Project shadow endpoint from object position at a specific time.

    Args:
        x: Object x-coordinate
        y: Object y-coordinate
        shadow_length: Shadow length in meters
        hour: Hour of day (0-24)
        hemisphere: Hemisphere enum

    Returns:
        Tuple of (shadow_x, shadow_y) endpoint coordinates
    """
    dx, dy = get_shadow_direction_at_time(hour, hemisphere)

    shadow_x = x + (dx * shadow_length)
    shadow_y = y + (dy * shadow_length)

    return (shadow_x, shadow_y)


def get_seasonal_sun_info(latitude: float) -> dict:
    """
    Get comprehensive seasonal sun information for a location.

    Args:
        latitude: Latitude in degrees

    Returns:
        Dictionary with sun altitude and shadow info for each season
    """
    hemisphere = get_hemisphere(latitude)
    lat_band = get_latitude_band(latitude)

    info = {
        "latitude": latitude,
        "hemisphere": hemisphere.value,
        "latitude_band": lat_band,
        "seasons": {}
    }

    for season in Season:
        altitude = get_sun_altitude(latitude, season)
        info["seasons"][season.value] = {
            "sun_altitude_degrees": altitude,
            "shadow_direction": get_shadow_direction(hemisphere),
            "shadow_multiplier": 1.0 / math.tan(math.radians(altitude)) if altitude > 0 else float('inf')
        }

    return info
