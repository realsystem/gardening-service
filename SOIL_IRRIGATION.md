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

### Soil Rules (`app/rules/soil_rules.py`)

**Plant-Specific Ranges:**
- Tomato: pH 6.0-6.8, N 20-50 ppm, P 25-75 ppm, K 150-250 ppm
- Lettuce: pH 6.0-7.0, N 30-60 ppm, P 20-60 ppm, K 120-200 ppm
- Default: pH 6.0-7.0, N 20-60 ppm, P 25-75 ppm, K 120-250 ppm

**Recommendation Logic:**
- Calculate deficit/excess from optimal range
- Determine status: optimal, low, high, critical
- Generate specific amendment amounts
- Assign priority based on severity

**Amendment Calculations:**
- pH: ~5 lbs lime per pH unit per 100 sq ft
- pH: ~1.5 lbs sulfur per pH unit per 100 sq ft
- Nitrogen: Compost, blood meal, fish emulsion rates
- Phosphorus: Bone meal, rock phosphate rates
- Potassium: Greensand, kelp meal, wood ash rates

### Irrigation Rules (`app/rules/irrigation_rules.py`)

**Watering Frequency:**
- Compare days since last watering to plant requirements
- Account for soil moisture if available
- Generate priority based on overdue days

**Seasonal Adjustments:**
- Summer (Jun-Aug): 1.3x water needs
- Winter (Dec-Feb): 0.7x water needs
- Spring/Fall: 1.0x baseline

**Status Determination:**
- `on_schedule`: Within ±1 day of recommended frequency
- `overdue`: More than 1 day past due
- `overwatered`: Watered more frequently than recommended
- `no_data`: No irrigation history

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
