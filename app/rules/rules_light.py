"""
Light Stress Rules - Light quantity and quality assessment.

Rules detect:
- Insufficient light (etiolation)
- Excessive light (photoinhibition)
- Photoperiod mismatch

Scientific basis:
- Light drives photosynthesis (quantum yield)
- Photoinhibition damages photosystem II at high intensity
- Photoperiod controls flowering in many species
"""

from typing import List, Optional
from .engine.base import Rule, RuleContext, RuleResult, RuleSeverity, RuleCategory


# Light requirements by plant (hours of bright light per day)
LIGHT_REQUIREMENTS = {
    "tomato": {"min": 8, "optimal": 12, "photoperiod": "day-neutral"},
    "lettuce": {"min": 6, "optimal": 10, "photoperiod": "long-day"},
    "pepper": {"min": 8, "optimal": 12, "photoperiod": "day-neutral"},
    "cucumber": {"min": 8, "optimal": 12, "photoperiod": "day-neutral"},
    "broccoli": {"min": 6, "optimal": 10, "photoperiod": "long-day"},
    "spinach": {"min": 6, "optimal": 10, "photoperiod": "long-day"},
    "basil": {"min": 6, "optimal": 10, "photoperiod": "day-neutral"},
    "strawberry": {"min": 6, "optimal": 10, "photoperiod": "short-day"},  # Flowers in short days
    "default": {"min": 6, "optimal": 10, "photoperiod": "day-neutral"}
}


class EtiolationRiskRule(Rule):
    """
    LIGHT_001: Detects insufficient light causing etiolation.

    Scientific rationale:
    - Insufficient light triggers shade avoidance syndrome
    - Auxin accumulation on shaded side causes stem elongation
    - Chlorophyll synthesis reduced (pale, yellowed leaves)
    - Weak, spindly growth with long internodes
    """

    def get_rule_id(self) -> str:
        return "LIGHT_001"

    def get_category(self) -> RuleCategory:
        return RuleCategory.LIGHT_STRESS

    def get_title(self) -> str:
        return "Insufficient Light (Etiolation Risk)"

    def get_description(self) -> str:
        return "Light levels are below optimal, risking weak, spindly growth"

    def is_applicable(self, context: RuleContext) -> bool:
        return context.light_hours_per_day is not None

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        light_hours = context.light_hours_per_day

        # Get plant requirements
        plant_key = context.plant_common_name.lower().split()[0] if context.plant_common_name else "default"
        requirements = LIGHT_REQUIREMENTS.get(plant_key, LIGHT_REQUIREMENTS["default"])

        min_light = requirements["min"]
        optimal_light = requirements["optimal"]

        if light_hours < min_light * 0.5:  # Severely deficient
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.CRITICAL,
                confidence=0.90,
                explanation=f"Light is critically low at {light_hours:.1f} hours/day. {context.plant_common_name or 'This plant'} needs at least {min_light} hours for healthy growth.",
                scientific_rationale="At <50% of minimum light requirement, photosynthesis cannot support maintenance respiration. Plants enter etiolation (shade avoidance): Stems elongate rapidly searching for light, leaves remain small and pale, internodes stretch. Auxin redistribution promotes upward growth at expense of lateral development. Plant becomes weak and leggy.",
                recommended_action=f"Increase light immediately. For indoor plants: Move closer to window, add grow lights (provide {min_light}-{optimal_light} hours). For outdoor: Relocate to sunnier spot, prune shade-causing branches. Weak etiolated stems may not recover - consider replanting with better light.",
                measured_value=light_hours,
                optimal_range=f"{optimal_light}+ hours/day",
                deviation_severity="severe",
                references=[
                    "Franklin, K.A. (2008). Shade avoidance. New Phytologist, 179(4), 930-944.",
                    "Ballaré, C.L. & Pierik, R. (2017). The shade-avoidance syndrome. Current Opinion in Plant Biology, 37, 1-7."
                ]
            )

        elif light_hours < min_light:  # Moderately deficient
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.WARNING,
                confidence=0.85,
                explanation=f"Light is low at {light_hours:.1f} hours/day. Optimal is {optimal_light}+ hours for robust growth.",
                scientific_rationale="Below minimum light, photosynthetic rate limits growth. Carbon fixation is insufficient for optimal biomass accumulation. Plants may grow but will be weaker, with reduced yields. Fruit production particularly suffers.",
                recommended_action=f"Increase light exposure. For indoor: Add supplemental grow lights (LED or fluorescent). For outdoor: Relocate or remove shade sources. Target {optimal_light}+ hours of bright light daily.",
                measured_value=light_hours,
                optimal_range=f"{optimal_light}+ hours/day",
                deviation_severity="moderate",
                references=["Franklin, K.A. (2008). Shade avoidance"]
            )

        elif light_hours < optimal_light:  # Suboptimal
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title="Suboptimal Light Levels",
                triggered=True,
                severity=RuleSeverity.INFO,
                confidence=0.75,
                explanation=f"Light is adequate ({light_hours:.1f} hrs/day) but below optimal ({optimal_light}+ hrs) for maximum growth.",
                scientific_rationale="Light is sufficient to prevent etiolation but not optimal for maximum photosynthetic capacity. Growth rate and yields will be reduced compared to optimal light conditions.",
                recommended_action=f"For best results, increase to {optimal_light}+ hours of bright light. Not critical but growth will be slower than optimal.",
                measured_value=light_hours,
                optimal_range=f"{optimal_light}+ hours/day",
                deviation_severity="slight",
                references=["Taiz, L. & Zeiger, E. (2010). Plant Physiology"]
            )

        return None


class PhotoinhibitionRule(Rule):
    """
    LIGHT_002: Detects excessive light causing photoinhibition.

    Scientific rationale:
    - Excess light energy damages photosystem II
    - Reactive oxygen species (ROS) accumulate
    - Photoprotective mechanisms (xanthophyll cycle) become overwhelmed
    - Bleached, scorched leaves
    """

    def get_rule_id(self) -> str:
        return "LIGHT_002"

    def get_category(self) -> RuleCategory:
        return RuleCategory.LIGHT_STRESS

    def get_title(self) -> str:
        return "Excessive Light (Photoinhibition Risk)"

    def get_description(self) -> str:
        return "Light levels may be too high, risking leaf damage"

    def is_applicable(self, context: RuleContext) -> bool:
        # Only applicable for indoor/artificial light where we can control intensity
        return (context.is_indoor and
                context.light_hours_per_day is not None and
                context.light_source_type in ["led", "fluorescent"])

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        light_hours = context.light_hours_per_day

        # For most plants under artificial light, >16 hours risks photoinhibition
        # and can disrupt circadian rhythms
        if light_hours > 18:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.WARNING,
                confidence=0.75,
                explanation=f"Artificial light is on for {light_hours:.1f} hours/day. This may cause photoinhibition and disrupt plant circadian rhythms.",
                scientific_rationale="Continuous or near-continuous light prevents daily recovery from photoinhibition. Photosystem II repair mechanisms require dark periods. Prolonged light increases reactive oxygen species (ROS), damaging chloroplasts. Circadian clock disruption affects flowering and metabolism.",
                recommended_action="Reduce light duration to 12-16 hours per day. Plants need dark periods for repair and metabolic processes (starch breakdown, protein synthesis). Use timer to ensure consistent day/night cycle. If plants show bleached/pale patches, reduce light intensity or distance.",
                measured_value=light_hours,
                optimal_range="12-16 hours/day for most plants",
                deviation_severity="moderate",
                references=[
                    "Takahashi, S. & Badger, M.R. (2011). Photoprotection in plants. The Plant Cell, 23(5), 1674-1684.",
                    "Murata, N. et al. (2007). Photoinhibition of photosystem II under environmental stress. Biochimica et Biophysica Acta, 1767(6), 414-421."
                ]
            )

        return None


def get_light_rules() -> List[Rule]:
    """Return all light stress rules."""
    return [
        EtiolationRiskRule(),
        PhotoinhibitionRule(),
    ]
