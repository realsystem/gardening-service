"""
Temperature Stress Rules - Heat and cold stress detection.

Rules detect:
- Cold shock / frost damage risk
- Heat stress / heat shock
- Suboptimal temperature ranges

Scientific basis:
- Enzyme activity is temperature-dependent
- Membranes become rigid when cold, fluid when hot
- Protein denaturation occurs at extreme temperatures
"""

from typing import List, Optional
from .engine.base import Rule, RuleContext, RuleResult, RuleSeverity, RuleCategory


# Plant-specific temperature tolerances (Fahrenheit)
TEMP_REQUIREMENTS = {
    "tomato": {"min": 50, "optimal_min": 65, "optimal_max": 85, "max": 95},
    "lettuce": {"min": 35, "optimal_min": 60, "optimal_max": 70, "max": 75},
    "pepper": {"min": 55, "optimal_min": 70, "optimal_max": 85, "max": 95},
    "cucumber": {"min": 50, "optimal_min": 70, "optimal_max": 85, "max": 95},
    "broccoli": {"min": 40, "optimal_min": 60, "optimal_max": 70, "max": 75},
    "spinach": {"min": 35, "optimal_min": 50, "optimal_max": 65, "max": 70},
    "basil": {"min": 50, "optimal_min": 70, "optimal_max": 90, "max": 100},
    "default": {"min": 45, "optimal_min": 65, "optimal_max": 80, "max": 90}
}


class ColdStressRule(Rule):
    """
    TEMP_001: Detects cold stress and chilling injury risk.

    Scientific rationale:
    - Below species-specific threshold, membrane lipids crystallize
    - Enzyme activity decreases exponentially with temperature
    - Ice crystal formation in cells causes mechanical damage
    - Chilling injury (non-freezing cold damage) in warm-season crops
    """

    def get_rule_id(self) -> str:
        return "TEMP_001"

    def get_category(self) -> RuleCategory:
        return RuleCategory.TEMPERATURE_STRESS

    def get_title(self) -> str:
        return "Cold Stress / Frost Risk"

    def get_description(self) -> str:
        return "Temperature is below optimal range, risking cold damage"

    def is_applicable(self, context: RuleContext) -> bool:
        return (context.temperature_f is not None or
                context.temperature_min_f is not None or
                context.frost_risk_next_7d)

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        # Get plant requirements
        plant_key = context.plant_common_name.lower().split()[0] if context.plant_common_name else "default"
        requirements = TEMP_REQUIREMENTS.get(plant_key, TEMP_REQUIREMENTS["default"])

        min_temp = requirements["min"]
        optimal_min = requirements["optimal_min"]

        # Check for frost risk (highest priority)
        if context.frost_risk_next_7d and not context.is_indoor:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title="Frost Risk Warning",
                triggered=True,
                severity=RuleSeverity.CRITICAL,
                confidence=0.95,
                explanation=f"Frost predicted in next 7 days. {context.plant_common_name or 'This plant'} is at risk of freeze damage.",
                scientific_rationale="Frost causes ice crystal formation in plant cells, rupturing cell membranes. Damage is irreversible. Warm-season crops (tomatoes, peppers, cucumbers) are killed by even light frost (32°F). Cool-season crops tolerate light frost but are damaged by hard freeze (<28°F).",
                recommended_action="Protect plants immediately: Cover with row covers, sheets, or cloches. Water soil before frost (moist soil holds more heat). Move containers indoors. Harvest any ripe fruit. For young transplants, bring indoors if possible.",
                optimal_range=f"Above {min_temp}°F",
                deviation_severity="severe",
                references=[
                    "Levitt, J. (1980). Responses of Plants to Environmental Stresses, Vol I: Chilling, Freezing, and High Temperature Stresses.",
                    "Thomashow, M.F. (1999). Plant cold acclimation: Freezing tolerance genes. Annual Review of Plant Physiology, 50, 571-599."
                ]
            )

        # Check minimum temperature
        temp_to_check = context.temperature_min_f if context.temperature_min_f is not None else context.temperature_f

        if temp_to_check is not None:
            if temp_to_check < min_temp:
                temp_deficit = min_temp - temp_to_check
                severity = RuleSeverity.CRITICAL if temp_deficit > 10 else RuleSeverity.WARNING

                return RuleResult(
                    rule_id=self.rule_id,
                    rule_category=self.category,
                    title=self.title,
                    triggered=True,
                    severity=severity,
                    confidence=0.90,
                    explanation=f"Temperature is {temp_to_check:.0f}°F, which is {temp_deficit:.0f}°F below minimum for {context.plant_common_name or 'this plant'}.",
                    scientific_rationale="Below minimum temperature, chilling injury occurs. Membrane phase transition causes lipid peroxidation. Enzyme activity drops exponentially (Q10 effect). Photosynthesis is impaired. For warm-season crops, temps below 50°F cause permanent damage.",
                    recommended_action="Increase temperature if possible (move indoors, add row covers, use heat mats). For indoor plants, move away from cold windows. Reduce watering as cold plants transpire less. Monitor for wilting and discoloration.",
                    measured_value=temp_to_check,
                    optimal_range=f"{optimal_min}-{requirements['optimal_max']}°F",
                    deviation_severity="severe" if temp_deficit > 10 else "moderate",
                    references=["Levitt, J. (1980). Responses of Plants to Environmental Stresses"]
                )

            elif temp_to_check < optimal_min:
                return RuleResult(
                    rule_id=self.rule_id,
                    rule_category=self.category,
                    title="Suboptimal Temperature (Cold)",
                    triggered=True,
                    severity=RuleSeverity.INFO,
                    confidence=0.75,
                    explanation=f"Temperature is {temp_to_check:.0f}°F, below optimal range of {optimal_min}-{requirements['optimal_max']}°F.",
                    scientific_rationale="Below optimal temperature, metabolic rates slow. Growth is reduced. Nutrient uptake decreases. Plants are not damaged but growth is suboptimal.",
                    recommended_action="Consider protection if outdoor (cloches, row covers). For indoor plants, ensure temperature stays above {optimal_min}°F for best growth.",
                    measured_value=temp_to_check,
                    optimal_range=f"{optimal_min}-{requirements['optimal_max']}°F",
                    deviation_severity="slight",
                    references=["Taiz, L. & Zeiger, E. (2010). Plant Physiology"]
                )

        return None


class HeatStressRule(Rule):
    """
    TEMP_002: Detects heat stress conditions.

    Scientific rationale:
    - High temperatures denature proteins (heat shock proteins activated)
    - Photosystem II is damaged above species-specific threshold
    - Respiration exceeds photosynthesis (negative carbon balance)
    - Flower/fruit abortion in many species
    """

    def get_rule_id(self) -> str:
        return "TEMP_002"

    def get_category(self) -> RuleCategory:
        return RuleCategory.TEMPERATURE_STRESS

    def get_title(self) -> str:
        return "Heat Stress"

    def get_description(self) -> str:
        return "Temperature is above optimal range, causing heat stress"

    def is_applicable(self, context: RuleContext) -> bool:
        return (context.temperature_f is not None or
                context.temperature_max_f is not None)

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        # Get plant requirements
        plant_key = context.plant_common_name.lower().split()[0] if context.plant_common_name else "default"
        requirements = TEMP_REQUIREMENTS.get(plant_key, TEMP_REQUIREMENTS["default"])

        optimal_max = requirements["optimal_max"]
        max_temp = requirements["max"]

        # Check maximum temperature
        temp_to_check = context.temperature_max_f if context.temperature_max_f is not None else context.temperature_f

        if temp_to_check is not None:
            if temp_to_check > max_temp:
                temp_excess = temp_to_check - max_temp
                return RuleResult(
                    rule_id=self.rule_id,
                    rule_category=self.category,
                    title=self.title,
                    triggered=True,
                    severity=RuleSeverity.CRITICAL,
                    confidence=0.90,
                    explanation=f"Temperature is critically high at {temp_to_check:.0f}°F, exceeding maximum for {context.plant_common_name or 'this plant'} by {temp_excess:.0f}°F.",
                    scientific_rationale="Above {max_temp}°F, protein denaturation occurs. Photosystem II is damaged (photoinhibition). Respiration exceeds photosynthesis, causing negative carbon balance. Flower drop, fruit abortion, and leaf scorch occur. Prolonged exposure can be lethal.",
                    recommended_action="Provide shade immediately (shade cloth 30-50%). Increase watering frequency (evaporative cooling). Mist foliage in morning. For indoor plants, improve air circulation and move away from hot windows. Avoid fertilizing during heat stress.",
                    measured_value=temp_to_check,
                    optimal_range=f"{requirements['optimal_min']}-{optimal_max}°F",
                    deviation_severity="severe",
                    references=[
                        "Wahid, A. et al. (2007). Heat tolerance in plants. Environmental and Experimental Botany, 61(3), 199-223.",
                        "Hasanuzzaman, M. et al. (2013). Physiological, biochemical, and molecular mechanisms of heat stress tolerance in plants. International Journal of Molecular Sciences, 14(5), 9643-9684."
                    ]
                )

            elif temp_to_check > optimal_max:
                return RuleResult(
                    rule_id=self.rule_id,
                    rule_category=self.category,
                    title=self.title,
                    triggered=True,
                    severity=RuleSeverity.WARNING,
                    confidence=0.85,
                    explanation=f"Temperature is {temp_to_check:.0f}°F, above optimal range.",
                    scientific_rationale="Above optimal temperature, respiration increases faster than photosynthesis. Net carbon gain decreases. Heat shock proteins are induced, diverting energy from growth. Pollination may fail in fruiting crops.",
                    recommended_action="Provide shade if possible. Increase watering to compensate for increased transpiration. Mulch to keep roots cool. Avoid transplanting or pruning during heat. For tomatoes/peppers, expect reduced fruit set.",
                    measured_value=temp_to_check,
                    optimal_range=f"{requirements['optimal_min']}-{optimal_max}°F",
                    deviation_severity="moderate",
                    references=["Wahid, A. et al. (2007). Heat tolerance in plants"]
                )

        return None


def get_temperature_rules() -> List[Rule]:
    """Return all temperature stress rules."""
    return [
        ColdStressRule(),
        HeatStressRule(),
    ]
