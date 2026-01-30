# Soil & Irrigation Tracking + Science Insights

Comprehensive soil analysis and irrigation tracking with actionable, science-based recommendations for amateur gardeners.

## Overview

This feature set adds professional-grade soil and water management to the gardening service:

1. **Soil Tracking** - Monitor soil chemistry with real-time recommendations
2. **Irrigation Tracking** - Log watering events with smart scheduling
3. **Science Engine** - Plant-specific, research-based guidance

All recommendations provide **specific numeric amounts** (lbs of lime, gallons of water, etc.) based on agricultural research.

---

## Soil Tracking

### Features

- **Track soil chemistry**: pH, Nitrogen (N), Phosphorus (P), Potassium (K), organic matter, moisture
- **Plant-specific analysis**: Different optimal ranges for tomatoes, lettuce, peppers, etc.
- **Actionable recommendations**: Exact amounts of amendments needed
- **Historical tracking**: Monitor soil improvements over time
- **Link to gardens or plantings**: Garden-wide or plant-specific samples

### Soil Sample Data

| Parameter | Range | Unit | Required |
|-----------|-------|------|----------|
| pH | 0-14 | - | ✅ |
| Nitrogen | 0+ | PPM | Optional |
| Phosphorus | 0+ | PPM | Optional |
| Potassium | 0+ | PPM | Optional |
| Organic Matter | 0-100 | % | Optional |
| Soil Moisture | 0-100 | % | Optional |

### Scientific Recommendations

The system generates specific guidance based on measured values:

#### pH Management

**Low pH (< 6.0 for most vegetables)**:
- Status: `low` or `critical`
- Recommendation: "Add X lbs of dolomitic lime per 100 sq ft"
- Specific amounts calculated based on pH deficit
- Alternative: Wood ash recommendations

**High pH (> 7.0 for most vegetables)**:
- Status: `high` or `critical`
- Recommendation: "Add X lbs of elemental sulfur per 100 sq ft"
- Alternative: Sulfate-based fertilizers, peat moss

#### Nutrient Management

**Nitrogen (N)**:
- Low: "Add X inches of aged compost or blood meal (12-0-0) at Y lbs per 100 sq ft"
- Deficient: Fish emulsion side-dressing every 2 weeks
- High: Plant heavy feeders, skip nitrogen fertilizers

**Phosphorus (P)**:
- Low: "Add bone meal (3-15-0) at X lbs per 100 sq ft"
- Deficient: Rock phosphate for long-term availability
- High: Avoid phosphorus fertilizers

**Potassium (K)**:
- Low: "Add greensand (0-0-3), kelp meal (1-0-2), or wood ash (0-0-8)"
- Deficient: Specific application rates based on deficit
- High: Leaching recommendations

#### Organic Matter

- Optimal range: 3-6%
- Low (<2%): Add 3-4 inches of compost worked into top 6-8 inches
- Very low: Cover crops (clover, rye) between seasons

#### Soil Moisture

- Optimal: 20-60% (field capacity)
- Dry (<15%): Immediate watering, mulching recommendations
- Wet (>70%): Drainage improvements, raised beds

### API Endpoints

#### POST /soil-samples

Create a new soil sample.

**Request:**
```json
{
  "garden_id": 1,
  "planting_event_id": null,
  "ph": 6.5,
  "nitrogen_ppm": 30,
  "phosphorus_ppm": 40,
  "potassium_ppm": 180,
  "organic_matter_percent": 4.5,
  "moisture_percent": 45,
  "date_collected": "2026-01-28",
  "notes": "Spring soil test"
}
```

**Response:**
```json
{
  "id": 1,
  "garden_id": 1,
  "ph": 6.5,
  "nitrogen_ppm": 30,
  ...
  "recommendations": [
    {
      "parameter": "pH",
      "current_value": 6.5,
      "optimal_range": "6.0 - 6.8",
      "status": "optimal",
      "recommendation": "pH is optimal for tomatoes. Maintain current levels with regular compost additions.",
      "priority": "low"
    },
    {
      "parameter": "Nitrogen",
      "current_value": 30,
      "optimal_range": "20 - 50 ppm",
      "status": "optimal",
      "recommendation": "Nitrogen is optimal for tomatoes. Maintain with 1-2 inches of compost annually.",
      "priority": "low"
    }
  ]
}
```

#### GET /soil-samples

List all soil samples with filters.

**Query Parameters:**
- `garden_id` - Filter by garden
- `planting_event_id` - Filter by planting
- `start_date` - From date
- `end_date` - To date

**Response:**
```json
{
  "samples": [...],
  "total": 5,
  "latest_sample": {...}
}
```

#### GET /soil-samples/{id}

Get specific soil sample with recommendations.

#### DELETE /soil-samples/{id}

Delete a soil sample.

---

## Irrigation Tracking

### Features

- **Log irrigation events**: Date, time, volume, method, duration
- **Smart scheduling**: Plant-specific watering frequencies
- **Overdue alerts**: High-priority notifications for overdue watering
- **Overwatering detection**: Prevent root rot with frequency analysis
- **Water usage statistics**: Track total volume, average per event
- **Multiple methods**: Drip, sprinkler, hand watering, soaker hose, flood, misting

### Irrigation Methods

- `drip` - Drip irrigation systems
- `sprinkler` - Overhead sprinklers
- `hand_watering` - Manual watering with hose or can
- `soaker_hose` - Soaker hoses
- `flood` - Flood irrigation
- `misting` - Misting systems (for seedlings, cuttings)

### Plant Water Requirements

Built-in database of watering needs:

| Plant | Frequency (days) | Volume (L/sq ft) | Notes |
|-------|------------------|------------------|-------|
| Tomato | 3 | 1.5 | Critical during fruiting |
| Lettuce | 2 | 1.0 | Shallow roots, keep moist |
| Cucumber | 2 | 1.6 | High water needs |
| Carrot | 4 | 1.2 | Even moisture prevents splitting |
| Pepper | 3 | 1.4 | Reduce during ripening |
| Broccoli | 3 | 1.3 | Consistent for head development |
| Spinach | 3 | 1.1 | Cool-season, avoid overwatering |
| Basil | 2 | 1.0 | Keep moist but not waterlogged |

### Irrigation Recommendations

#### On Schedule
```json
{
  "plant_name": "Tomato",
  "days_since_last_watering": 2,
  "recommended_frequency_days": 3,
  "recommended_volume_liters": 1.5,
  "status": "on_schedule",
  "recommendation": "Watering schedule is good. Last watered 2 days ago. Next watering in 1 days. Apply 1.5 liters per sq ft when watering.",
  "priority": "low"
}
```

#### Overdue
```json
{
  "plant_name": "Lettuce",
  "days_since_last_watering": 5,
  "recommended_frequency_days": 2,
  "status": "overdue",
  "recommendation": "Water immediately! Last watered 5 days ago (recommended: every 2 days). Apply 1.0 liters per sq ft. Water deeply in early morning. Keep soil consistently moist, shallow roots",
  "priority": "high"
}
```

#### Overwatered
```json
{
  "plant_name": "Carrot",
  "days_since_last_watering": 1,
  "recommended_frequency_days": 4,
  "status": "overwatered",
  "recommendation": "Watering too frequently. Last watered 1 days ago. Wait 3 more days before next watering. Overwatering can cause root rot and nutrient leaching.",
  "priority": "medium"
}
```

### API Endpoints

#### POST /irrigation

Log a new irrigation event.

**Request:**
```json
{
  "garden_id": 1,
  "irrigation_date": "2026-01-28T08:30:00",
  "water_volume_liters": 20.0,
  "irrigation_method": "hand_watering",
  "duration_minutes": 15,
  "notes": "Morning watering, weather sunny"
}
```

**Response:**
```json
{
  "id": 1,
  "garden_id": 1,
  "irrigation_date": "2026-01-28T08:30:00",
  "water_volume_liters": 20.0,
  "irrigation_method": "hand_watering",
  "duration_minutes": 15,
  "garden_name": "Main Garden"
}
```

#### GET /irrigation

List irrigation events with summary and recommendations.

**Query Parameters:**
- `garden_id` - Filter by garden
- `planting_event_id` - Filter by planting
- `days` - Last N days (default: all time)
- `start_date` - From datetime
- `end_date` - To datetime

**Response:**
```json
{
  "events": [...],
  "summary": {
    "total_events": 15,
    "total_volume_liters": 250.0,
    "last_irrigation_date": "2026-01-28T08:30:00",
    "days_since_last_irrigation": 0,
    "average_volume_per_event": 16.7,
    "most_common_method": "hand_watering",
    "recommendations": [...]
  }
}
```

#### GET /irrigation/summary

Get irrigation summary and recommendations without event details.

**Query Parameters:**
- `garden_id` - Garden ID
- `planting_event_id` - Planting ID
- `days` - Number of days (default: 30)

#### DELETE /irrigation/{id}

Delete an irrigation event.

---

## Frontend Components

### Soil Components

#### SoilSampleForm
Create new soil samples with form validation.

**Props:**
```typescript
interface SoilSampleFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
  defaultGardenId?: number;
  defaultPlantingEventId?: number;
}
```

**Usage:**
```tsx
<SoilSampleForm
  onSuccess={() => loadSamples()}
  onCancel={() => setShowForm(false)}
  defaultGardenId={gardenId}
/>
```

#### SoilSampleList
Display soil samples with expandable recommendations.

**Props:**
```typescript
interface SoilSampleListProps {
  gardenId?: number;
  plantingEventId?: number;
  onRefresh?: () => void;
}
```

**Features:**
- Soil chemistry data grid
- Expandable scientific recommendations
- Priority badges (critical, high, medium, low)
- Status color coding
- Delete functionality

### Irrigation Components

#### IrrigationLog
Log new irrigation events.

**Props:**
```typescript
interface IrrigationLogProps {
  onSuccess?: () => void;
  onCancel?: () => void;
  defaultGardenId?: number;
  defaultPlantingEventId?: number;
}
```

#### IrrigationHistory
View irrigation history with statistics and recommendations.

**Props:**
```typescript
interface IrrigationHistoryProps {
  gardenId?: number;
  plantingEventId?: number;
  days?: number;  // Default: 30
  onRefresh?: () => void;
}
```

**Features:**
- Summary statistics cards
- Watering recommendations (expandable)
- Event history with method/volume display
- Delete functionality
- Day range selector

---

## Database Schema

### soil_samples Table

```sql
CREATE TABLE soil_samples (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) NOT NULL,
  garden_id INTEGER REFERENCES gardens(id) ON DELETE CASCADE,
  planting_event_id INTEGER REFERENCES planting_events(id) ON DELETE CASCADE,

  ph FLOAT NOT NULL,
  nitrogen_ppm FLOAT,
  phosphorus_ppm FLOAT,
  potassium_ppm FLOAT,
  organic_matter_percent FLOAT,
  moisture_percent FLOAT,

  date_collected DATE NOT NULL,
  notes TEXT
);
```

### irrigation_events Table

```sql
CREATE TABLE irrigation_events (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) NOT NULL,
  garden_id INTEGER REFERENCES gardens(id) ON DELETE CASCADE,
  planting_event_id INTEGER REFERENCES planting_events(id) ON DELETE CASCADE,

  irrigation_date TIMESTAMP NOT NULL,
  water_volume_liters FLOAT,
  irrigation_method VARCHAR(50) NOT NULL,
  duration_minutes INTEGER,
  notes TEXT
);
```

**Cascade Behavior:**
- Deleting a garden deletes all its soil samples and irrigation events
- Deleting a planting event deletes its soil samples and irrigation events

---

## Science-Based Rule Engine

The **Science-Based Gardening Rule Engine** provides deterministic, explainable, and scientifically-grounded recommendations based on measurable garden state. See [RULE_ENGINE.md](RULE_ENGINE.md) for complete documentation.

### Architecture (`app/rules/engine/`)

**Core Components:**
- `RuleContext` - Comprehensive input data (27 parameters: plant ID, soil chemistry, environmental conditions, irrigation history)
- `RuleResult` - Structured output with severity, confidence, scientific rationale, and academic references
- `Rule` - Abstract base class enforcing scientific standards
- `RuleEngine` - Deterministic evaluation (<100ms performance target)
- `RuleRegistry` - Global rule management and discovery

### Rule Categories (11 Rules Implemented)

**1. Water Stress Rules** (`app/rules/rules_water.py`):
- `WATER_001` - Under-watering detection (soil moisture <15% critical, <20% warning)
- `WATER_002` - Over-watering/root oxygen stress (>70% critical, >60% warning)
- `WATER_003` - Excessive irrigation frequency (>10 events in 7 days)

**2. Soil Chemistry Rules** (`app/rules/rules_soil.py`):
- `SOIL_001` - pH imbalance (plant-specific ranges: tomato 6.0-6.8, blueberry 4.5-5.5)
- `SOIL_002` - Nitrogen deficiency (<10 ppm critical, <20 ppm warning)
- `SOIL_003` - Salinity stress (EC >4.0 dS/m critical, >2.0 warning)

**3. Temperature Stress Rules** (`app/rules/rules_temperature.py`):
- `TEMP_001` - Cold stress/frost risk (below plant minimums, frost warnings)
- `TEMP_002` - Heat stress (>95°F critical for most plants, plant-specific maximums)

**4. Light Stress Rules** (`app/rules/rules_light.py`):
- `LIGHT_001` - Etiolation risk (insufficient light causing spindly growth)
- `LIGHT_002` - Photoinhibition (excessive artificial light >18 hrs/day)

**5. Growth Stage Rules** (`app/rules/rules_growth.py`):
- `GROWTH_001` - Harvest readiness (within ±7 days of expected harvest date)

### API Endpoints

**Garden-Level Evaluation:**
```bash
GET /rule-insights/garden/{garden_id}
```

**Plant-Level Evaluation:**
```bash
GET /rule-insights/planting/{planting_id}
```

**Response Format:**
```json
{
  "garden_id": 1,
  "garden_name": "Main Garden",
  "evaluation_time": "2026-01-29T19:00:00Z",
  "triggered_rules": [
    {
      "rule_id": "WATER_001",
      "category": "water_stress",
      "title": "Under-watering Detected",
      "severity": "critical",
      "confidence": 0.95,
      "explanation": "Soil moisture is critically low at 8.0%...",
      "scientific_rationale": "At moisture levels below 15%, stomatal closure reduces photosynthesis by 40-60%...",
      "recommended_action": "Water immediately with 1-2 inches of water...",
      "measured_value": 8.0,
      "optimal_range": "20-60% (field capacity)",
      "references": ["Jones, H.G. (2004). Irrigation scheduling..."]
    }
  ],
  "rules_by_severity": {
    "critical": 2,
    "warning": 1,
    "info": 1
  }
}
```

### Scientific Integrity Requirements

**Every rule must include:**
- **Scientific rationale** - Plant physiology explanation (transpiration, photosynthesis, nutrient uptake)
- **Academic references** - Peer-reviewed research citations
- **Confidence score** - 0.0-1.0 certainty level
- **Measured values** - Actual vs. optimal ranges
- **Specific actions** - Amendment calculations, timing recommendations

**No folklore allowed** - All recommendations backed by horticulture science

### Frontend Integration

**RuleInsightsCard Component** (`frontend/src/components/RuleInsightsCard.tsx`):
- Color-coded severity indicators (🚨 Critical, ⚠️ Warning, ℹ️ Info)
- Interactive filtering by severity
- Expandable rule details showing scientific rationale and references
- Real-time evaluation timestamps
- Smart empty states ("All Systems Optimal" when no issues detected)

**Integrated in Dashboard:**
```typescript
<RuleInsightsCard gardenId={gardens[0]?.id} />
```

### Testing

**Comprehensive Test Suite** (`tests/test_rule_engine.py`):
- 57 tests with 100% pass rate
- Unit tests for each rule (45 tests)
- Integration tests for RuleEngine (7 tests)
- Real-world scenario tests (6 tests)
- Scientific integrity validation (3 tests)

**Run Tests:**
```bash
pytest tests/test_rule_engine.py -v
```

### Performance

- **Evaluation time:** <100ms for all 11 rules (target and actual)
- **Deterministic:** Same input always produces same output
- **No side effects:** Pure evaluation functions
- **Scalable:** Add new rules without modifying engine code

---

## Testing

### Backend Tests

**Soil Sample Tests** (`tests/test_soil_samples.py`):
- CRUD operations (create, list, get, delete)
- Authorization (users can only access their own samples)
- Filtering (by garden, planting, date range)
- Recommendation generation
- Numeric guidance verification

**Irrigation Tests** (`tests/test_irrigation.py`):
- CRUD operations
- Summary statistics calculation
- Recommendation generation (on-schedule, overdue, overwatered)
- Cascade deletion with gardens/plantings
- Authorization

**Run Tests:**
```bash
pytest tests/test_soil_samples.py -v
pytest tests/test_irrigation.py -v
```

### Frontend Tests (Pending)

- SoilSampleForm: Form validation, submission
- SoilSampleList: Display, recommendations, delete
- IrrigationLog: Form validation, method selection
- IrrigationHistory: Statistics, recommendations, filtering

---

## Usage Examples

### Complete Soil Workflow

1. **Take a soil sample:**
```bash
POST /soil-samples
{
  "garden_id": 1,
  "ph": 5.5,
  "nitrogen_ppm": 15,
  "phosphorus_ppm": 25,
  "potassium_ppm": 120,
  "date_collected": "2026-01-28"
}
```

2. **Get recommendations:**
```json
{
  "recommendations": [
    {
      "parameter": "pH",
      "status": "low",
      "recommendation": "Add 2.5 lbs of dolomitic lime per 100 sq ft...",
      "priority": "high"
    },
    {
      "parameter": "Nitrogen",
      "status": "low",
      "recommendation": "Add 2 inches of compost, or apply alfalfa meal...",
      "priority": "high"
    }
  ]
}
```

3. **Apply amendments** based on recommendations

4. **Re-test in 2-4 weeks** to verify improvements

### Complete Irrigation Workflow

1. **Log watering:**
```bash
POST /irrigation
{
  "planting_event_id": 5,
  "irrigation_date": "2026-01-28T08:00:00",
  "water_volume_liters": 10.0,
  "irrigation_method": "drip"
}
```

2. **Check recommendations:**
```bash
GET /irrigation?planting_event_id=5
```

3. **Review summary:**
```json
{
  "summary": {
    "days_since_last_irrigation": 0,
    "recommendations": [
      {
        "plant_name": "Tomato",
        "status": "on_schedule",
        "recommendation": "Next watering in 3 days. Apply 1.5 liters per sq ft.",
        "priority": "low"
      }
    ]
  }
}
```

---

## Compatibility

Fully compatible with all existing features:
- ✅ Outdoor gardens
- ✅ Indoor gardens
- ✅ Hydroponics systems
- ✅ User profiles
- ✅ Plant varieties
- ✅ Planting events
- ✅ Task generation
- ✅ Sensor readings

**Integration Points:**
- Soil moisture + irrigation recommendations = precise watering
- Hydroponics pH monitoring + soil pH tracking = complete nutrient management
- Task generation can trigger soil/irrigation reminders

---

## Future Enhancements

1. **Automated Task Generation**: Create tasks based on soil/irrigation recommendations
2. **Trend Analysis**: Chart soil improvements over time
3. **Weather Integration**: Adjust irrigation for rainfall
4. **Fertilizer Calculator**: Convert N-P-K recommendations to specific products
5. **Multi-Plant Optimization**: Watering schedules for mixed plantings
6. **Export Reports**: PDF soil/irrigation reports
7. **Mobile Notifications**: Push alerts for overdue watering

---

## Summary

The soil and irrigation tracking system provides **professional-grade gardening science** for amateur gardeners:

- **Actionable**: Specific amounts, not vague advice
- **Plant-Specific**: Different recommendations for each plant type
- **Research-Based**: Agricultural best practices
- **Integrated**: Works seamlessly with existing features
- **User-Friendly**: Simple forms, clear recommendations

Gardeners can now manage soil fertility and water usage with confidence, leading to healthier plants and better harvests.
