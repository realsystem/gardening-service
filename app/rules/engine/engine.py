"""
Rule Engine - Evaluates all rules against garden state.

Provides deterministic, testable evaluation with clear outputs.
"""

from typing import List, Optional, Dict
from datetime import datetime
import logging

from .base import Rule, RuleContext, RuleResult, RuleSeverity, RuleCategory

logger = logging.getLogger(__name__)


class RuleEngine:
    """
    Evaluates all registered rules against garden state.

    Design principles:
    - Deterministic: Same input always produces same output
    - Fast: Evaluates all rules in <100ms for typical garden
    - Safe: No side effects, clear error handling
    - Explainable: Every result includes rationale
    """

    def __init__(self, rules: Optional[List[Rule]] = None):
        """
        Initialize rule engine with optional rule list.

        Args:
            rules: List of Rule instances to evaluate
        """
        self.rules: List[Rule] = rules or []
        self._evaluation_count = 0
        self._last_evaluation_time: Optional[datetime] = None

    def register_rule(self, rule: Rule) -> None:
        """Add a rule to the engine."""
        if not isinstance(rule, Rule):
            raise TypeError(f"Expected Rule instance, got {type(rule)}")
        self.rules.append(rule)
        logger.info(f"Registered rule: {rule.rule_id}")

    def register_rules(self, rules: List[Rule]) -> None:
        """Add multiple rules to the engine."""
        for rule in rules:
            self.register_rule(rule)

    def evaluate(self, context: RuleContext) -> List[RuleResult]:
        """
        Evaluate all applicable rules against garden state.

        Args:
            context: Current garden state

        Returns:
            List of triggered rule results, sorted by severity
        """
        start_time = datetime.utcnow()
        results: List[RuleResult] = []

        for rule in self.rules:
            try:
                # Check if rule is applicable with current data
                if not rule.is_applicable(context):
                    logger.debug(f"Rule {rule.rule_id} not applicable, skipping")
                    continue

                # Evaluate rule
                result = rule.evaluate(context)

                # Only include triggered rules
                if result and result.triggered:
                    results.append(result)
                    logger.debug(f"Rule {rule.rule_id} triggered: {result.severity.value}")

            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {e}", exc_info=True)
                # Don't let one rule failure break the entire evaluation
                continue

        # Sort by severity (critical first, then warning, then info)
        severity_order = {
            RuleSeverity.CRITICAL: 0,
            RuleSeverity.WARNING: 1,
            RuleSeverity.INFO: 2
        }
        results.sort(key=lambda r: (severity_order[r.severity], r.rule_id))

        # Track evaluation metrics
        self._evaluation_count += 1
        self._last_evaluation_time = start_time
        evaluation_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.info(
            f"Evaluated {len(self.rules)} rules in {evaluation_time_ms:.1f}ms, "
            f"{len(results)} triggered"
        )

        # Performance assertion: Should complete in <100ms
        if evaluation_time_ms > 100:
            logger.warning(f"Rule evaluation slow: {evaluation_time_ms:.1f}ms")

        return results

    def get_rules_by_category(self, category: RuleCategory) -> List[Rule]:
        """Get all rules in a specific category."""
        return [r for r in self.rules if r.category == category]

    def get_rule_by_id(self, rule_id: str) -> Optional[Rule]:
        """Get a specific rule by ID."""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        return None

    def get_summary(self) -> Dict:
        """Get engine status and statistics."""
        return {
            "total_rules": len(self.rules),
            "rules_by_category": {
                cat.value: len(self.get_rules_by_category(cat))
                for cat in RuleCategory
            },
            "evaluation_count": self._evaluation_count,
            "last_evaluation": self._last_evaluation_time.isoformat() if self._last_evaluation_time else None
        }

    def __repr__(self) -> str:
        return f"<RuleEngine: {len(self.rules)} rules, {self._evaluation_count} evaluations>"
