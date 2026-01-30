"""
Water Stress Rules - Scientifically-grounded watering recommendations.

Rules detect:
- Under-watering (root water stress)
- Over-watering (root oxygen deprivation)
- Irrigation frequency issues

Scientific basis:
- Transpiration rates vary by growth stage
- Root zone oxygen is critical for nutrient uptake
- Water stress timing affects yield significantly
"""

from typing import List, Optional
from .engine.base import Rule, RuleContext, RuleResult, RuleSeverity, RuleCategory


# Plant-specific water requirements (days between watering)
WATER_REQUIREMENTS = {
    "tomato": {"min_days": 2, "max_days": 4, "critical_stages": ["flowering", "fruiting"]},
    "lettuce": {"min_days": 1, "max_days": 3, "critical_stages": ["all"]},
    "cucumber": {"min_days": 1, "max_days": 3, "critical_stages": ["flowering", "fruiting"]},
    "pepper": {"min_days": 2, "max_days": 4, "critical_stages": ["flowering", "fruiting"]},
    "broccoli": {"min_days": 2, "max_days": 4, "critical_stages": ["head_formation"]},
    "carrot": {"min_days": 3, "max_days": 5, "critical_stages": ["root_development"]},
    "spinach": {"min_days": 2, "max_days": 4, "critical_stages": ["all"]},
    "basil": {"min_days": 1, "max_days": 3, "critical_stages": ["all"]},
    "default": {"min_days": 2, "max_days": 4, "critical_stages": ["flowering", "fruiting"]}
}


class UnderWateringRule(Rule):
    """
    WATER_001: Detects under-watering conditions.

    Scientific rationale:
    - Plants lose water through transpiration (stomatal conductance)
    - Insufficient soil moisture closes stomata, reducing CO2 uptake
    - Photosynthesis efficiency drops, affecting growth and yield
    - Critical during flowering/fruiting when water stress reduces fruit set
    """

    def get_rule_id(self) -> str:
        return "WATER_001"

    def get_category(self) -> RuleCategory:
        return RuleCategory.WATER_STRESS

    def get_title(self) -> str:
        return "Under-watering Detected"

    def get_description(self) -> str:
        return "Plant is showing signs of water stress based on irrigation frequency or soil moisture"

    def is_applicable(self, context: RuleContext) -> bool:
        """Requires either irrigation history or soil moisture data."""
        return (context.days_since_last_watering is not None or
                context.soil_moisture_percent is not None)

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        # Get plant requirements
        plant_key = context.plant_common_name.lower().split()[0] if context.plant_common_name else "default"
        requirements = WATER_REQUIREMENTS.get(plant_key, WATER_REQUIREMENTS["default"])

        # Check soil moisture first (most direct indicator)
        if context.soil_moisture_percent is not None:
            if context.soil_moisture_percent < 15:
                return RuleResult(
                    rule_id=self.rule_id,
                    rule_category=self.category,
                    title=self.title,
                    triggered=True,
                    severity=RuleSeverity.CRITICAL,
                    confidence=0.95,
                    explanation=f"Soil moisture is critically low at {context.soil_moisture_percent:.1f}%. Plants are experiencing severe water stress.",
                    scientific_rationale="At moisture levels below 15%, most plants cannot extract sufficient water from soil. Stomatal closure reduces photosynthesis by 40-60%, and prolonged stress causes permanent wilting point.",
                    recommended_action=f"Water immediately with 1-2 inches of water. For {context.plant_common_name or 'this plant'}, water deeply to encourage root growth. Apply mulch to retain moisture.",
                    measured_value=context.soil_moisture_percent,
                    optimal_range="20-60% (field capacity)",
                    deviation_severity="severe",
                    references=[
                        "Jones, H.G. (2004). Irrigation scheduling: advantages and pitfalls of plant-based methods. Journal of Experimental Botany, 55(407), 2427-2436.",
                        "Boyer, J.S. (1982). Plant productivity and environment. Science, 218(4571), 443-448."
                    ]
                )
            elif context.soil_moisture_percent < 20:
                return RuleResult(
                    rule_id=self.rule_id,
                    rule_category=self.category,
                    title=self.title,
                    triggered=True,
                    severity=RuleSeverity.WARNING,
                    confidence=0.85,
                    explanation=f"Soil moisture is low at {context.soil_moisture_percent:.1f}%. Plant may be approaching water stress.",
                    scientific_rationale="As soil moisture drops below 20%, soil water potential decreases logarithmically, making water extraction increasingly difficult for roots.",
                    recommended_action=f"Increase watering frequency. For {context.plant_common_name or 'this plant'}, water within the next 24 hours.",
                    measured_value=context.soil_moisture_percent,
                    optimal_range="20-60%",
                    deviation_severity="moderate",
                    references=["Jones, H.G. (2004). Irrigation scheduling"]
                )

        # Check irrigation frequency
        if context.days_since_last_watering is not None:
            max_days = requirements["max_days"]
            days_overdue = context.days_since_last_watering - max_days

            if days_overdue > 2:
                # Critically overdue
                severity = RuleSeverity.CRITICAL
                confidence = 0.90
                explanation = f"Last watered {context.days_since_last_watering} days ago. Severely overdue for {context.plant_common_name or 'this plant'} (recommended every {max_days} days)."
                rationale = f"Extended water stress ({days_overdue} days overdue) causes irreversible cellular damage. Turgor pressure loss affects cell expansion, permanently limiting growth. During {context.growth_stage or 'critical'} stages, this can reduce yields by 30-50%."
                deviation = "severe"
            elif days_overdue > 0:
                # Moderately overdue
                severity = RuleSeverity.WARNING
                confidence = 0.80
                explanation = f"Last watered {context.days_since_last_watering} days ago. Overdue for watering (recommended every {max_days} days)."
                rationale = "Water stress reduces stomatal conductance, limiting CO2 uptake for photosynthesis. Even mild stress can reduce growth rates by 20%."
                deviation = "moderate"
            else:
                # Not triggered
                return None

            if days_overdue > 0:
                return RuleResult(
                    rule_id=self.rule_id,
                    rule_category=self.category,
                    title=self.title,
                    triggered=True,
                    severity=severity,
                    confidence=confidence,
                    explanation=explanation,
                    scientific_rationale=rationale,
                    recommended_action=f"Water immediately. Apply water slowly to allow soil infiltration. For established plants, water deeply (6-8 inches) to encourage root growth.",
                    measured_value=float(context.days_since_last_watering),
                    optimal_range=f"Every {requirements['min_days']}-{requirements['max_days']} days",
                    deviation_severity=deviation,
                    references=["Boyer, J.S. (1982). Plant productivity and environment"]
                )

        return None


class OverWateringRule(Rule):
    """
    WATER_002: Detects over-watering and root oxygen deprivation.

    Scientific rationale:
    - Roots require oxygen for aerobic respiration
    - Waterlogged soil fills air pockets, creating anaerobic conditions
    - Root cells die within 24-48 hours without oxygen
    - Anaerobic bacteria produce toxic compounds (ethylene, methane)
    """

    def get_rule_id(self) -> str:
        return "WATER_002"

    def get_category(self) -> RuleCategory:
        return RuleCategory.WATER_STRESS

    def get_title(self) -> str:
        return "Over-watering / Root Oxygen Stress"

    def get_description(self) -> str:
        return "Excessive soil moisture may be limiting root oxygen availability"

    def is_applicable(self, context: RuleContext) -> bool:
        return (context.soil_moisture_percent is not None or
                context.days_since_last_watering is not None)

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        # Check soil moisture (most direct)
        if context.soil_moisture_percent is not None:
            if context.soil_moisture_percent > 70:
                return RuleResult(
                    rule_id=self.rule_id,
                    rule_category=self.category,
                    title=self.title,
                    triggered=True,
                    severity=RuleSeverity.CRITICAL,
                    confidence=0.90,
                    explanation=f"Soil moisture is critically high at {context.soil_moisture_percent:.1f}%. Root zone is likely waterlogged, limiting oxygen availability.",
                    scientific_rationale="At >70% moisture, soil macropores are water-saturated, blocking oxygen diffusion to roots. Root respiration shifts to anaerobic pathways, producing toxic byproducts (ethanol, acetaldehyde). Root cells die within 24-48 hours without oxygen.",
                    recommended_action="Stop all irrigation immediately. Improve drainage by adding organic matter or creating raised beds. Monitor for yellowing leaves (chlorosis) and wilting despite wet soil - signs of root rot.",
                    measured_value=context.soil_moisture_percent,
                    optimal_range="20-60%",
                    deviation_severity="severe",
                    references=[
                        "Drew, M.C. (1997). Oxygen deficiency and root metabolism. Annual Review of Plant Physiology, 48, 223-250.",
                        "Voesenek, L.A. & Bailey-Serres, J. (2015). Flood adaptive traits and processes. New Phytologist, 206(1), 57-73."
                    ]
                )
            elif context.soil_moisture_percent > 60:
                return RuleResult(
                    rule_id=self.rule_id,
                    rule_category=self.category,
                    title=self.title,
                    triggered=True,
                    severity=RuleSeverity.WARNING,
                    confidence=0.75,
                    explanation=f"Soil moisture is high at {context.soil_moisture_percent:.1f}%. Risk of reduced oxygen availability to roots.",
                    scientific_rationale="Moisture above 60% begins to restrict oxygen diffusion through soil. Root respiration efficiency decreases, limiting nutrient uptake.",
                    recommended_action="Reduce watering frequency. Ensure good drainage. Allow soil to dry to 40-50% before next watering.",
                    measured_value=context.soil_moisture_percent,
                    optimal_range="20-60%",
                    deviation_severity="moderate",
                    references=["Drew, M.C. (1997). Oxygen deficiency and root metabolism"]
                )

        # Check irrigation frequency
        if context.days_since_last_watering is not None and context.plant_common_name:
            plant_key = context.plant_common_name.lower().split()[0]
            requirements = WATER_REQUIREMENTS.get(plant_key, WATER_REQUIREMENTS["default"])
            min_days = requirements["min_days"]

            if context.days_since_last_watering < min_days and context.days_since_last_watering >= 0:
                days_too_soon = min_days - context.days_since_last_watering
                return RuleResult(
                    rule_id=self.rule_id,
                    rule_category=self.category,
                    title=self.title,
                    triggered=True,
                    severity=RuleSeverity.WARNING,
                    confidence=0.70,
                    explanation=f"Watering too frequently. Last watered only {context.days_since_last_watering} days ago (recommended minimum {min_days} days between watering).",
                    scientific_rationale="Frequent shallow watering prevents roots from growing deep, creating drought-vulnerable plants. Constant moisture encourages fungal diseases and nutrient leaching.",
                    recommended_action=f"Wait {min_days - context.days_since_last_watering} more days before next watering. Water deeply but infrequently to encourage deep root development.",
                    measured_value=float(context.days_since_last_watering),
                    optimal_range=f"Every {min_days}-{requirements['max_days']} days",
                    deviation_severity="moderate",
                    references=["Taiz, L. & Zeiger, E. (2010). Plant Physiology, 5th ed. Sinauer Associates."]
                )

        return None


class IrrigationFrequencyRule(Rule):
    """
    WATER_003: Excessive irrigation events can indicate over-watering pattern.

    Scientific rationale:
    - Multiple daily waterings prevent soil aeration cycles
    - Shallow frequent watering encourages shallow root systems
    - Reduces plant drought tolerance
    """

    def get_rule_id(self) -> str:
        return "WATER_003"

    def get_category(self) -> RuleCategory:
        return RuleCategory.WATER_STRESS

    def get_title(self) -> str:
        return "Excessive Irrigation Frequency"

    def get_description(self) -> str:
        return "Too many irrigation events may indicate over-watering pattern"

    def is_applicable(self, context: RuleContext) -> bool:
        return context.total_irrigation_events_7d is not None

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        events_7d = context.total_irrigation_events_7d

        # More than once per day on average is excessive for most plants
        if events_7d > 10:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.WARNING,
                confidence=0.80,
                explanation=f"{events_7d} irrigation events in the last 7 days is excessive. This pattern may lead to shallow root development.",
                scientific_rationale="Frequent shallow watering trains roots to stay near the surface, reducing drought tolerance. Roots grow where water is available - shallow frequent watering creates shallow root systems vulnerable to stress.",
                recommended_action="Switch to deep, infrequent watering. Water 1-2 times per week with 1-2 inches of water rather than daily shallow watering. Allow top 2 inches of soil to dry between watering.",
                measured_value=float(events_7d),
                optimal_range="2-4 events per week",
                deviation_severity="moderate",
                references=[
                    "Bassuk, N. et al. (2009). Recommended Urban Trees: Site Assessment and Tree Selection. Cornell University."
                ]
            )

        return None


def get_water_rules() -> List[Rule]:
    """Return all water stress rules."""
    return [
        UnderWateringRule(),
        OverWateringRule(),
        IrrigationFrequencyRule(),
    ]
