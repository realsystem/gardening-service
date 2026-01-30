"""
Growth Stage Rules - Growth timing and harvest readiness.

Rules detect:
- Harvest window timing
- Growth stage transitions
- Nutrient timing issues

Scientific basis:
- Plant development follows predictable phenological stages
- Days to maturity vary by variety and temperature
- Optimal harvest timing affects quality and yield
"""

from typing import List, Optional
from .engine.base import Rule, RuleContext, RuleResult, RuleSeverity, RuleCategory


class HarvestReadinessRule(Rule):
    """
    GROWTH_001: Detects when plant is approaching harvest window.

    Scientific rationale:
    - Each crop has optimal harvest timing for quality/yield
    - Days to harvest varies by variety and growing conditions
    - Temperature affects development rate (growing degree days)
    """

    def get_rule_id(self) -> str:
        return "GROWTH_001"

    def get_category(self) -> RuleCategory:
        return RuleCategory.GROWTH_STAGE

    def get_title(self) -> str:
        return "Harvest Window Approaching"

    def get_description(self) -> str:
        return "Plant is approaching harvest maturity"

    def is_applicable(self, context: RuleContext) -> bool:
        return context.days_since_planting is not None

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        days_since_planting = context.days_since_planting

        # Typical days to harvest for common crops
        days_to_harvest = {
            "tomato": 75, "lettuce": 50, "cucumber": 60, "pepper": 75,
            "broccoli": 70, "carrot": 75, "spinach": 45, "basil": 60
        }

        plant_key = context.plant_common_name.lower().split()[0] if context.plant_common_name else None
        expected_days = days_to_harvest.get(plant_key, 70)  # Default 70 days

        days_until_harvest = expected_days - days_since_planting

        if -7 <= days_until_harvest <= 7:  # Within harvest window
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.INFO,
                confidence=0.80,
                explanation=f"{context.plant_common_name or 'Plant'} planted {days_since_planting} days ago is at expected harvest maturity (typically {expected_days} days).",
                scientific_rationale="Harvest timing affects quality, flavor, and storage life. Vegetables harvested at peak maturity have optimal sugar content, texture, and nutrient density. Over-mature produce develops off-flavors, toughness, or bolting.",
                recommended_action=f"Monitor for harvest readiness signs. For {context.plant_common_name or 'this crop'}, check size, color, and firmness. Harvest in morning after dew dries for best quality. Note that actual days to harvest vary with temperature and variety.",
                measured_value=float(days_since_planting),
                optimal_range=f"~{expected_days} days",
                references=[
                    "Cantwell, M. & Kasmire, R.F. (2002). Postharvest handling systems: Fresh-cut fruits and vegetables. University of California Agriculture and Natural Resources.",
                    "Kader, A.A. (2002). Postharvest Technology of Horticultural Crops, 3rd ed. UC ANR."
                ]
            )

        return None


def get_growth_rules() -> List[Rule]:
    """Return all growth stage rules."""
    return [
        HarvestReadinessRule(),
    ]
