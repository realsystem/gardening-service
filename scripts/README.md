# Irrigation System API Test Scripts

This directory contains test scripts for validating the irrigation system API endpoints.

## Prerequisites

1. **API must be running**: `docker-compose up -d`
2. **User account must exist**: Create a test user or use existing credentials
3. **Python 3**: Required for JSON formatting (optional, but recommended)

## Quick Start

### Recommended: End-to-End Test

Run the complete automated test workflow:

```bash
./scripts/test_irrigation_e2e.sh
```

This will:
1. Clean up any existing test user
2. Create a fresh test user
3. Run quick smoke test
4. Optionally run full test suite
5. Provide cleanup instructions

## Test Scripts

### 0. Setup Test User: `setup_test_user.sh`

Creates a test user account for running API tests.

**Usage:**
```bash
./scripts/setup_test_user.sh
```

**Default credentials:**
- Email: `test@example.com`
- Password: `password123`

**Custom credentials:**
```bash
TEST_EMAIL="custom@test.com" TEST_PASSWORD="custom123" ./scripts/setup_test_user.sh
```

### 0b. Setup Comprehensive Test Data: `setup_test_data.sh`

Creates a complete test environment with gardens, land layout, irrigation system, and soil samples designed to trigger alerts.

**Idempotent:** This script can be run multiple times safely. It automatically cleans up existing resources before creating new ones.

**Usage:**
```bash
./scripts/setup_test_data.sh
```

**Custom land size:**
```bash
# Default: 32x25 ft (very compact, screen-friendly)
LAND_WIDTH=32 LAND_HEIGHT=25 ./scripts/setup_test_data.sh

# Medium: 45x35 ft (comfortable margins)
LAND_WIDTH=45 LAND_HEIGHT=35 ./scripts/setup_test_data.sh

# Larger: 60x45 ft (spacious layout)
LAND_WIDTH=60 LAND_HEIGHT=45 ./scripts/setup_test_data.sh
```

**What it creates:**
- 1 Land parcel (default 32x25 ft, configurable) with positioned gardens
- 5 Gardens:
  - Vegetable Garden (Outdoor, Loam soil) - 14x10 ft
  - Herb Garden (Outdoor, Sandy soil) - 14x10 ft - **triggers alerts**
  - Flower Garden (Outdoor, Clay soil) - 30x11 ft
  - Indoor Herb Garden (not positioned on land)
  - Hydroponic Greens (NFT system, not positioned on land)
- 2 Water sources (City water + Rain barrel)
- 2 Irrigation zones with assigned gardens
- 17 Planting events with diverse varieties:
  - Vegetable Garden: Cherry Tomatoes, Bell Peppers, Romaine Lettuce, Slicing Cucumbers
  - Herb Garden: Basil (stressed), Cilantro, Mint
  - Flower Garden: Marigolds, Zinnias, Sunflowers
  - Indoor Herb Garden: Basil, Parsley
  - Hydroponic Greens: Romaine, Butterhead Lettuce, Microgreens
- 22 Watering/irrigation events (zone-based + manual + hydroponic maintenance)
- 5 Soil samples (including low moisture samples)

**Garden layout:**
- Compact arrangement filling most of the land area
- 2 gardens in top row: Vegetable (1,1) and Herb (17,1)
- 1 wide garden in bottom row: Flower (1,13) spanning full width
- Default 32x25 land fits well on typical screens

**Alerts triggered:**
- ⚠️ FREQ_001: Watering too frequently (daily watering on Herb & Flower Zone)
- ⚠️ DUR_001: Short duration watering (8 minutes instead of 20-30)
- 🔴 RESPONSE_001: Low soil moisture despite watering (Herb Garden at 12%)

**Prerequisites:**
- Test user must exist (run `./scripts/setup_test_user.sh` first)
- Plant varieties must be loaded in database (auto-loaded if missing)

**Duration:** ~5-8 seconds

### 1. Full Test Suite: `test_irrigation_api.sh`

Comprehensive test covering all irrigation system endpoints.

**Usage:**
```bash
./scripts/test_irrigation_api.sh
```

**With custom credentials:**
```bash
TEST_EMAIL="your@email.com" TEST_PASSWORD="yourpassword" ./scripts/test_irrigation_api.sh
```

**What it tests:**
- ✅ User authentication
- ✅ Create water sources
- ✅ Create irrigation zones (with and without sources)
- ✅ Record watering events
- ✅ List all resources (sources, zones, events)
- ✅ Get detailed zone information
- ✅ Get irrigation overview
- ✅ Get irrigation insights (rule engine)
- ✅ Update zone configuration
- ✅ Assign gardens to zones

**Expected outcomes:**
- Creates 1-2 water sources
- Creates 2 irrigation zones
- Records 6 watering events (designed to trigger rules)
- Triggers FREQ_001 (watering too frequently - every day)
- Triggers DUR_001 (short duration watering - 8 minutes)

### 2. Quick Smoke Test: `quick_test_irrigation.sh`

Fast validation of basic functionality.

**Usage:**
```bash
./scripts/quick_test_irrigation.sh
```

**What it tests:**
- ✅ Authentication
- ✅ Create source
- ✅ Create zone
- ✅ Record event
- ✅ Get overview
- ✅ Get insights

**Duration:** ~5 seconds

### 3. Cleanup Test User: `cleanup_test_user.sh`

Deletes the test user via API endpoint (interactive with confirmation).

**Usage:**
```bash
./scripts/cleanup_test_user.sh
```

**How it works:**
- ✅ Uses DELETE /users/me endpoint (single API call)
- ✅ No direct database access required
- ✅ Respects application business logic and CASCADE deletes
- ✅ Clean and portable

**What it deletes:**
- User account and ALL associated data:
  - Gardens, planting events, care tasks
  - Seed batches, soil samples
  - Irrigation zones, sources, and watering events
  - Sensor readings, germination events, lands

**Custom user:**
```bash
TEST_EMAIL="custom@test.com" TEST_PASSWORD="pass123" ./scripts/cleanup_test_user.sh
```

### 4. Automated Cleanup: `cleanup_test_user_auto.sh`

Same as above but without confirmation prompt (for automated workflows).

**Usage:**
```bash
./scripts/cleanup_test_user_auto.sh
```

### 5. End-to-End Test: `test_irrigation_e2e.sh`

Complete automated test workflow with setup and cleanup.

**Usage:**
```bash
./scripts/test_irrigation_e2e.sh
```

**Workflow:**
1. Cleans up existing test user (auto)
2. Creates fresh test user
3. Runs quick smoke test
4. Asks if you want to run full test suite
5. Provides cleanup instructions

## Manual Testing with curl

### 1. Login and Get Token

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token: $TOKEN"
```

### 2. Create Water Source

```bash
curl -X POST http://localhost:8080/irrigation-system/sources \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "City Water",
    "source_type": "city",
    "flow_capacity_lpm": 50.0
  }'
```

### 3. Create Irrigation Zone

```bash
curl -X POST http://localhost:8080/irrigation-system/zones \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vegetable Garden",
    "delivery_type": "drip",
    "schedule": {
      "frequency_days": 3,
      "duration_minutes": 30
    }
  }'
```

### 4. Record Watering Event

```bash
curl -X POST http://localhost:8080/irrigation-system/events \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "irrigation_zone_id": 1,
    "watered_at": "2026-01-30T12:00:00.000Z",
    "duration_minutes": 30,
    "is_manual": true
  }'
```

### 5. Get Irrigation Overview

```bash
curl -X GET http://localhost:8080/irrigation-system/overview \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 6. Get Irrigation Insights

```bash
curl -X GET http://localhost:8080/irrigation-system/insights \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 7. List Watering Events for Zone

```bash
curl -X GET "http://localhost:8080/irrigation-system/events?zone_id=1&days=30" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 8. Get Zone Details

```bash
curl -X GET http://localhost:8080/irrigation-system/zones/1/details \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 9. Update Zone

```bash
curl -X PATCH http://localhost:8080/irrigation-system/zones/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule": {
      "frequency_days": 4,
      "duration_minutes": 45
    }
  }'
```

### 10. Assign Garden to Zone

```bash
curl -X POST "http://localhost:8080/irrigation-system/gardens/1/assign-zone?zone_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

## Understanding the Rule Engine

The irrigation insights endpoint analyzes watering patterns and triggers rules:

### FREQ_001 - Watering Too Frequently
- **Triggers when:** Average interval < 2 days
- **Severity:** Warning
- **Fix:** Water deeper, less often (promotes root development)

### FREQ_002 - Infrequent Watering
- **Triggers when:** Average interval > 10 days
- **Severity:** Info
- **Fix:** Verify soil moisture, adjust schedule if needed

### DUR_001 - Frequent Shallow Watering
- **Triggers when:** >50% of waterings < 10 minutes
- **Severity:** Warning
- **Fix:** Increase duration to 20-30 minutes for deep watering

### CONFLICT_001 - Mixed Soil Types
- **Triggers when:** Sandy and clay soils in same zone
- **Severity:** Warning
- **Fix:** Separate zones or manually adjust watering

### RESPONSE_001 - Low Moisture Despite Watering
- **Triggers when:** Soil moisture < 20% with recent watering
- **Severity:** Critical
- **Fix:** Check for runoff, compaction, or system issues

## Troubleshooting

### "Login failed"
- Verify API is running: `docker-compose ps`
- Check credentials match an existing user
- Create user via frontend or API

### "Failed to create X"
- Check API logs: `docker-compose logs api --tail=50`
- Verify token is valid
- Check request body format

### "No insights generated"
- Record multiple watering events over several days
- Insights require historical data to analyze patterns
- Try the full test script which creates pattern-triggering data

## API Documentation

Full API documentation available at:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
