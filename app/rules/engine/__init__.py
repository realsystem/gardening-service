"""
Science-Based Gardening Rule Engine

A declarative, testable, and scientifically-grounded rule system for
generating intelligent recommendations based on measurable garden state.
"""

from .base import Rule, RuleResult, RuleSeverity, RuleContext, RuleCategory
from .engine import RuleEngine
from .registry import RuleRegistry, get_registry

__all__ = [
    'Rule',
    'RuleResult',
    'RuleSeverity',
    'RuleContext',
    'RuleCategory',
    'RuleEngine',
    'RuleRegistry',
    'get_registry',
]
