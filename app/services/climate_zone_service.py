"""Climate zone service for USDA zone determination"""
from typing import Optional


class ClimateZoneService:
    """
    Service to determine USDA climate zone from location.
    For MVP, uses simplified ZIP code mapping.
    In production, would use a proper geolocation API.
    """

    # Simplified USDA zone mapping by ZIP prefix (first digit)
    # This is a very rough approximation for demonstration
    ZIP_ZONE_MAP = {
        "0": "4a",  # Northeast (ME, VT, NH)
        "1": "6a",  # Northeast (MA, NY)
        "2": "7a",  # Mid-Atlantic (DC, MD, VA)
        "3": "7b",  # Southeast (NC, SC, GA, FL)
        "4": "6b",  # Midwest (KY, IN, OH, MI)
        "5": "5a",  # Upper Midwest (MN, WI, IA)
        "6": "6a",  # Midwest (IL, MO, KS)
        "7": "7a",  # South (TX, OK, AR, LA)
        "8": "7b",  # Mountain West (CO, AZ, NM)
        "9": "9b",  # West Coast (CA, OR, WA)
    }

    @classmethod
    def get_zone_from_zip(cls, zip_code: str) -> Optional[str]:
        """
        Get USDA zone from ZIP code.
        Uses simplified mapping based on first digit of ZIP.
        """
        if not zip_code or len(zip_code) < 5:
            return None

        first_digit = zip_code[0]
        return cls.ZIP_ZONE_MAP.get(first_digit)

    @classmethod
    def get_zone_from_coordinates(cls, latitude: float, longitude: float) -> Optional[str]:
        """
        Get USDA zone from lat/lon coordinates.
        For MVP, uses very rough latitude-based approximation.
        In production, would use proper USDA zone shapefile or API.
        """
        # Very rough approximation based on latitude
        if latitude >= 48:
            return "4a"
        elif latitude >= 45:
            return "5a"
        elif latitude >= 42:
            return "6a"
        elif latitude >= 38:
            return "7a"
        elif latitude >= 34:
            return "8a"
        elif latitude >= 28:
            return "9a"
        else:
            return "10a"
