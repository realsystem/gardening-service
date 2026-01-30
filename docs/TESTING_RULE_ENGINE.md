# Testing the Science-Based Rule Engine

This guide explains how to test the newly implemented Science-Based Gardening Rule Engine.

## Quick Start - Automated Testing

The easiest way to test the rule engine is to run the automated test script:

```bash
# 1. Update credentials in test_rule_engine.py (lines 10-11)
#    TEST_EMAIL = "your@email.com"
#    TEST_PASSWORD = "yourpassword"

# 2. Run the test script
python3 test_rule_engine.py
```

This script will:
- Create a test garden
- Add soil samples and irrigation events that trigger various rules
- Display the triggered rules and their details
- Show you the API responses

## Manual Testing in the UI

1. **Login to the application**
   - Visit http://localhost:3000
   - Login with your credentials

2. **Create a garden**
   - Click "Create Garden" button
   - Fill in garden details
   - Submit

3. **Add soil samples that trigger rules**

   To test different rules, add soil samples with these values:

   **Under-watering (WATER_001 - CRITICAL)**
   - Moisture: 8% (very dry)
   - pH: 6.5

   **Over-watering (WATER_002 - CRITICAL)**
   - Moisture: 85% (saturated)
   - pH: 6.5

   **pH Imbalance (SOIL_001 - CRITICAL)**
   - pH: 4.5 (too acidic for most plants)
   - Moisture: 45%

   **Nitrogen Deficiency (SOIL_002 - CRITICAL)**
   - Nitrogen: 5 ppm (very low)
   - pH: 6.5
   - Moisture: 45%

   **Salinity Stress (SOIL_003 - CRITICAL)**
   - pH: 6.5
   - Moisture: 45%
   - (Note: You'll need to add EC/salinity field support or test via API)

4. **View the Scientific Insights card**
   - Scroll down to the "🧪 Scientific Insights" card
   - You'll see:
     - Summary counts (Critical, Warning, Info)
     - List of triggered rules with color-coded severity
     - Click any rule to expand and see:
       - Scientific rationale with biological explanation
       - Recommended actions
       - Academic references

## Testing via API (curl)

### 1. Login and get token
```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your@email.com&password=yourpassword"
```

Save the `access_token` from the response.

### 2. Create a garden
```bash
TOKEN="your_access_token_here"

curl -X POST http://localhost:8080/gardens/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Garden",
    "garden_type": "outdoor"
  }'
```

Save the garden `id` from the response.

### 3. Add problematic soil sample
```bash
GARDEN_ID=1  # Use your garden ID

curl -X POST http://localhost:8080/soil-samples/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": $GARDEN_ID,
    \"ph\": 4.5,
    \"moisture_percent\": 8.0,
    \"nitrogen_ppm\": 5.0,
    \"date_collected\": \"$(date +%Y-%m-%d)\"
  }"
```

### 4. Get rule insights
```bash
curl -X GET http://localhost:8080/rule-insights/garden/$GARDEN_ID \
  -H "Authorization: Bearer $TOKEN" | jq
```

This will return a JSON response like:
```json
{
  "garden_id": 1,
  "garden_name": "Test Garden",
  "evaluation_time": "2026-01-29T19:15:00Z",
  "triggered_rules": [
    {
      "rule_id": "WATER_001",
      "category": "water_stress",
      "title": "Under-Watering Detected",
      "severity": "critical",
      "confidence": 0.95,
      "explanation": "Soil moisture is critically low at 8.0%...",
      "scientific_rationale": "Plant cells maintain turgor pressure through...",
      "recommended_action": "Water immediately. Increase irrigation frequency...",
      "measured_value": 8.0,
      "optimal_range": "40-60%",
      "references": [
        "Boyer, J.S. (1982). Plant productivity and environment...",
        ...
      ]
    },
    ...
  ],
  "rules_by_severity": {
    "critical": 3,
    "warning": 1,
    "info": 0
  }
}
```

## What Rules Are Available?

The system includes 11 rules across 5 categories:

### Water Stress (3 rules)
- **WATER_001**: Under-watering detection (moisture <15%)
- **WATER_002**: Over-watering detection (moisture >70%)
- **WATER_003**: Excessive irrigation frequency (>10 events/week)

### Soil Chemistry (3 rules)
- **SOIL_001**: pH imbalance detection
- **SOIL_002**: Nitrogen deficiency (N <10 ppm)
- **SOIL_003**: Salinity stress (EC >2.0 dS/m)

### Temperature Stress (2 rules)
- **TEMP_001**: Cold stress and frost risk
- **TEMP_002**: Heat stress (temp >95°F or >15°F above plant max)

### Light Stress (2 rules)
- **LIGHT_001**: Etiolation risk (indoor plants <6h light)
- **LIGHT_002**: Photoinhibition (>18h artificial light)

### Growth Stage (1 rule)
- **GROWTH_001**: Harvest readiness (days >= days_to_harvest)

## Understanding Severity Levels

- **🚨 CRITICAL** (Red): Immediate action required to prevent crop failure
- **⚠️ WARNING** (Orange): Suboptimal conditions requiring attention
- **ℹ️ INFO** (Blue): Informational alerts (e.g., harvest ready)

## Running Unit Tests

The rule engine has 57 comprehensive unit tests:

```bash
cd /Users/segorov/Projects/t/gardening-service

# Run all rule engine tests
docker-compose exec api pytest tests/test_rule_engine.py -v

# Run tests for a specific rule category
docker-compose exec api pytest tests/test_rule_engine.py::TestUnderWateringRule -v

# Run with coverage
docker-compose exec api pytest tests/test_rule_engine.py --cov=app.rules
```

## Performance Testing

The rule engine is designed to evaluate all rules in <100ms. To verify:

```bash
# The engine logs warnings if evaluation exceeds 100ms
docker-compose logs api | grep "Rule evaluation slow"
```

## Troubleshooting

### No rules are triggering
- Verify you've added soil samples, irrigation events, or sensor readings
- Check that the data values are outside optimal ranges
- View API logs: `docker-compose logs api`

### Dashboard not showing insights
- Check browser console for errors (F12)
- Verify the garden has data (soil samples, irrigation, etc.)
- Check API response: `curl http://localhost:8080/rule-insights/garden/{id}`

### Rules triggering incorrectly
- Review the rule implementation in `app/rules/rules_*.py`
- Check the plant-specific thresholds in `app/rules/engine/base.py` (PLANT_REQUIREMENTS)
- Run unit tests to verify rule logic

## Next Steps

After testing:
1. Review [RULE_ENGINE.md](RULE_ENGINE.md) for architecture details
2. Learn how to add new rules (see "Adding New Rules" section)
3. Check [SOIL_IRRIGATION.md](SOIL_IRRIGATION.md) for API documentation
