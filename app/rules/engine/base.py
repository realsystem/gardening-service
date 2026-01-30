"""
Base classes for the Science-Based Rule Engine.

Defines the core rule structure and evaluation interfaces.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List


class RuleSeverity(str, Enum):
    """Severity levels for rule violations."""
    INFO = "info"           # Informational, no action needed
    WARNING = "warning"     # Should address soon
    CRITICAL = "critical"   # Immediate action required


class RuleCategory(str, Enum):
    """Categories of gardening rules."""
    WATER_STRESS = "water_stress"
    SOIL_CHEMISTRY = "soil_chemistry"
    TEMPERATURE_STRESS = "temperature_stress"
    LIGHT_STRESS = "light_stress"
    GROWTH_STAGE = "growth_stage"
    PEST_DISEASE = "pest_disease"
    NUTRIENT_TIMING = "nutrient_timing"


@dataclass
class RuleContext:
    """
    Input context for rule evaluation.

    Contains all measurable garden state needed for scientific assessment.
    """
    # Plant identification
    plant_variety_id: Optional[int] = None
    plant_common_name: Optional[str] = None
    plant_scientific_name: Optional[str] = None

    # Growth stage
    planting_date: Optional[datetime] = None
    days_since_planting: Optional[int] = None
    growth_stage: Optional[str] = None  # germination, vegetative, flowering, fruiting, harvest

    # Environment type
    garden_type: Optional[str] = None  # outdoor, indoor, hydroponic
    is_indoor: bool = False
    is_hydroponic: bool = False

    # Soil conditions (None for hydroponics)
    soil_ph: Optional[float] = None
    soil_moisture_percent: Optional[float] = None
    nitrogen_ppm: Optional[float] = None
    phosphorus_ppm: Optional[float] = None
    potassium_ppm: Optional[float] = None
    organic_matter_percent: Optional[float] = None
    soil_salinity_ec: Optional[float] = None  # Electrical conductivity

    # Irrigation data
    days_since_last_watering: Optional[int] = None
    total_irrigation_events_7d: Optional[int] = None
    avg_water_volume_liters: Optional[float] = None

    # Environmental
    temperature_f: Optional[float] = None
    temperature_min_f: Optional[float] = None  # 24h min
    temperature_max_f: Optional[float] = None  # 24h max
    humidity_percent: Optional[float] = None
    light_hours_per_day: Optional[float] = None
    light_source_type: Optional[str] = None  # natural, led, fluorescent

    # Frost risk (outdoor only)
    frost_risk_next_7d: bool = False
    last_frost_date: Optional[datetime] = None

    # Additional metadata
    user_id: Optional[int] = None
    garden_id: Optional[int] = None
    planting_event_id: Optional[int] = None

    # Timestamp of evaluation
    evaluation_time: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RuleResult:
    """
    Output from a rule evaluation.

    Provides actionable, explainable, and scientifically-grounded recommendations.
    """
    # Rule identification
    rule_id: str
    rule_category: RuleCategory
    title: str

    # Assessment
    triggered: bool  # Whether rule condition is met
    severity: RuleSeverity
    confidence: float  # 0.0-1.0, how certain is this assessment

    # Explanation
    explanation: str  # Plain English explanation of what's happening
    scientific_rationale: str  # Why this matters (plant physiology)
    recommended_action: Optional[str] = None  # What to do about it

    # Supporting data
    measured_value: Optional[float] = None
    optimal_range: Optional[str] = None
    deviation_severity: Optional[str] = None  # slight, moderate, severe

    # Metadata
    evaluation_time: datetime = field(default_factory=datetime.utcnow)
    references: List[str] = field(default_factory=list)  # Scientific sources

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "rule_id": self.rule_id,
            "category": self.rule_category.value,
            "title": self.title,
            "triggered": self.triggered,
            "severity": self.severity.value,
            "confidence": round(self.confidence, 2),
            "explanation": self.explanation,
            "scientific_rationale": self.scientific_rationale,
            "recommended_action": self.recommended_action,
            "measured_value": self.measured_value,
            "optimal_range": self.optimal_range,
            "deviation_severity": self.deviation_severity,
            "evaluation_time": self.evaluation_time.isoformat(),
            "references": self.references
        }


class Rule(ABC):
    """
    Abstract base class for all gardening rules.

    Each rule:
    - Has a unique ID
    - Belongs to a category
    - Evaluates garden state deterministically
    - Provides scientific rationale
    - Is independently testable
    """

    def __init__(self):
        """Initialize rule metadata."""
        self.rule_id: str = self.get_rule_id()
        self.category: RuleCategory = self.get_category()
        self.title: str = self.get_title()
        self.description: str = self.get_description()

    @abstractmethod
    def get_rule_id(self) -> str:
        """Return unique rule identifier (e.g., 'WATER_001')."""
        pass

    @abstractmethod
    def get_category(self) -> RuleCategory:
        """Return rule category."""
        pass

    @abstractmethod
    def get_title(self) -> str:
        """Return short human-readable title."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Return detailed description of what this rule checks."""
        pass

    @abstractmethod
    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        """
        Evaluate the rule against garden state.

        Args:
            context: Current garden state

        Returns:
            RuleResult if rule is applicable and triggered, None otherwise
        """
        pass

    def is_applicable(self, context: RuleContext) -> bool:
        """
        Check if rule can be evaluated with given context.

        Override this method if rule requires specific data.
        Default returns True.
        """
        return True

    def __repr__(self) -> str:
        return f"<Rule {self.rule_id}: {self.title}>"
