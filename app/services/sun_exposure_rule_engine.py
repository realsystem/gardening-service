"""Science-based rule engine for sun exposure analysis

This module implements deterministic rules for evaluating garden placement
relative to seasonal sun exposure and plant requirements.

Rules are grounded in plant physiology and provide explainable feedback.
NO ML predictions, NO false precision, NO speculative claims.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class RuleSeverity(str, Enum):
    """Rule severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class SunExposureRule:
    """Represents a triggered sun exposure rule"""
    rule_id: str
    severity: RuleSeverity
    title: str
    explanation: str
    suggested_action: str
    affected_gardens: List[int] = None
    affected_trees: List[int] = None

    def __post_init__(self):
        if self.affected_gardens is None:
            self.affected_gardens = []
        if self.affected_trees is None:
            self.affected_trees = []


class SunExposureRuleEngine:
    """
    Evaluates garden sun exposure against science-based rules.

    Rules explain WHY sun exposure matters for plant health and productivity.
    """

    # Plant sun requirement categories (standard horticulture classification)
    SUN_REQUIREMENTS = {
        "full_sun": {
            "min_hours": 6,
            "description": "6+ hours direct sun",
            "examples": "Tomatoes, peppers, squash, most fruiting vegetables"
        },
        "partial_sun": {
            "min_hours": 3,
            "max_hours": 6,
            "description": "3-6 hours direct sun",
            "examples": "Lettuce, spinach, peas, root vegetables"
        },
        "shade": {
            "max_hours": 3,
            "description": "<3 hours direct sun",
            "examples": "Shade-tolerant herbs, ferns, hostas"
        }
    }

    @staticmethod
    def evaluate_exposure_category_match(
        garden_exposure_category: str,
        plant_sun_requirement: Optional[str],
        garden_id: int,
        seasonal_shading: Dict[str, dict]
    ) -> List[SunExposureRule]:
        """
        Evaluate if garden exposure matches plant requirements.

        Science basis: Plants have evolved for specific light levels.
        Insufficient sun reduces photosynthesis, growth, and yield.
        Excess sun can stress shade-adapted plants.

        Args:
            garden_exposure_category: "Full Sun", "Partial Sun", or "Shade"
            plant_sun_requirement: Expected plant requirement (if known)
            garden_id: Garden ID
            seasonal_shading: Seasonal shading data

        Returns:
            List of triggered rules
        """
        rules = []

        # If no plant requirement specified, provide informational context
        if not plant_sun_requirement:
            if garden_exposure_category == "Shade":
                rules.append(SunExposureRule(
                    rule_id="SUN_001",
                    severity=RuleSeverity.INFO,
                    title="Shaded Garden Location",
                    explanation=(
                        f"This garden is classified as '{garden_exposure_category}' "
                        "based on seasonal shadow analysis. Shaded locations receive "
                        "less than 40% direct sunlight during peak seasons. "
                        "This significantly limits photosynthesis and plant productivity."
                    ),
                    suggested_action=(
                        "Consider shade-tolerant plants (leafy greens, herbs like parsley, "
                        "mint, cilantro). Avoid sun-demanding crops like tomatoes, peppers, "
                        "or squash, which require 6+ hours of direct sun for good yields."
                    ),
                    affected_gardens=[garden_id]
                ))
            return rules

        # Compare exposure to requirements
        exposure_lower = garden_exposure_category.lower()
        requirement_lower = plant_sun_requirement.lower()

        # Rule: Full sun plant in shade
        if "full" in requirement_lower and exposure_lower == "shade":
            rules.append(SunExposureRule(
                rule_id="SUN_002",
                severity=RuleSeverity.CRITICAL,
                title="Full Sun Plant in Shade",
                explanation=(
                    "This location is heavily shaded but full-sun plants require 6+ hours "
                    "of direct sunlight for photosynthesis and fruit production. "
                    "Shaded conditions will severely reduce growth rate, delay fruiting, "
                    "and decrease yields. Plants may become leggy (stretching toward light) "
                    "and more susceptible to fungal diseases in low-light, high-moisture conditions."
                ),
                suggested_action=(
                    "CRITICAL: Relocate to a sunnier location with minimal seasonal shading, "
                    "or replace with shade-tolerant plants. Full-sun crops (tomatoes, peppers, "
                    "cucumbers, squash) will not thrive in this location."
                ),
                affected_gardens=[garden_id]
            ))

        # Rule: Full sun plant in partial sun
        elif "full" in requirement_lower and "partial" in exposure_lower:
            rules.append(SunExposureRule(
                rule_id="SUN_003",
                severity=RuleSeverity.WARNING,
                title="Reduced Sun for Full-Sun Plant",
                explanation=(
                    "This location provides partial sun (40-75% exposure) but full-sun plants "
                    "perform best with 6+ hours of direct sunlight. Reduced light levels "
                    "will slow growth, delay fruit maturity, and reduce overall yields. "
                    "Expect 20-40% yield reduction compared to optimal sun exposure."
                ),
                suggested_action=(
                    "Consider relocating to a sunnier spot if possible. If this location is "
                    "necessary, monitor plants closely and be prepared for slower growth and "
                    "lower productivity. Alternatively, choose partial-sun tolerant varieties."
                ),
                affected_gardens=[garden_id]
            ))

        # Rule: Shade plant in full sun
        elif "shade" in requirement_lower and exposure_lower == "full sun":
            rules.append(SunExposureRule(
                rule_id="SUN_004",
                severity=RuleSeverity.WARNING,
                title="Shade Plant in Full Sun",
                explanation=(
                    "This location receives full sun (75%+ exposure) but shade-adapted plants "
                    "can experience stress from intense light and heat. Symptoms may include "
                    "leaf burn (brown, crispy edges), wilting during midday, bleached foliage, "
                    "and increased water requirements."
                ),
                suggested_action=(
                    "Provide afternoon shade or use shade cloth (30-50% density) during peak "
                    "summer months. Alternatively, relocate to a naturally shaded area or "
                    "choose sun-tolerant plant varieties."
                ),
                affected_gardens=[garden_id]
            ))

        return rules

    @staticmethod
    def evaluate_seasonal_shading_pattern(
        seasonal_shading: Dict[str, dict],
        garden_id: int
    ) -> List[SunExposureRule]:
        """
        Evaluate seasonal shading patterns for potential issues.

        Science basis: Seasonal variation in sun exposure affects
        planting timing and crop selection.

        Args:
            seasonal_shading: Dict mapping season to shading info
            garden_id: Garden ID

        Returns:
            List of triggered rules
        """
        rules = []

        # Extract shading percentages by season
        winter_shading = seasonal_shading.get("winter", {}).get("shaded_percentage", 0)
        equinox_shading = seasonal_shading.get("equinox", {}).get("shaded_percentage", 0)
        summer_shading = seasonal_shading.get("summer", {}).get("shaded_percentage", 0)

        # Rule: High winter shading
        if winter_shading > 75:
            rules.append(SunExposureRule(
                rule_id="SUN_005",
                severity=RuleSeverity.INFO,
                title="Heavy Winter Shading",
                explanation=(
                    f"This garden receives significant shading during winter ({winter_shading:.0f}% shaded). "
                    "Low winter sun angles combined with tall objects (trees, structures) create "
                    "longer shadows. This limits winter growing potential in mild climates."
                ),
                suggested_action=(
                    "In regions with mild winters, this location is better suited for dormant season "
                    "or spring/summer crops. For winter growing, consider cold-hardy shade-tolerant "
                    "greens (kale, spinach, mâche) if attempting winter production."
                ),
                affected_gardens=[garden_id]
            ))

        # Rule: Summer shading advantage
        if summer_shading > 30 and summer_shading < 60:
            rules.append(SunExposureRule(
                rule_id="SUN_006",
                severity=RuleSeverity.INFO,
                title="Beneficial Summer Shading",
                explanation=(
                    f"This garden receives partial shade during summer ({summer_shading:.0f}% shaded). "
                    "In hot climates, afternoon shade can reduce heat stress and extend the growing "
                    "season for cool-season crops (lettuce, spinach, cilantro) that bolt in full sun."
                ),
                suggested_action=(
                    "Take advantage of summer shading by planting heat-sensitive crops that benefit "
                    "from cooler conditions. This location is ideal for extending spring crop seasons "
                    "into early summer."
                ),
                affected_gardens=[garden_id]
            ))

        # Rule: Inconsistent seasonal exposure
        shading_range = max(winter_shading, equinox_shading, summer_shading) - \
                       min(winter_shading, equinox_shading, summer_shading)

        if shading_range > 50:
            rules.append(SunExposureRule(
                rule_id="SUN_007",
                severity=RuleSeverity.WARNING,
                title="High Seasonal Variability",
                explanation=(
                    f"Sun exposure varies significantly across seasons (range: {shading_range:.0f}%). "
                    "Winter: {winter_shading:.0f}% shaded, "
                    f"Equinox: {equinox_shading:.0f}% shaded, "
                    f"Summer: {summer_shading:.0f}% shaded. "
                    "High variability requires seasonal crop planning adjustments."
                ),
                suggested_action=(
                    "Plan crop rotation based on seasonal sun availability. Plant sun-demanding crops "
                    "during seasons with best exposure, and shade-tolerant crops during heavily shaded "
                    "seasons. Monitor plant performance and adjust timing accordingly."
                ),
                affected_gardens=[garden_id]
            ))

        return rules

    @staticmethod
    def evaluate_garden_sun_exposure(
        garden_exposure_data: Dict[str, Any],
        plant_sun_requirement: Optional[str] = None
    ) -> List[SunExposureRule]:
        """
        Comprehensive evaluation of garden sun exposure.

        Args:
            garden_exposure_data: Output from SunExposureService.get_garden_sun_exposure()
            plant_sun_requirement: Optional plant sun requirement

        Returns:
            List of all triggered rules
        """
        rules = []

        # Extract data
        garden_id = garden_exposure_data.get("garden_id", 0)
        exposure_category = garden_exposure_data.get("exposure_category")
        seasonal_shading = garden_exposure_data.get("seasonal_shading", {})

        if not exposure_category or not seasonal_shading:
            return rules

        # Evaluate exposure match
        rules.extend(
            SunExposureRuleEngine.evaluate_exposure_category_match(
                garden_exposure_category=exposure_category,
                plant_sun_requirement=plant_sun_requirement,
                garden_id=garden_id,
                seasonal_shading=seasonal_shading
            )
        )

        # Evaluate seasonal patterns
        rules.extend(
            SunExposureRuleEngine.evaluate_seasonal_shading_pattern(
                seasonal_shading=seasonal_shading,
                garden_id=garden_id
            )
        )

        return rules

    @staticmethod
    def evaluate_tree_placement(
        tree_x: float,
        tree_y: float,
        nearby_gardens: List[Dict[str, Any]],
        tree_id: int,
        hemisphere: str
    ) -> List[SunExposureRule]:
        """
        Evaluate tree placement relative to nearby gardens.

        Science basis: Trees cast shadows in predictable directions.
        In Northern Hemisphere, trees to the south cast shadows northward.

        Args:
            tree_x: Tree x-coordinate
            tree_y: Tree y-coordinate
            nearby_gardens: List of gardens with x, y coordinates
            tree_id: Tree ID
            hemisphere: "northern" or "southern"

        Returns:
            List of triggered rules
        """
        rules = []

        if not nearby_gardens:
            return rules

        # Determine problematic direction based on hemisphere
        if hemisphere == "northern":
            # Trees to the south (lower Y) cast shadows northward
            problematic_position = "south"
            check_func = lambda g: tree_y < g['y']  # Tree has lower Y than garden
        else:
            # Trees to the north (higher Y) cast shadows southward
            problematic_position = "north"
            check_func = lambda g: tree_y > g['y']  # Tree has higher Y than garden

        affected_gardens = []
        for garden in nearby_gardens:
            if check_func(garden):
                # Tree is in problematic position relative to this garden
                affected_gardens.append(garden['id'])

        if affected_gardens:
            rules.append(SunExposureRule(
                rule_id="SUN_008",
                severity=RuleSeverity.WARNING,
                title=f"Tree Positioned {problematic_position.title()} of Garden(s)",
                explanation=(
                    f"This tree is located {problematic_position} of {len(affected_gardens)} garden(s). "
                    f"In the {hemisphere} hemisphere, this positioning will cast shadows onto these gardens, "
                    "reducing their sun exposure. As the tree grows taller, shadow impact will increase. "
                    "Shadow length increases significantly during winter months when sun angle is lowest."
                ),
                suggested_action=(
                    f"Consider relocating tree to the {opposite_direction(problematic_position)} side of gardens "
                    "to minimize shading impact. If relocation is not possible, choose shade-tolerant plants "
                    "for affected gardens or select dwarf/compact tree varieties to limit shadow extent."
                ),
                affected_gardens=affected_gardens,
                affected_trees=[tree_id]
            ))

        return rules


def opposite_direction(direction: str) -> str:
    """Helper to get opposite cardinal direction"""
    opposites = {
        "north": "south",
        "south": "north",
        "east": "west",
        "west": "east"
    }
    return opposites.get(direction, direction)
