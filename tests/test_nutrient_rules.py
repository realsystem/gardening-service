"""Tests for Nutrient Management Rules (ECDrift, PHLockout, SaltBuildup)"""
import pytest
from app.rules.engine.base import RuleContext, RuleSeverity
from app.rules.rules_nutrients import ECDriftRule, PHLockoutRule, SaltBuildupRule


@pytest.mark.nutrient_optimization
class TestECDriftRule:
    """Test NUT_001: EC Drift Detection (aging nutrient solution)"""

    def test_critical_old_solution(self):
        """Test critical severity when solution is >21 days old"""
        rule = ECDriftRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Tomato",
            days_since_solution_change=25,
            recommended_change_days=14,
            current_ec_ms_cm=2.5
        )

        result = rule.evaluate(context)

        assert result is not None
        assert result.triggered is True
        assert result.severity == RuleSeverity.CRITICAL
        assert result.confidence >= 0.90
        assert "overdue" in result.explanation.lower() or "old" in result.explanation.lower()
        assert "change" in result.recommended_action.lower()
        assert len(result.references) > 0
        assert "NUT_001" in result.rule_id

    def test_warning_solution_aging(self):
        """Test warning severity when solution exceeds recommended interval"""
        rule = ECDriftRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Lettuce",
            days_since_solution_change=16,
            recommended_change_days=14,
            current_ec_ms_cm=1.2
        )

        result = rule.evaluate(context)

        assert result is not None
        assert result.triggered is True
        assert result.severity == RuleSeverity.WARNING
        assert result.confidence >= 0.85
        assert "change" in result.recommended_action.lower()

    def test_no_trigger_fresh_solution(self):
        """Test no trigger when solution is within recommended interval"""
        rule = ECDriftRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Tomato",
            days_since_solution_change=7,
            recommended_change_days=14,
            current_ec_ms_cm=2.0
        )

        result = rule.evaluate(context)

        assert result is None

    def test_not_applicable_without_data(self):
        """Test rule is not applicable without required data"""
        rule = ECDriftRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Tomato",
            days_since_solution_change=None
        )

        assert rule.is_applicable(context) is False

    def test_info_level_for_moderate_age(self):
        """Test info severity for solution approaching recommended change"""
        rule = ECDriftRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Basil",
            days_since_solution_change=12,
            recommended_change_days=14,
            current_ec_ms_cm=1.5
        )

        result = rule.evaluate(context)

        assert result is not None
        assert result.triggered is True
        assert result.severity == RuleSeverity.INFO
        assert "soon" in result.explanation.lower() or "approaching" in result.explanation.lower()


@pytest.mark.nutrient_optimization
class TestPHLockoutRule:
    """Test NUT_002: pH Lockout Detection (nutrient unavailability)"""

    def test_critical_ph_very_low(self):
        """Test critical severity when pH < 5.0 (severe lockout)"""
        rule = PHLockoutRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Tomato",
            current_ph=4.5,
            optimal_ph_min=5.5,
            optimal_ph_max=6.5
        )

        result = rule.evaluate(context)

        assert result is not None
        assert result.triggered is True
        assert result.severity == RuleSeverity.CRITICAL
        assert result.confidence >= 0.95
        assert "locked out" in result.explanation.lower() or "unavailable" in result.explanation.lower()
        assert "ph up" in result.recommended_action.lower() or "increase" in result.recommended_action.lower()
        assert len(result.references) > 0
        assert "NUT_002" in result.rule_id

    def test_critical_ph_very_high(self):
        """Test critical severity when pH > 7.5 (severe lockout)"""
        rule = PHLockoutRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Lettuce",
            current_ph=8.0,
            optimal_ph_min=5.5,
            optimal_ph_max=6.5
        )

        result = rule.evaluate(context)

        assert result is not None
        assert result.triggered is True
        assert result.severity == RuleSeverity.CRITICAL
        assert result.confidence >= 0.95
        assert "locked out" in result.explanation.lower()
        assert "ph down" in result.recommended_action.lower() or "decrease" in result.recommended_action.lower()

    def test_warning_ph_slightly_low(self):
        """Test warning severity when pH is below optimal but > 5.0"""
        rule = PHLockoutRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Basil",
            current_ph=5.2,
            optimal_ph_min=5.5,
            optimal_ph_max=6.5
        )

        result = rule.evaluate(context)

        assert result is not None
        assert result.triggered is True
        assert result.severity == RuleSeverity.WARNING
        assert result.confidence >= 0.80
        assert "below" in result.explanation.lower() or "low" in result.explanation.lower()

    def test_warning_ph_slightly_high(self):
        """Test warning severity when pH is above optimal but < 7.5"""
        rule = PHLockoutRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Cucumber",
            current_ph=7.0,
            optimal_ph_min=5.5,
            optimal_ph_max=6.5
        )

        result = rule.evaluate(context)

        assert result is not None
        assert result.triggered is True
        assert result.severity == RuleSeverity.WARNING
        assert "above" in result.explanation.lower() or "high" in result.explanation.lower()

    def test_no_trigger_optimal_ph(self):
        """Test no trigger when pH is within optimal range"""
        rule = PHLockoutRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Tomato",
            current_ph=6.0,
            optimal_ph_min=5.5,
            optimal_ph_max=6.5
        )

        result = rule.evaluate(context)

        assert result is None

    def test_not_applicable_without_data(self):
        """Test rule is not applicable without pH data"""
        rule = PHLockoutRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Tomato",
            current_ph=None
        )

        assert rule.is_applicable(context) is False

    def test_measured_value_in_result(self):
        """Test that measured pH value appears in result"""
        rule = PHLockoutRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Pepper",
            current_ph=4.8,
            optimal_ph_min=5.8,
            optimal_ph_max=6.3
        )

        result = rule.evaluate(context)

        assert result is not None
        assert result.measured_value == 4.8
        assert result.optimal_range == "5.8-6.3"


@pytest.mark.nutrient_optimization
class TestSaltBuildupRule:
    """Test NUT_003: Salt Buildup Detection (excessive EC)"""

    def test_critical_extreme_ec(self):
        """Test critical severity when EC > 4.0 mS/cm (severe salt stress)"""
        rule = SaltBuildupRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Lettuce",
            current_ec_ms_cm=4.5,
            recommended_ec_max=1.2
        )

        result = rule.evaluate(context)

        assert result is not None
        assert result.triggered is True
        assert result.severity == RuleSeverity.CRITICAL
        assert result.confidence >= 0.95
        assert "osmotic" in result.explanation.lower() or "stress" in result.explanation.lower() or "critically high" in result.explanation.lower()
        assert "flush" in result.recommended_action.lower() or "replace" in result.recommended_action.lower()
        assert len(result.references) > 0
        assert "NUT_003" in result.rule_id

    def test_warning_high_ec(self):
        """Test warning severity when EC > 3.0 mS/cm"""
        rule = SaltBuildupRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Tomato",
            current_ec_ms_cm=3.2,
            recommended_ec_max=2.5
        )

        result = rule.evaluate(context)

        assert result is not None
        assert result.triggered is True
        assert result.severity == RuleSeverity.WARNING
        assert result.confidence >= 0.85
        assert "high" in result.explanation.lower() or "elevated" in result.explanation.lower()

    def test_info_slightly_elevated_ec(self):
        """Test info severity when EC is slightly above recommended max"""
        rule = SaltBuildupRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Basil",
            current_ec_ms_cm=1.8,
            recommended_ec_max=1.6
        )

        result = rule.evaluate(context)

        assert result is not None
        assert result.triggered is True
        assert result.severity == RuleSeverity.INFO
        assert "slightly" in result.explanation.lower() or "above" in result.explanation.lower()

    def test_no_trigger_normal_ec(self):
        """Test no trigger when EC is within recommended range"""
        rule = SaltBuildupRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Tomato",
            current_ec_ms_cm=2.0,
            recommended_ec_max=2.5
        )

        result = rule.evaluate(context)

        assert result is None

    def test_not_applicable_without_data(self):
        """Test rule is not applicable without EC data"""
        rule = SaltBuildupRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Cucumber",
            current_ec_ms_cm=None
        )

        assert rule.is_applicable(context) is False

    def test_measured_value_in_result(self):
        """Test that measured EC value appears in result"""
        rule = SaltBuildupRule()
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Pepper",
            current_ec_ms_cm=4.2,
            recommended_ec_max=2.0
        )

        result = rule.evaluate(context)

        assert result is not None
        assert result.measured_value == 4.2
        assert "2.0" in result.optimal_range or "< 2.0" in result.optimal_range


@pytest.mark.nutrient_optimization
class TestNutrientRulesIntegration:
    """Integration tests for nutrient rules working together"""

    def test_multiple_nutrient_issues(self):
        """Test scenario with multiple nutrient problems"""
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Tomato",
            current_ph=4.5,  # Too low -> PHLockout
            current_ec_ms_cm=4.5,  # Too high -> SaltBuildup
            days_since_solution_change=25,  # Too old -> ECDrift
            recommended_change_days=14,
            optimal_ph_min=5.5,
            optimal_ph_max=6.5,
            recommended_ec_max=2.5
        )

        ph_rule = PHLockoutRule()
        ec_drift_rule = ECDriftRule()
        salt_rule = SaltBuildupRule()

        ph_result = ph_rule.evaluate(context)
        drift_result = ec_drift_rule.evaluate(context)
        salt_result = salt_rule.evaluate(context)

        # All three should trigger
        assert ph_result is not None
        assert drift_result is not None
        assert salt_result is not None

        # All should be critical
        assert ph_result.severity == RuleSeverity.CRITICAL
        assert drift_result.severity == RuleSeverity.CRITICAL
        assert salt_result.severity == RuleSeverity.CRITICAL

    def test_perfect_hydroponic_conditions(self):
        """Test scenario with perfect nutrient conditions"""
        context = RuleContext(
            is_hydroponic=True,
            plant_common_name="Lettuce",
            current_ph=6.0,  # Optimal
            current_ec_ms_cm=1.0,  # Good
            days_since_solution_change=7,  # Fresh
            recommended_change_days=14,
            optimal_ph_min=5.5,
            optimal_ph_max=6.5,
            recommended_ec_max=1.2
        )

        ph_rule = PHLockoutRule()
        ec_drift_rule = ECDriftRule()
        salt_rule = SaltBuildupRule()

        ph_result = ph_rule.evaluate(context)
        drift_result = ec_drift_rule.evaluate(context)
        salt_result = salt_rule.evaluate(context)

        # None should trigger
        assert ph_result is None
        assert drift_result is None
        assert salt_result is None

    def test_rule_categories(self):
        """Test that all nutrient rules have correct category"""
        from app.rules.engine.base import RuleCategory

        ph_rule = PHLockoutRule()
        drift_rule = ECDriftRule()
        salt_rule = SaltBuildupRule()

        assert ph_rule.category == RuleCategory.NUTRIENT_TIMING
        assert drift_rule.category == RuleCategory.NUTRIENT_TIMING
        assert salt_rule.category == RuleCategory.NUTRIENT_TIMING

    def test_rule_references_present(self):
        """Test that all nutrient rules include scientific references"""
        rules = [PHLockoutRule(), ECDriftRule(), SaltBuildupRule()]

        for rule in rules:
            # Create triggering context
            context = RuleContext(
            is_hydroponic=True,
                plant_common_name="Tomato",
                current_ph=4.0,
                current_ec_ms_cm=5.0,
                days_since_solution_change=30,
                recommended_change_days=14,
                optimal_ph_min=5.5,
                optimal_ph_max=6.5,
                recommended_ec_max=2.0
            )

            result = rule.evaluate(context)
            if result is not None:
                assert len(result.references) > 0
                # Check references are relevant
                assert any(
                    "hydroponic" in ref.lower() or
                    "nutrient" in ref.lower() or
                    "resh" in ref.lower() or
                    "jones" in ref.lower() or
                    "graves" in ref.lower()
                    for ref in result.references
                )