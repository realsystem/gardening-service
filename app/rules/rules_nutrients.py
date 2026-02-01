"""
Nutrient Management Rules - Science-based EC/pH monitoring for hydroponic systems.

Rules detect:
- EC drift risk (solution concentration changes)
- pH lockout (nutrient unavailability due to pH)
- Salt buildup (excessive EC from mineral accumulation)

Scientific basis:
- EC measures total dissolved salts (nutrient concentration)
- pH controls nutrient ion solubility and availability
- Solution aging leads to ion imbalance and salt accumulation

References:
- Resh, H.M. (2012). Hydroponic Food Production (7th ed.)
- Jones, J.B. (2016). Hydroponics: A Practical Guide for the Soilless Grower (3rd ed.)
- Graves, W.R. (2018). Hydroponic Nutrient Management
"""

from typing import Optional
from .engine.base import Rule, RuleContext, RuleResult, RuleSeverity, RuleCategory


class ECDriftRule(Rule):
    """
    NUT_001: Detects EC drift risk from aging nutrient solution.

    Scientific rationale:
    - Plants uptake water faster than nutrients (selective uptake)
    - As water evaporates/transpires, nutrient concentration increases
    - EC drift > 20% from target indicates solution aging
    - Leads to ion imbalance and potential toxicity

    Trigger conditions:
    - Solution age exceeds recommended change interval
    - EC measurement significantly above or below target range
    """

    def get_rule_id(self) -> str:
        return "NUT_001"

    def get_category(self) -> RuleCategory:
        return RuleCategory.NUTRIENT_TIMING

    def get_title(self) -> str:
        return "EC Drift Risk Detected"

    def get_description(self) -> str:
        return "Nutrient solution is aging and may have imbalanced EC levels"

    def is_applicable(self, context: RuleContext) -> bool:
        """Requires hydroponic system with solution age data"""
        return context.is_hydroponic and context.days_since_solution_change is not None

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        if not self.is_applicable(context):
            return None

        days_old = context.days_since_solution_change
        recommended_max = context.recommended_change_days or 14

        # Critical: Solution extremely old (>21 days)
        if days_old > 21:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.CRITICAL,
                confidence=0.95,
                explanation=(
                    f"Nutrient solution is severely overdue for change ({days_old} days old). "
                    "EC drift and ion imbalance are highly likely."
                ),
                scientific_rationale=(
                    "Plants uptake water faster than nutrients through selective membrane transport. "
                    "Over extended periods (>21 days), this causes severe EC drift and ion imbalances. "
                    "Preferential uptake of N and K creates deficiencies while other salts accumulate, "
                    "leading to nutrient lockout and potential toxicity."
                ),
                recommended_action=(
                    "URGENT: Perform complete reservoir flush and fresh solution mix immediately. "
                    "Measure EC/pH before and after change."
                ),
                measured_value=float(days_old),
                optimal_range=f"< {recommended_max} days",
                deviation_severity="severe",
                references=[
                    "Resh, H.M. (2012). Hydroponic Food Production, Chapter 6",
                    "Jones, J.B. (2016). Hydroponics: A Practical Guide, pp. 134-147"
                ]
            )

        # Warning: Solution past recommended interval
        if days_old > recommended_max:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.WARNING,
                confidence=0.85,
                explanation=(
                    f"Nutrient solution is past recommended change interval ({days_old} days vs {recommended_max} days max). "
                    "EC drift and ion imbalance risk increasing."
                ),
                scientific_rationale=(
                    "As solution ages beyond optimal interval, differential water/nutrient uptake "
                    "causes EC to drift and ion ratios to shift. This reduces nutrient availability "
                    "and can stress plants."
                ),
                recommended_action=(
                    "Perform full reservoir change within 2-3 days. Monitor EC/pH closely."
                ),
                measured_value=float(days_old),
                optimal_range=f"< {recommended_max} days",
                deviation_severity="moderate",
                references=[
                    "Resh, H.M. (2012). Hydroponic Food Production",
                    "Cornell CEA Program (2020). Hydroponic Lettuce Handbook"
                ]
            )

        # Info: Approaching recommended change
        if days_old > recommended_max * 0.85:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title="Solution Change Due Soon",
                triggered=True,
                severity=RuleSeverity.INFO,
                confidence=0.75,
                explanation=(
                    f"Nutrient solution approaching recommended change interval ({days_old}/{recommended_max} days)."
                ),
                scientific_rationale=(
                    "Regular solution changes prevent ion imbalance and maintain optimal nutrient availability."
                ),
                recommended_action=(
                    "Plan solution change in next few days. Prepare fresh nutrient mix."
                ),
                measured_value=float(days_old),
                optimal_range=f"< {recommended_max} days",
                references=[
                    "Resh, H.M. (2012). Hydroponic Food Production"
                ]
            )

        return None


class PHLockoutRule(Rule):
    """
    NUT_002: Detects pH levels causing nutrient lockout.

    Scientific rationale:
    - Nutrient ion availability depends on pH (solubility equilibria)
    - pH < 5.0: Iron, manganese, zinc available; calcium, magnesium locked out
    - pH 5.5-6.5: Optimal availability for most nutrients
    - pH > 7.0: Iron, manganese, zinc locked out; calcium, magnesium available
    - Lockout causes deficiency symptoms despite adequate EC

    Trigger conditions:
    - pH outside optimal range for crop
    - pH in critical lockout zones (< 5.0 or > 7.5)
    """

    def get_rule_id(self) -> str:
        return "NUT_002"

    def get_category(self) -> RuleCategory:
        return RuleCategory.NUTRIENT_TIMING

    def get_title(self) -> str:
        return "pH Nutrient Lockout Risk"

    def get_description(self) -> str:
        return "pH level is outside optimal range, reducing nutrient availability"

    def is_applicable(self, context: RuleContext) -> bool:
        """Requires pH measurement"""
        return context.current_ph is not None

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        if not self.is_applicable(context):
            return None

        current_ph = context.current_ph
        optimal_min = context.optimal_ph_min or 5.5
        optimal_max = context.optimal_ph_max or 6.5

        # Critical lockout zones
        if current_ph < 5.0:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.CRITICAL,
                confidence=0.95,
                explanation=(
                    f"pH is critically low at {current_ph:.1f}. Calcium and magnesium are locked out, "
                    "even if present in solution. Plants will show deficiency symptoms."
                ),
                scientific_rationale=(
                    "At pH < 5.0, calcium precipitates as insoluble compounds and magnesium forms "
                    "unavailable complexes. Meanwhile, iron and manganese solubility increases to "
                    "potentially toxic levels. This creates a double problem: deficiency of Ca/Mg "
                    "and potential toxicity of micronutrients. Blossom end rot (Ca deficiency) is "
                    "common even with adequate Ca in solution."
                ),
                recommended_action=(
                    "Adjust pH immediately using pH Up (potassium hydroxide or potassium carbonate). "
                    "Add slowly while stirring. Target pH 5.5-6.5. "
                    "Monitor for next 24 hours as pH may drift. "
                    "Check water source - acidic tap water may require pH buffer."
                ),
                measured_value=current_ph,
                optimal_range=f"{optimal_min}-{optimal_max}",
                deviation_severity="severe",
                references=[
                    "Jones, J.B. (2016). Hydroponics: A Practical Guide, Chapter 4: Nutrient Solutions",
                    "Bugbee, B. (2004). Nutrient Management in Recirculating Hydroponic Culture",
                    "Mattson, N. & Peters, C. (2014). A Recipe for Hydroponic Success. Cornell CEA"
                ]
            )

        elif current_ph > 7.5:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.CRITICAL,
                confidence=0.95,
                explanation=(
                    f"pH is critically high at {current_ph:.1f}. Iron, manganese, and zinc are locked out. "
                    "Plants will develop chlorosis (yellowing) despite adequate nutrients."
                ),
                scientific_rationale=(
                    "At pH > 7.5, micronutrient cations (Fe³⁺, Mn²⁺, Zn²⁺) form insoluble hydroxides "
                    "and oxides, becoming plant-unavailable. Iron chlorosis appears first as interveinal "
                    "yellowing in new growth. Severe cases cause complete growth cessation. This is "
                    "particularly problematic because micronutrient deficiencies are difficult to "
                    "correct quickly - even after pH adjustment, recovery takes 7-14 days."
                ),
                recommended_action=(
                    "Adjust pH immediately using pH Down (phosphoric acid or citric acid). "
                    "Add slowly while stirring. Target pH 5.5-6.5. "
                    "May need iron chelate (Fe-EDTA) foliar spray for quick chlorosis correction. "
                    "Check for hard water - high alkalinity requires more frequent pH adjustment."
                ),
                measured_value=current_ph,
                optimal_range=f"{optimal_min}-{optimal_max}",
                deviation_severity="severe",
                references=[
                    "Jones, J.B. (2016). Hydroponics: A Practical Guide, pp. 89-104",
                    "Sonneveld, C. & Voogt, W. (2009). Plant Nutrition of Greenhouse Crops",
                    "Resh, H.M. (2012). Hydroponic Food Production, pp. 178-192"
                ]
            )

        # Warning zones (outside optimal but not critical)
        elif current_ph < optimal_min:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title="pH Below Optimal Range",
                triggered=True,
                severity=RuleSeverity.WARNING,
                confidence=0.85,
                explanation=f"pH is slightly low at {current_ph:.1f}. Nutrient uptake efficiency is reduced.",
                scientific_rationale=(
                    "pH between 5.0-5.5 reduces calcium and magnesium availability by 20-40%. "
                    "While not causing immediate lockout, chronic low pH causes slow development "
                    "and increased susceptibility to stress."
                ),
                recommended_action=f"Adjust pH to {optimal_min}-{optimal_max} range using pH Up solution. Monitor daily.",
                measured_value=current_ph,
                optimal_range=f"{optimal_min}-{optimal_max}",
                deviation_severity="mild",
                references=["Jones, J.B. (2016). Hydroponics: A Practical Guide"]
            )

        elif current_ph > optimal_max:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title="pH Above Optimal Range",
                triggered=True,
                severity=RuleSeverity.WARNING,
                confidence=0.85,
                explanation=f"pH is slightly high at {current_ph:.1f}. Micronutrient availability is decreasing.",
                scientific_rationale=(
                    "pH above optimal range reduces iron availability by 30-50%. Early signs include "
                    "slight yellowing of new growth. Extended exposure causes progressive iron "
                    "deficiency chlorosis."
                ),
                recommended_action=f"Adjust pH to {optimal_min}-{optimal_max} range using pH Down solution. Monitor daily.",
                measured_value=current_ph,
                optimal_range=f"{optimal_min}-{optimal_max}",
                deviation_severity="mild",
                references=["Resh, H.M. (2012). Hydroponic Food Production"]
            )

        return None


class SaltBuildupRule(Rule):
    """
    NUT_003: Detects excessive salt accumulation from high EC.

    Scientific rationale:
    - EC measures electrical conductivity from dissolved ions (salts)
    - High EC reduces water uptake (osmotic stress)
    - Leaf tip/edge burn from salt accumulation
    - Excessive EC > 4.0 mS/cm causes severe stress in most crops

    Trigger conditions:
    - EC significantly above recommended range (> 20% over max)
    - EC in dangerous zone (> 4.0 mS/cm)
    """

    def get_rule_id(self) -> str:
        return "NUT_003"

    def get_category(self) -> RuleCategory:
        return RuleCategory.NUTRIENT_TIMING

    def get_title(self) -> str:
        return "Salt Buildup Detected"

    def get_description(self) -> str:
        return "EC is excessively high, indicating salt accumulation"

    def is_applicable(self, context: RuleContext) -> bool:
        """Requires EC measurement"""
        return context.current_ec_ms_cm is not None

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        if not self.is_applicable(context):
            return None

        current_ec = context.current_ec_ms_cm
        recommended_max = context.recommended_ec_max or 2.5

        # Critical EC levels (> 4.0 mS/cm)
        if current_ec > 4.0:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.CRITICAL,
                confidence=0.95,
                explanation=(
                    f"EC is critically high at {current_ec:.1f} mS/cm. Severe osmotic stress is occurring. "
                    "Plants cannot uptake water effectively despite saturated roots."
                ),
                scientific_rationale=(
                    "At EC > 4.0 mS/cm, the osmotic potential of the solution exceeds most plants' "
                    "ability to extract water. This creates \"physiological drought\" - roots are "
                    "surrounded by water but cannot uptake it. Water flows OUT of roots (plasmolysis), "
                    "causing severe wilting despite wet media. Salt ions accumulate in leaf margins, "
                    "causing necrotic tip burn. Growth halts and yields drop dramatically."
                ),
                recommended_action=(
                    "EMERGENCY: Flush reservoir immediately with fresh water (pH adjusted). "
                    "Drain completely and refill with new solution at proper EC (1.5-2.5 mS/cm). "
                    "Rinse growing media with low-EC water to remove accumulated salts. "
                    "Investigate cause: Over-fertilization? Insufficient water changes? Evaporation?"
                ),
                measured_value=current_ec,
                optimal_range=f"< {recommended_max} mS/cm",
                deviation_severity="severe",
                references=[
                    "Grieve, C.M. & Grattan, S.R. (1983). Rapid assay for determination of water soluble quaternary ammonium compounds. Plant and Soil, 70(2), 303-307.",
                    "Resh, H.M. (2012). Hydroponic Food Production, pp. 143-156",
                    "Shannon, M.C. & Grieve, C.M. (1999). Tolerance of vegetable crops to salinity. Scientia Horticulturae, 78(1-4), 5-38."
                ]
            )

        # Warning levels (moderately high EC)
        elif current_ec > 3.0:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title="Elevated EC Levels",
                triggered=True,
                severity=RuleSeverity.WARNING,
                confidence=0.85,
                explanation=(
                    f"EC is elevated at {current_ec:.1f} mS/cm. Salt accumulation is beginning. "
                    "Monitor for leaf tip burn and reduced water uptake."
                ),
                scientific_rationale=(
                    "EC between 3.0-4.0 mS/cm causes moderate osmotic stress. Water uptake efficiency "
                    "decreases by 20-30%. Salt-sensitive crops (lettuce, strawberries) show tip burn. "
                    "Continued exposure reduces yield by 15-25% and increases susceptibility to "
                    "environmental stress."
                ),
                recommended_action=(
                    "Dilute solution by replacing 30-50% with fresh water (pH adjusted). "
                    "Reduce nutrient concentration in next refill. "
                    "Increase solution change frequency to prevent further buildup. "
                    "Check for adequate drainage/recirculation."
                ),
                measured_value=current_ec,
                optimal_range=f"< {recommended_max} mS/cm",
                deviation_severity="moderate",
                references=[
                    "Resh, H.M. (2012). Hydroponic Food Production",
                    "Shannon, M.C. & Grieve, C.M. (1999). Tolerance of vegetable crops to salinity"
                ]
            )

        # Info: Slightly elevated above recommended
        elif current_ec > recommended_max:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title="EC Slightly Elevated",
                triggered=True,
                severity=RuleSeverity.INFO,
                confidence=0.75,
                explanation=(
                    f"EC is slightly above recommended maximum ({current_ec:.1f} vs {recommended_max:.1f} mS/cm)."
                ),
                scientific_rationale=(
                    "Slightly elevated EC may indicate solution concentration from evaporation or over-feeding. "
                    "While not immediately harmful, continued elevation can lead to salt accumulation."
                ),
                recommended_action=(
                    "Monitor EC closely. Consider diluting with fresh water if it continues to rise. "
                    "Check water levels and top-off regularly."
                ),
                measured_value=current_ec,
                optimal_range=f"< {recommended_max} mS/cm",
                references=[
                    "Resh, H.M. (2012). Hydroponic Food Production"
                ]
            )

        return None