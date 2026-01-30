"""
Rule Registry - Centralized rule loading and management.

Provides a single source of truth for all garden rules.
"""

from typing import List, Dict, Optional
from .base import Rule, RuleCategory
from .engine import RuleEngine


class RuleRegistry:
    """
    Central registry for all gardening rules.

    Responsibilities:
    - Load all rule modules
    - Validate rule uniqueness
    - Provide rule discovery
    - Create configured RuleEngine instances
    """

    def __init__(self):
        """Initialize empty registry."""
        self._rules: Dict[str, Rule] = {}
        self._initialized = False

    def register(self, rule: Rule) -> None:
        """
        Register a single rule.

        Args:
            rule: Rule instance to register

        Raises:
            ValueError: If rule ID already exists
        """
        if rule.rule_id in self._rules:
            raise ValueError(f"Rule ID {rule.rule_id} already registered")

        self._rules[rule.rule_id] = rule

    def register_many(self, rules: List[Rule]) -> None:
        """Register multiple rules."""
        for rule in rules:
            self.register(rule)

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)

    def get_all_rules(self) -> List[Rule]:
        """Get all registered rules."""
        return list(self._rules.values())

    def get_rules_by_category(self, category: RuleCategory) -> List[Rule]:
        """Get all rules in a specific category."""
        return [r for r in self._rules.values() if r.category == category]

    def create_engine(self, categories: Optional[List[RuleCategory]] = None) -> RuleEngine:
        """
        Create a RuleEngine instance with registered rules.

        Args:
            categories: Optional list of categories to include (default: all)

        Returns:
            Configured RuleEngine instance
        """
        if categories:
            rules = []
            for cat in categories:
                rules.extend(self.get_rules_by_category(cat))
        else:
            rules = self.get_all_rules()

        return RuleEngine(rules=rules)

    def get_summary(self) -> Dict:
        """Get registry statistics."""
        return {
            "total_rules": len(self._rules),
            "rules_by_category": {
                cat.value: len(self.get_rules_by_category(cat))
                for cat in RuleCategory
            },
            "rule_ids": sorted(self._rules.keys())
        }

    def __repr__(self) -> str:
        return f"<RuleRegistry: {len(self._rules)} rules>"


# Global registry instance
_global_registry: Optional[RuleRegistry] = None


def get_registry() -> RuleRegistry:
    """Get the global rule registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = RuleRegistry()
        # Load all rules
        _load_all_rules(_global_registry)
    return _global_registry


def _load_all_rules(registry: RuleRegistry) -> None:
    """
    Load all rule implementations into registry.

    This function imports and registers all rule classes.
    """
    # Import all rule modules
    # (We'll create these in the next steps)
    try:
        from ..rules_water import get_water_rules
        registry.register_many(get_water_rules())
    except ImportError:
        pass

    try:
        from ..rules_soil import get_soil_rules
        registry.register_many(get_soil_rules())
    except ImportError:
        pass

    try:
        from ..rules_temperature import get_temperature_rules
        registry.register_many(get_temperature_rules())
    except ImportError:
        pass

    try:
        from ..rules_light import get_light_rules
        registry.register_many(get_light_rules())
    except ImportError:
        pass

    try:
        from ..rules_growth import get_growth_rules
        registry.register_many(get_growth_rules())
    except ImportError:
        pass
