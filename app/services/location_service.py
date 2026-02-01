"""Location and geocoding service for ZIP code processing

This service handles ZIP code validation, geocoding, and unit system detection.
For production use, integrate with a geocoding API like:
- Google Maps Geocoding API
- OpenCage Geocoder
- ZipCodeBase API
"""

import re
from typing import Optional, Tuple
from app.models.user import UnitSystem


class LocationService:
    """Service for handling location-based operations"""

    @staticmethod
    def is_us_zip_code(zip_code: str) -> bool:
        """
        Check if a ZIP code appears to be a US ZIP code.

        US ZIP codes are either:
        - 5 digits (e.g., "12345")
        - 5 digits + 4 digits with hyphen (e.g., "12345-6789")

        Args:
            zip_code: ZIP/postal code string

        Returns:
            True if appears to be US ZIP code, False otherwise
        """
        if not zip_code:
            return False

        # US ZIP code patterns
        five_digit = re.match(r'^\d{5}$', zip_code.strip())
        nine_digit = re.match(r'^\d{5}-\d{4}$', zip_code.strip())

        return bool(five_digit or nine_digit)

    @staticmethod
    def detect_unit_system(zip_code: Optional[str]) -> UnitSystem:
        """
        Detect appropriate unit system based on ZIP code.

        Args:
            zip_code: ZIP/postal code string

        Returns:
            UnitSystem.IMPERIAL for US ZIP codes, UnitSystem.METRIC otherwise
        """
        if not zip_code:
            return UnitSystem.METRIC  # Default to metric

        if LocationService.is_us_zip_code(zip_code):
            return UnitSystem.IMPERIAL  # US uses imperial (feet, fahrenheit)
        else:
            return UnitSystem.METRIC  # Rest of world uses metric

    @staticmethod
    def geocode_zip_code(zip_code: str) -> Optional[Tuple[float, float]]:
        """
        Convert ZIP code to latitude/longitude coordinates.

        This is a placeholder implementation. In production, integrate with:
        - Google Maps Geocoding API
        - OpenCage Geocoder
        - ZipCodeBase API
        - USPS API for US ZIP codes

        Args:
            zip_code: ZIP/postal code string

        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails

        Example integration with zipcodebase.com:
        ```python
        import requests

        api_key = "your_api_key"
        response = requests.get(
            f"https://app.zipcodebase.com/api/v1/search",
            headers={"apikey": api_key},
            params={"codes": zip_code, "country": "US"}
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                result = data["results"][zip_code][0]
                return (float(result["latitude"]), float(result["longitude"]))
        return None
        ```
        """
        # Placeholder: Return None to indicate geocoding not available
        # When implementing, remove this comment and add real geocoding logic

        # For development/testing, you could add hardcoded mappings for common ZIPs:
        # SAMPLE_ZIP_COORDINATES = {
        #     "94102": (37.7749, -122.4194),  # San Francisco, CA
        #     "10001": (40.7506, -73.9971),   # New York, NY
        #     "60601": (41.8859, -87.6181),   # Chicago, IL
        #     "90001": (33.9731, -118.2479),  # Los Angeles, CA
        # }
        # return SAMPLE_ZIP_COORDINATES.get(zip_code.split("-")[0])

        return None

    @staticmethod
    def get_default_coordinates_for_unit_system(unit_system: UnitSystem) -> Tuple[float, float]:
        """
        Get default coordinates based on unit system.

        Returns reasonable defaults when geocoding is unavailable.

        Args:
            unit_system: The user's unit system preference

        Returns:
            Tuple of (latitude, longitude)
        """
        if unit_system == UnitSystem.IMPERIAL:
            # Default to US center (Kansas) for imperial users
            return (39.8283, -98.5795)
        else:
            # Default to European center for metric users
            return (50.8503, 4.3517)  # Brussels, Belgium

    @staticmethod
    def process_user_zip_code(
        zip_code: Optional[str]
    ) -> Tuple[UnitSystem, Optional[float], Optional[float]]:
        """
        Process a ZIP code and return unit system and coordinates.

        This is the main entry point for ZIP code processing during user registration.

        Args:
            zip_code: ZIP/postal code string

        Returns:
            Tuple of (unit_system, latitude, longitude)
            Latitude and longitude will be None if geocoding fails
        """
        # Detect unit system based on ZIP code format
        unit_system = LocationService.detect_unit_system(zip_code)

        # Try to geocode the ZIP code
        coordinates = None
        if zip_code:
            coordinates = LocationService.geocode_zip_code(zip_code)

        # If geocoding succeeded, return coordinates
        if coordinates:
            latitude, longitude = coordinates
            return (unit_system, latitude, longitude)

        # If geocoding failed but we have a ZIP code, return defaults
        # This allows the user to still use the app with reasonable defaults
        if zip_code:
            latitude, longitude = LocationService.get_default_coordinates_for_unit_system(unit_system)
            return (unit_system, latitude, longitude)

        # No ZIP code provided - return metric with no coordinates
        return (UnitSystem.METRIC, None, None)
