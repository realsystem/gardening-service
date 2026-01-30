# Science-Based Gardening Rule Engine

## Overview

The Rule Engine is a deterministic, explainable, and scientifically-grounded system that evaluates garden state and generates intelligent recommendations based on measurable inputs.

### Design Principles

✅ **Deterministic**: Same input always produces same output
✅ **Explainable**: Every recommendation includes scientific rationale
✅ **Testable**: Rules can be unit tested in isolation
✅ **Scientifically Grounded**: Based on plant physiology research, not folklore
✅ **Performance**: Evaluates all rules in <100ms for typical garden
✅ **Safe**: No side effects, graceful error handling

---

## Rule Categories

### 1. Water Stress Rules (`WATER_001-003`)

**Detects:**
- Under-watering (root water stress)
- Over-watering (root oxygen deprivation)
- Excessive irrigation frequency

**Scientific Basis:**
- Transpiration rates vary by growth stage
- Root zone oxygen is critical for nutrient uptake
- Water stress timing affects yield significantly

**Rules Implemented:**
- `WATER_001`: Under-watering Detection
- `WATER_002`: Over-watering / Root Oxygen Stress
- `WATER_003`: Excessive Irrigation Frequency

### 2. Soil Chemistry Rules (`SOIL_001-003`)

**Detects:**
- pH imbalances affecting nutrient availability
- Nutrient deficiencies/toxicities
- Salinity stress

**Scientific Basis:**
- pH controls nutrient solubility (Mulder's chart)
- Nutrient availability follows predictable patterns
- Salinity reduces water potential (osmotic stress)

**Rules Implemented:**
- `SOIL_001`: Soil pH Imbalance
- `SOIL_002`: Nitrogen Deficiency
- `SOIL_003`: Soil Salinity Stress

### 3. Temperature Stress Rules (`TEMP_001-002`)

**Detects:**
- Cold shock / frost damage risk
- Heat stress / heat shock
- Suboptimal temperature ranges

**Scientific Basis:**
- Enzyme activity is temperature-dependent
- Membranes crystallize when cold, become fluid when hot
- Protein denaturation at extreme temperatures

**Rules Implemented:**
- `TEMP_001`: Cold Stress / Frost Risk
- `TEMP_002`: Heat Stress

### 4. Light Stress Rules (`LIGHT_001-002`)

**Detects:**
- Insufficient light (etiolation)
- Excessive light (photoinhibition)
- Photoperiod mismatch

**Scientific Basis:**
- Light drives photosynthesis (quantum yield)
- Photoinhibition damages photosystem II
- Photoperiod controls flowering

**Rules Implemented:**
- `LIGHT_001`: Insufficient Light (Etiolation Risk)
- `LIGHT_002`: Excessive Light (Photoinhibition Risk)

### 5. Growth Stage Rules (`GROWTH_001`)

**Detects:**
- Harvest window timing
- Growth stage transitions
- Nutrient timing issues

**Scientific Basis:**
- Plant development follows phenological stages
- Days to maturity vary by variety/temperature
- Optimal harvest timing affects quality

**Rules Implemented:**
- `GROWTH_001`: Harvest Window Approaching

---

## Architecture

### Core Components

#### 1. RuleContext

Input data structure containing all measurable garden state:

```python
@dataclass
class RuleContext:
    # Plant identification
    plant_common_name: Optional[str]
    plant_scientific_name: Optional[str]

    # Growth stage
    planting_date: Optional[datetime]
    days_since_planting: Optional[int]
    growth_stage: Optional[str]

    # Environment
    garden_type: Optional[str]  # outdoor, indoor, hydroponic
    is_indoor: bool
    is_hydroponic: bool

    # Soil conditions
    soil_ph: Optional[float]
    soil_moisture_percent: Optional[float]
    nitrogen_ppm: Optional[float]
    phosphorus_ppm: Optional[float]
    potassium_ppm: Optional[float]
    organic_matter_percent: Optional[float]
    soil_salinity_ec: Optional[float]

    # Irrigation
    days_since_last_watering: Optional[int]
    total_irrigation_events_7d: Optional[int]

    # Environmental
    temperature_f: Optional[float]
    temperature_min_f: Optional[float]
    temperature_max_f: Optional[float]
    humidity_percent: Optional[float]
    light_hours_per_day: Optional[float]

    # Frost risk
    frost_risk_next_7d: bool
```

#### 2. RuleResult

Output structure with explainable recommendations:

```python
@dataclass
class RuleResult:
    rule_id: str                    # e.g., "WATER_001"
    rule_category: RuleCategory     # WATER_STRESS, SOIL_CHEMISTRY, etc.
    title: str                      # Human-readable title
    triggered: bool                 # Whether rule condition is met
    severity: RuleSeverity          # INFO, WARNING, CRITICAL
    confidence: float               # 0.0-1.0

    # Explanations
    explanation: str                # What's happening
    scientific_rationale: str       # Why it matters (plant physiology)
    recommended_action: str         # What to do

    # Supporting data
    measured_value: Optional[float]
    optimal_range: Optional[str]
    deviation_severity: Optional[str]  # slight, moderate, severe

    # Scientific integrity
    references: List[str]           # Academic sources
```

#### 3. Rule Base Class

All rules inherit from abstract base:

```python
class Rule(ABC):
    @abstractmethod
    def get_rule_id(self) -> str:
        """Unique identifier (e.g., 'WATER_001')"""

    @abstractmethod
    def get_category(self) -> RuleCategory:
        """Rule category"""

    @abstractmethod
    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        """Evaluate rule against garden state"""

    def is_applicable(self, context: RuleContext) -> bool:
        """Check if rule can be evaluated with given data"""
```

#### 4. RuleEngine

Evaluates all rules deterministically:

```python
engine = RuleEngine(rules)
results = engine.evaluate(context)  # Returns List[RuleResult]
```

**Performance:**
- Target: <100ms for typical garden
- Monitoring: Logs warning if >100ms
- No side effects: Pure function evaluation

---

## API Usage

### Endpoint: GET /rule-insights/garden/{garden_id}

Get all insights for a garden.

**Response:**
```json
{
  "garden_id": 1,
  "garden_name": "Main Garden",
  "evaluation_time": "2026-01-29T18:00:00",
  "total_alerts": 3,
  "critical_alerts": 1,
  "warning_alerts": 2,
  "info_alerts": 0,
  "insights": [
    {
      "rule_id": "WATER_001",
      "category": "water_stress",
      "title": "Under-watering Detected",
      "triggered": true,
      "severity": "critical",
      "confidence": 0.95,
      "explanation": "Soil moisture is critically low at 12.3%. Plants are experiencing severe water stress.",
      "scientific_rationale": "At moisture levels below 15%, most plants cannot extract sufficient water from soil. Stomatal closure reduces photosynthesis by 40-60%...",
      "recommended_action": "Water immediately with 1-2 inches of water...",
      "measured_value": 12.3,
      "optimal_range": "20-60% (field capacity)",
      "deviation_severity": "severe",
      "references": [
        "Jones, H.G. (2004). Irrigation scheduling...",
        "Boyer, J.S. (1982). Plant productivity..."
      ]
    }
  ]
}
```

### Endpoint: GET /rule-insights/planting/{planting_id}

Get plant-specific insights.

**Response:** Same structure as garden endpoint, but with plant-specific context.

---

## Example Rule Outputs

### Example 1: Critical Under-Watering

```json
{
  "rule_id": "WATER_001",
  "severity": "critical",
  "explanation": "Last watered 7 days ago. Severely overdue for Tomato (recommended every 3 days).",
  "scientific_rationale": "Extended water stress (4 days overdue) causes irreversible cellular damage. During fruiting stages, this can reduce yields by 30-50%.",
  "recommended_action": "Water immediately. Apply water slowly to allow soil infiltration...",
  "measured_value": 7.0,
  "optimal_range": "Every 2-4 days"
}
```

### Example 2: pH Imbalance

```json
{
  "rule_id": "SOIL_001",
  "severity": "warning",
  "explanation": "Soil pH is slightly acidic at 5.7. Optimal range for Tomato is 6.0-6.8.",
  "scientific_rationale": "Below optimal pH, nutrient availability decreases. Calcium and magnesium become less available...",
  "recommended_action": "Add 2.5 lbs of garden lime per 100 sq ft. Mix into topsoil.",
  "measured_value": 5.7,
  "optimal_range": "6.0 - 6.8"
}
```

### Example 3: Heat Stress

```json
{
  "rule_id": "TEMP_002",
  "severity": "critical",
  "explanation": "Temperature is critically high at 98°F, exceeding maximum for Lettuce by 23°F.",
  "scientific_rationale": "Above 75°F, protein denaturation occurs. Photosystem II is damaged. Respiration exceeds photosynthesis...",
  "recommended_action": "Provide shade immediately (shade cloth 30-50%). Increase watering frequency...",
  "measured_value": 98.0,
  "optimal_range": "60-70°F"
}
```

---

## Testing

### Unit Tests

Each rule must have:
- **Pass case**: Rule triggers when it should
- **Fail case**: Rule doesn't trigger when conditions are normal
- **Edge case**: Rule handles boundary conditions

**Example:**

```python
def test_underwatering_critical():
    """WATER_001 triggers for critically low moisture"""
    context = RuleContext(soil_moisture_percent=12.0)
    rule = UnderWateringRule()
    result = rule.evaluate(context)

    assert result is not None
    assert result.triggered == True
    assert result.severity == RuleSeverity.CRITICAL
    assert result.confidence >= 0.90

def test_underwatering_optimal():
    """WATER_001 does not trigger for optimal moisture"""
    context = RuleContext(soil_moisture_percent=45.0)
    rule = UnderWateringRule()
    result = rule.evaluate(context)

    assert result is None  # No alert when optimal
```

### Integration Tests

```python
def test_rule_engine_evaluation():
    """Engine evaluates all rules deterministically"""
    context = RuleContext(
        soil_ph=5.5,
        soil_moisture_percent=12.0,
        temperature_f=95.0
    )

    registry = get_registry()
    engine = registry.create_engine()
    results = engine.evaluate(context)

    # Should trigger multiple rules
    assert len(results) > 0
    # Should be sorted by severity
    assert results[0].severity == RuleSeverity.CRITICAL
```

---

## Adding New Rules

### Step 1: Create Rule Class

```python
from app.rules.engine.base import Rule, RuleContext, RuleResult, RuleSeverity, RuleCategory

class MyNewRule(Rule):
    def get_rule_id(self) -> str:
        return "CATEGORY_###"  # Unique ID

    def get_category(self) -> RuleCategory:
        return RuleCategory.WATER_STRESS  # Or appropriate category

    def get_title(self) -> str:
        return "Short Human-Readable Title"

    def get_description(self) -> str:
        return "Detailed description of what this rule checks"

    def is_applicable(self, context: RuleContext) -> bool:
        # Return True if rule can be evaluated with given data
        return context.required_field is not None

    def evaluate(self, context: RuleContext) -> Optional[RuleResult]:
        # Evaluate condition
        if condition_is_met:
            return RuleResult(
                rule_id=self.rule_id,
                rule_category=self.category,
                title=self.title,
                triggered=True,
                severity=RuleSeverity.WARNING,  # or CRITICAL, INFO
                confidence=0.85,  # 0.0-1.0
                explanation="Plain English: what's happening",
                scientific_rationale="Why this matters (plant physiology)",
                recommended_action="What to do about it",
                measured_value=measured_value,
                optimal_range="Expected range",
                deviation_severity="slight/moderate/severe",
                references=["Academic citation 1", "Academic citation 2"]
            )
        return None  # No alert if condition not met
```

### Step 2: Register Rule

Add to appropriate rule module's `get_*_rules()` function:

```python
def get_water_rules() -> List[Rule]:
    return [
        UnderWateringRule(),
        OverWateringRule(),
        MyNewRule(),  # Add here
    ]
```

### Step 3: Write Tests

```python
def test_my_new_rule_triggers():
    context = RuleContext(required_field=problematic_value)
    rule = MyNewRule()
    result = rule.evaluate(context)
    assert result.triggered == True

def test_my_new_rule_does_not_trigger():
    context = RuleContext(required_field=normal_value)
    rule = MyNewRule()
    result = rule.evaluate(context)
    assert result is None
```

---

## Scientific Integrity

### Every Rule Must Include:

1. **Scientific Rationale**: Brief explanation of plant physiological basis
2. **References**: At least one academic citation
3. **Measurable Thresholds**: Specific numeric values, not vague terms
4. **Conservative Confidence**: Don't overclaim certainty

### No Folklore Gardening

❌ **Bad**: "Plant by the moon phases"
✅ **Good**: "Photoperiod affects flowering in day-length sensitive species"

❌ **Bad**: "Add eggshells for calcium"
✅ **Good**: "Add lime (CaCO3) to raise pH and provide calcium"

---

## Performance Monitoring

Engine tracks evaluation metrics:

```python
engine.get_summary()
# Returns:
{
  "total_rules": 11,
  "rules_by_category": {
    "water_stress": 3,
    "soil_chemistry": 3,
    "temperature_stress": 2,
    "light_stress": 2,
    "growth_stage": 1
  },
  "evaluation_count": 42,
  "last_evaluation": "2026-01-29T18:00:00"
}
```

---

## Current Implementation Status

### ✅ Implemented (11 Rules)

| Rule ID | Category | Description |
|---------|----------|-------------|
| WATER_001 | Water Stress | Under-watering Detection |
| WATER_002 | Water Stress | Over-watering / Root Oxygen Stress |
| WATER_003 | Water Stress | Excessive Irrigation Frequency |
| SOIL_001 | Soil Chemistry | Soil pH Imbalance |
| SOIL_002 | Soil Chemistry | Nitrogen Deficiency |
| SOIL_003 | Soil Chemistry | Soil Salinity Stress |
| TEMP_001 | Temperature Stress | Cold Stress / Frost Risk |
| TEMP_002 | Temperature Stress | Heat Stress |
| LIGHT_001 | Light Stress | Insufficient Light (Etiolation) |
| LIGHT_002 | Light Stress | Excessive Light (Photoinhibition) |
| GROWTH_001 | Growth Stage | Harvest Window Approaching |

### Future Enhancements

- Add phosphorus/potassium deficiency rules
- Implement photoperiod mismatch detection
- Add growth stage nutrient timing rules
- Create pest/disease risk assessment rules
- Integrate weather forecast data for predictive alerts

---

## Files

### Core Engine
- `app/rules/engine/__init__.py` - Package exports
- `app/rules/engine/base.py` - Base classes (Rule, RuleContext, RuleResult)
- `app/rules/engine/engine.py` - RuleEngine implementation
- `app/rules/engine/registry.py` - Global rule registry

### Rule Implementations
- `app/rules/rules_water.py` - Water stress rules (3 rules)
- `app/rules/rules_soil.py` - Soil chemistry rules (3 rules)
- `app/rules/rules_temperature.py` - Temperature stress rules (2 rules)
- `app/rules/rules_light.py` - Light stress rules (2 rules)
- `app/rules/rules_growth.py` - Growth stage rules (1 rule)

### API
- `app/api/rule_insights.py` - API endpoints for rule evaluation

### Documentation
- `RULE_ENGINE.md` - This file

---

## Summary

The Rule Engine provides **professional-grade gardening science** for amateur gardeners:

✅ **Actionable**: Specific amounts, not vague advice
✅ **Plant-Specific**: Different recommendations for each plant
✅ **Research-Based**: Agricultural best practices with citations
✅ **Explainable**: Every recommendation includes scientific rationale
✅ **Testable**: Rules can be validated independently
✅ **Fast**: <100ms evaluation time
✅ **Safe**: No side effects, deterministic behavior

This ensures gardeners receive credible, scientifically-sound recommendations they can trust.
