"""
Soil Chemistry Rules - pH, nutrients, and salinity management.

Rules detect:
- pH imbalances affecting nutrient availability
- Nutrient deficiencies/toxicities
- Salinity stress

Scientific basis:
- pH controls nutrient solubility and microbial activity
- Nutrient availability follows the Mulder's chart relationships
- Salinity reduces water potential, creating osmotic stress
"""

from typing import List, Optional
from .engine.base import Rule, RuleContext, RuleResult, RuleSeverity, RuleCategory


# Plant-specific pH requirements
PH_REQUIREMENTS = {
    "tomato": {"min": 6.0, "max": 6.8},
    "lettuce": {"min": 6.0, "max": 7.0},
    "blueberry": {"min": 4.5, "max": 5.5},  # Acid-loving
    "carrot": {"min": 5.5, "max": 7.0},
    "pepper": {"min": 6.0, "max": 7.0},
    "broccoli": {"min": 6.0, "max": 7.5},
    "potato": {"min": 5.0, "max": 6.0},  # Slightly acidic
    "spinach": {"min": 6.5, "max": 7.5},
    "basil": {"min": 6.0, "max": 7.5},
    "default": {"min": 6.0, "max": 7.0}
}


class PHImbalanceRule(Rule):
    """
    SOIL_001: Detects pH outside optimal range.

    Scientific rationale:
    - pH controls nutrient solubility in soil solution
    - At pH <5.5: Iron, aluminum, manganese become toxic
    - At pH >7.5: Phosphorus, iron, zinc become unavailable (lockout)
    - Microbial activity peaks at pH 6.0-7.5
    """

    def get_rule_id(self) -> str:
        return "SOIL_001"

    def get_category(self) -> RuleCategory:
        return RuleCategory.SOIL_CHEMISTRY

    def get_title(self) -> str:
        return "Soil pH Imbalance"

    def get_description(self) -> str:
        return "Soil pH is outside optimal range, affecting nutrient availability"

    def is_applicable(self, context: RuleContext) -> bool:
        return context.soil_ph is not None

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        if context.soil_ph is None:
            return None

        # Get plant requirements
        plant_key = context.plant_common_name.lower().split()[0] if context.plant_common_name else "default"
        requirements = PH_REQUIREMENTS.get(plant_key, PH_REQUIREMENTS["default"])

        ph_min = requirements["min"]
        ph_max = requirements["max"]
        ph = context.soil_ph

        # Check for severe acidic conditions
        if ph < ph_min - 1.0:
            lime_needed = (ph_min - ph) * 5  # ~5 lbs lime per pH unit per 100 sq ft
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.CRITICAL,
                confidence=0.95,
                explanation=f"Soil pH is severely acidic at {ph:.1f}. This is {ph_min - ph:.1f} pH units below optimal for {context.plant_common_name or 'this plant'}.",
                scientific_rationale="At pH below 5.5, aluminum and manganese become soluble and toxic to roots. Iron toxicity can also occur. Beneficial bacteria (Rhizobium, nitrifiers) become inactive. Phosphorus binds with iron/aluminum, becoming unavailable.",
                recommended_action=f"Apply approximately {lime_needed:.1f} lbs of dolomitic lime per 100 sq ft. Work into top 6 inches of soil. Lime takes 2-3 months to react, so apply in fall for spring planting. Test again in 6-8 weeks.",
                measured_value=ph,
                optimal_range=f"{ph_min:.1f} - {ph_max:.1f}",
                deviation_severity="severe",
                references=[
                    "Brady, N.C. & Weil, R.R. (2016). The Nature and Properties of Soils, 15th ed.",
                    "Hue, N.V. & Licudine, D.L. (1999). Amelioration of subsoil acidity. Plant and Soil, 215(2), 197-206."
                ]
            )

        # Check for moderate acidic conditions
        elif ph < ph_min:
            lime_needed = (ph_min - ph) * 5
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.WARNING,
                confidence=0.90,
                explanation=f"Soil pH is slightly acidic at {ph:.1f}. Optimal range for {context.plant_common_name or 'this plant'} is {ph_min:.1f}-{ph_max:.1f}.",
                scientific_rationale="Below optimal pH, nutrient availability decreases. Calcium and magnesium become less available. Beneficial bacterial activity slows. Plant growth is suboptimal.",
                recommended_action=f"Add {lime_needed:.1f} lbs of garden lime per 100 sq ft. Wood ash (2-3 lbs per 100 sq ft) is also effective for small pH adjustments. Mix into topsoil.",
                measured_value=ph,
                optimal_range=f"{ph_min:.1f} - {ph_max:.1f}",
                deviation_severity="moderate",
                references=["Brady, N.C. & Weil, R.R. (2016). The Nature and Properties of Soils"]
            )

        # Check for severe alkaline conditions
        elif ph > ph_max + 1.0:
            sulfur_needed = (ph - ph_max) * 1.5  # ~1.5 lbs sulfur per pH unit per 100 sq ft
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.CRITICAL,
                confidence=0.95,
                explanation=f"Soil pH is severely alkaline at {ph:.1f}. This is {ph - ph_max:.1f} pH units above optimal.",
                scientific_rationale="At pH above 7.5, phosphorus precipitates with calcium (calcium phosphate), becoming unavailable. Iron, zinc, manganese, copper become insoluble, causing deficiencies (iron chlorosis is common). Boron toxicity can occur.",
                recommended_action=f"Add {sulfur_needed:.1f} lbs of elemental sulfur per 100 sq ft to lower pH. Alternatively, use sulfate-based fertilizers or add 3-4 inches of peat moss. Sulfur acts slowly (3-6 months), plan accordingly.",
                measured_value=ph,
                optimal_range=f"{ph_min:.1f} - {ph_max:.1f}",
                deviation_severity="severe",
                references=[
                    "Mengel, K. & Kirkby, E.A. (2001). Principles of Plant Nutrition, 5th ed.",
                    "Lindsay, W.L. (1979). Chemical Equilibria in Soils. Wiley."
                ]
            )

        # Check for moderate alkaline conditions
        elif ph > ph_max:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.WARNING,
                confidence=0.85,
                explanation=f"Soil pH is slightly alkaline at {ph:.1f}. Optimal range is {ph_min:.1f}-{ph_max:.1f}.",
                scientific_rationale="Above optimal pH, iron and phosphorus availability decreases. Micronutrient deficiencies (iron chlorosis) become more likely. Nitrogen mineralization slows.",
                recommended_action="Add sulfur (1-2 lbs per 100 sq ft) or organic matter (compost, peat moss). Coffee grounds and pine needles also acidify soil gradually. Monitor for yellowing between leaf veins (iron deficiency).",
                measured_value=ph,
                optimal_range=f"{ph_min:.1f} - {ph_max:.1f}",
                deviation_severity="moderate",
                references=["Mengel, K. & Kirkby, E.A. (2001). Principles of Plant Nutrition"]
            )

        # pH is optimal - no alert
        return None


class NitrogenDeficiencyRule(Rule):
    """
    SOIL_002: Detects nitrogen deficiency.

    Scientific rationale:
    - Nitrogen is component of chlorophyll, proteins, nucleic acids
    - Deficiency causes chlorosis (yellowing), starting with older leaves
    - Mobile nutrient - remobilized from old to new growth
    - Critical during vegetative growth phase
    """

    def get_rule_id(self) -> str:
        return "SOIL_002"

    def get_category(self) -> RuleCategory:
        return RuleCategory.SOIL_CHEMISTRY

    def get_title(self) -> str:
        return "Nitrogen Deficiency"

    def get_description(self) -> str:
        return "Soil nitrogen levels are below optimal range"

    def is_applicable(self, context: RuleContext) -> bool:
        return context.nitrogen_ppm is not None

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        n_ppm = context.nitrogen_ppm
        optimal_min = 20  # Conservative threshold for most vegetables

        if n_ppm < 10:  # Severely deficient
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.CRITICAL,
                confidence=0.90,
                explanation=f"Nitrogen is severely deficient at {n_ppm:.0f} ppm. Plants will show stunted growth and yellowing.",
                scientific_rationale="Nitrogen is essential for chlorophyll synthesis and protein formation. At <10 ppm, photosynthesis is limited by chlorophyll deficiency. Stunted growth, pale yellow leaves (especially older leaves), reduced yields. Plants cannot produce adequate amino acids for growth.",
                recommended_action="Apply nitrogen-rich amendment immediately: blood meal (12-0-0) at 3 lbs per 100 sq ft, or fish emulsion (5-1-1) as foliar spray every 2 weeks. Add 3-4 inches of aged compost for long-term nitrogen supply.",
                measured_value=n_ppm,
                optimal_range="20-60 ppm",
                deviation_severity="severe",
                references=[
                    "Marschner, H. (2011). Marschner's Mineral Nutrition of Higher Plants, 3rd ed.",
                    "Epstein, E. & Bloom, A.J. (2005). Mineral Nutrition of Plants. Sinauer."
                ]
            )

        elif n_ppm < optimal_min:  # Moderately deficient
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.WARNING,
                confidence=0.85,
                explanation=f"Nitrogen is low at {n_ppm:.0f} ppm. Growth may be suboptimal.",
                scientific_rationale="Below 20 ppm, nitrogen becomes limiting for optimal growth. Chlorophyll production is reduced, decreasing photosynthetic efficiency by 15-30%.",
                recommended_action="Add compost (2-3 inches) or apply alfalfa meal (3-0-2) at 2 lbs per 100 sq ft. Plant nitrogen-fixing cover crops (clover, peas) between seasons. Side-dress with compost during growing season.",
                measured_value=n_ppm,
                optimal_range="20-60 ppm",
                deviation_severity="moderate",
                references=["Marschner, H. (2011). Mineral Nutrition of Higher Plants"]
            )

        return None


class SalinityStressRule(Rule):
    """
    SOIL_003: Detects high soil salinity (salt stress).

    Scientific rationale:
    - High salinity reduces soil water potential (osmotic potential)
    - Plants expend energy to accumulate osmoprotectants
    - Salt ions (Na+, Cl-) can be toxic at high concentrations
    - Reduces water uptake even when soil moisture is adequate
    """

    def get_rule_id(self) -> str:
        return "SOIL_003"

    def get_category(self) -> RuleCategory:
        return RuleCategory.SOIL_CHEMISTRY

    def get_title(self) -> str:
        return "Soil Salinity Stress"

    def get_description(self) -> str:
        return "Elevated salt levels may be affecting water uptake"

    def is_applicable(self, context: RuleContext) -> bool:
        return context.soil_salinity_ec is not None

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        ec = context.soil_salinity_ec  # Electrical conductivity in dS/m

        # Most vegetables are sensitive to salinity
        # EC > 2.0 dS/m begins to reduce yields
        # EC > 4.0 dS/m severely limits growth

        if ec > 4.0:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.CRITICAL,
                confidence=0.90,
                explanation=f"Soil salinity is critically high at {ec:.1f} dS/m. Most vegetables will not grow well.",
                scientific_rationale="At EC >4 dS/m, osmotic potential is so negative that roots cannot extract water efficiently even when soil is moist. Plants wilt despite adequate moisture. Salt ions (especially Na+) disrupt cell membranes and enzyme function. Yields reduced by 50-100%.",
                recommended_action="Leach salts with deep irrigation (4-6 inches of water). Improve drainage to allow salt movement below root zone. Add gypsum (calcium sulfate) to displace sodium. Consider growing salt-tolerant crops (beets, asparagus) until salinity decreases. Test again after leaching.",
                measured_value=ec,
                optimal_range="< 2.0 dS/m",
                deviation_severity="severe",
                references=[
                    "Taiz, L. & Zeiger, E. (2010). Plant Physiology, 5th ed.",
                    "Munns, R. & Tester, M. (2008). Mechanisms of salinity tolerance. Annual Review of Plant Biology, 59, 651-681."
                ]
            )

        elif ec > 2.0:
            yield_reduction = (ec - 2.0) * 12.5  # Approximate 12.5% per unit EC above 2.0
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.WARNING,
                confidence=0.85,
                explanation=f"Soil salinity is elevated at {ec:.1f} dS/m. Yield may be reduced by ~{yield_reduction:.0f}%.",
                scientific_rationale="At EC 2-4 dS/m, osmotic stress begins to limit water uptake. Plants must expend energy accumulating compatible solutes (proline, glycine betaine) to maintain turgor, reducing energy for growth.",
                recommended_action="Increase irrigation to leach salts below root zone. Ensure good drainage. Avoid high-salt fertilizers. Use organic matter to improve soil structure and salt tolerance.",
                measured_value=ec,
                optimal_range="< 2.0 dS/m",
                deviation_severity="moderate",
                references=["Munns, R. & Tester, M. (2008). Mechanisms of salinity tolerance"]
            )

        return None


def get_soil_rules() -> List[Rule]:
    """Return all soil chemistry rules."""
    return [
        PHImbalanceRule(),
        NitrogenDeficiencyRule(),
        SalinityStressRule(),
    ]
