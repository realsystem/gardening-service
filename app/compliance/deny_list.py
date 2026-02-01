"""Centralized deny-list for restricted/controlled plant species.

This module maintains the authoritative list of plant names that are prohibited
from the system due to legal/compliance requirements. This is a risk mitigation
feature, not agricultural guidance.

IMPORTANT: This system does not provide cultivation advice for any prohibited species.
"""
from typing import Set, List
import re


# Version of the deny-list for audit trails
DENY_LIST_VERSION = "1.0.0"

# Primary deny-list: controlled substances
# This list includes common names, scientific names, slang terms, and cultivar names
RESTRICTED_PLANT_NAMES: Set[str] = {
    # Cannabis - Scientific names
    "cannabis",
    "cannabis sativa",
    "cannabis indica",
    "cannabis ruderalis",

    # Cannabis - Common names
    "marijuana",
    "marihuana",
    "hemp",

    # Cannabis - Slang/street names
    "pot",
    "weed",
    "ganja",
    "mary jane",
    "bud",
    "dope",
    "grass",
    "reefer",
    "chronic",
    "herb",

    # Cannabis - Subspecies/cultivars (patterns)
    "indica",
    "sativa",
    "ruderalis",

    # Cannabis - Common cultivar patterns
    "og kush",
    "sour diesel",
    "white widow",
    "northern lights",
    "ak-47",
    "purple haze",
    "skunk",
    "haze",

    # CBD/THC related
    "cbd hemp",
    "thc",
    "cannabidiol",
}

# Pattern-based detection for evasive naming
RESTRICTED_PATTERNS: List[re.Pattern] = [
    re.compile(r"\bcannab", re.IGNORECASE),  # cannabis, cannabidiol, cannabinoid
    re.compile(r"\bcanab", re.IGNORECASE),   # common misspelling "canabis"
    re.compile(r"\bthc\b", re.IGNORECASE),
    re.compile(r"\bcbd\b", re.IGNORECASE),
    re.compile(r"\b(indica|sativa|ruderalis)\b", re.IGNORECASE),
    re.compile(r"\bmarijuana\b", re.IGNORECASE),
    re.compile(r"\bmarihuana\b", re.IGNORECASE),
    re.compile(r"\bganja\b", re.IGNORECASE),
    re.compile(r"\bhemp\b", re.IGNORECASE),  # industrial cannabis
    re.compile(r"\bpot\s+plant\b", re.IGNORECASE),
    re.compile(r"\bweed\s+(plant|strain|variety)\b", re.IGNORECASE),
]


class RestrictedPlantDetector:
    """Detector for restricted plant names and patterns."""

    def __init__(self):
        self.deny_list = RESTRICTED_PLANT_NAMES
        self.patterns = RESTRICTED_PATTERNS
        self.version = DENY_LIST_VERSION

    def is_restricted(
        self,
        common_name: str = None,
        scientific_name: str = None,
        species: str = None,
        genus: str = None,
        aliases: List[str] = None,
        notes: str = None
    ) -> tuple[bool, str]:
        """Check if any provided plant identifiers match restricted patterns.

        Args:
            common_name: Common name of plant
            scientific_name: Scientific/botanical name
            species: Species name
            genus: Genus name
            aliases: Alternative names
            notes: Plant notes or description

        Returns:
            Tuple of (is_restricted: bool, reason: str)
        """
        # Collect all text fields to check
        fields_to_check = []

        if common_name:
            fields_to_check.append(("common_name", common_name))
        if scientific_name:
            fields_to_check.append(("scientific_name", scientific_name))
        if species:
            fields_to_check.append(("species", species))
        if genus:
            fields_to_check.append(("genus", genus))
        if aliases:
            for alias in aliases:
                fields_to_check.append(("alias", alias))
        if notes:
            fields_to_check.append(("notes", notes))

        # Check exact matches (case-insensitive)
        for field_name, field_value in fields_to_check:
            normalized = field_value.lower().strip()
            if normalized in self.deny_list:
                return True, f"restricted_term_in_{field_name}"

        # Check pattern matches
        for field_name, field_value in fields_to_check:
            for pattern in self.patterns:
                if pattern.search(field_value):
                    return True, f"restricted_pattern_in_{field_name}"

        return False, ""

    def get_sanitized_reason(self, detailed_reason: str) -> str:
        """Get user-facing generic message (never reveal what was detected).

        Args:
            detailed_reason: Internal reason code

        Returns:
            Generic user-facing message
        """
        # Always return the same generic message
        return "This request violates platform usage policies and cannot be completed."

    def get_version(self) -> str:
        """Get deny-list version for audit trails."""
        return self.version


# Singleton instance
detector = RestrictedPlantDetector()


def check_plant_restricted(
    common_name: str = None,
    scientific_name: str = None,
    species: str = None,
    genus: str = None,
    aliases: List[str] = None,
    notes: str = None
) -> tuple[bool, str]:
    """Convenience function to check if plant is restricted.

    Returns:
        Tuple of (is_restricted: bool, internal_reason: str)
    """
    return detector.is_restricted(
        common_name=common_name,
        scientific_name=scientific_name,
        species=species,
        genus=genus,
        aliases=aliases,
        notes=notes
    )


def get_user_facing_message() -> str:
    """Get generic user-facing rejection message."""
    return detector.get_sanitized_reason("")
