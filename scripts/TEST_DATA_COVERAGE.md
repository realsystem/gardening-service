# Test Data Coverage

This document describes the comprehensive test data created by `setup_test_data.sh` and which features it demonstrates.

## Overview

The script creates a complete gardening system with realistic data that showcases all major features of the application.

## Features Covered

### ✅ Land Management
- **1 Land Parcel**: Main Property (32×25 ft)
- **Configurable Size**: Set via `LAND_WIDTH` and `LAND_HEIGHT` environment variables
- **Grid-Based Layout**: Demonstrates snap-to-grid positioning (0.1 unit precision)

### ✅ Garden Management
- **5 Gardens** with diverse configurations:
  - **Vegetable Garden** (Outdoor, Loam, Full Sun) - 14×10 ft
  - **Herb Garden** (Outdoor, Sandy, Full Sun) - 14×10 ft
  - **Flower Garden** (Outdoor, Clay, Partial Sun) - 30×11 ft
  - **Indoor Herb Garden** (Indoor, Potting Mix, Partial Sun)
  - **Hydroponic Greens** (Indoor, NFT System, Artificial Light)
- Demonstrates all garden types: outdoor, indoor, hydroponic
- Various soil types and sun exposure categories

### ✅ Tree Shading & Sun-Path Visualization
- **5 Trees** strategically placed to demonstrate sun exposure effects:

  1. **Mature Oak** (18 ft tall, 4.5 ft radius)
     - Position: South of Vegetable Garden
     - Demonstrates: **Heavy winter shading** effect
     - Shadow length: ~31 ft in winter (30° sun angle)

  2. **Red Maple** (12 ft tall, 3 ft radius)
     - Position: East of Herb Garden
     - Demonstrates: **Minimal shading** (east-west position)

  3. **White Pine** (22 ft tall, 3.5 ft radius)
     - Position: North of Flower Garden
     - Demonstrates: **Zero shading** (shadows cast away in NH)
     - Validates hemisphere-aware shadow calculations

  4. **Ornamental Cherry** (8 ft tall, 2 ft radius)
     - Position: Southeast corner
     - Demonstrates: **Small shadows** from short trees

  5. **Sugar Maple** (15 ft tall, 3.5 ft radius)
     - Position: Between Vegetable and Flower Gardens
     - Demonstrates: **Moderate seasonal shading**

**Sun-Path Features Demonstrated:**
- ☀️ Seasonal shadow projections (Winter/Equinox/Summer)
- 🎨 Garden color-coding by exposure (Green/Orange/Gray)
- 📊 Detailed seasonal sun exposure data per garden
- 🌍 Northern Hemisphere shadow behavior
- ⚠️ Science-based placement warnings

### ✅ Irrigation System
- **2 Water Sources**:
  - City Water (60 L/min)
  - Rain Barrel Collection (20 L/min)

- **2 Irrigation Zones**:
  - Vegetable Zone (Drip, every 3 days, 30 min)
  - Herb & Flower Zone (Drip, every 2 days, 20 min)

- **3 Gardens Assigned to Zones**:
  - Vegetable Garden → Vegetable Zone
  - Herb Garden → Herb & Flower Zone
  - Flower Garden → Herb & Flower Zone

- **22 Watering Events**:
  - Zone-based automated events
  - Manual watering for indoor gardens
  - Hydroponic reservoir maintenance

### ✅ Irrigation Rule Engine (Alerts)
The test data intentionally triggers these irrigation alerts:

1. **FREQ_001 - Watering Too Frequently**
   - Trigger: 7 daily watering events on Herb & Flower Zone
   - Expected: Warning about over-watering

2. **DUR_001 - Short Duration Watering**
   - Trigger: Only 8 minutes per watering session
   - Expected: Warning about insufficient duration

3. **RESPONSE_001 - Low Moisture Despite Watering**
   - Trigger: 3 soil samples with 12% moisture after recent watering
   - Expected: Critical alert about irrigation effectiveness

### ✅ Soil Health Monitoring
- **5 Soil Samples**:
  - 3 low-moisture samples for Herb Garden (triggers alert)
  - 1 healthy sample for Vegetable Garden
  - 1 healthy sample for Flower Garden

- Measurements include:
  - pH levels
  - NPK nutrients (Nitrogen, Phosphorus, Potassium)
  - Moisture percentage
  - Organic matter percentage

### ✅ Planting Events
- **17 Planting Events** across all gardens:

**Vegetable Garden (4 varieties):**
- Cherry Tomatoes (6 plants, 45 days old) - Near harvest
- Bell Peppers (4 plants, 45 days old) - Near harvest
- Romaine Lettuce (12 plants, 20 days old) - Growing
- Slicing Cucumbers (3 plants, 30 days old) - Growing

**Herb Garden (3 varieties):**
- Basil (8 plants, stressed) - Demonstrates health_status tracking
- Cilantro (20 plants, succession planting)
- Mint (3 plants, contained) - Shows container management

**Flower Garden (3 varieties):**
- Marigolds (15 plants) - Pest deterrent
- Zinnias (25 plants) - Pollinator attractors
- Sunflowers (6 plants) - Tall variety

**Indoor Herb Garden (2 varieties):**
- Basil (4 plants)
- Parsley (6 plants)

**Hydroponic Greens (3 varieties):**
- Romaine Lettuce (12 plants)
- Butterhead Lettuce (8 plants)
- Microgreens (100+ seeds, almost ready)

### ✅ Plant Lifecycle Tracking
- Different planting dates: 5, 15, 20, 30, 45 days ago
- Various planting methods: direct sow, transplant
- Health status tracking: healthy, stressed
- Location tracking within gardens
- Harvest readiness detection

### ✅ Layout Grid System
- **Snap-to-Grid**: All gardens positioned with 0.1 unit precision
- **Compact Layout**: Optimized for screen display (32×25 ft)
- **No Overlaps**: Gardens positioned to demonstrate overlap prevention
- **Realistic Spacing**: Margins between gardens for visual clarity

## Not Covered

These features are NOT included in the automated test data (require manual testing):

- ❌ **Seed Batches**: Requires user to create via UI
- ❌ **Care Tasks**: Would need planting event IDs from API response
- ❌ **Sensor Readings**: Indoor gardens don't auto-generate readings
- ❌ **Harvests**: No harvest tracking in automated setup
- ❌ **Tree Species**: Trees created without species data (species_id is nullable)
- ❌ **Admin Features**: Admin role testing requires separate user
- ❌ **Export/Import**: Requires manual trigger via UI

## Usage

### Basic Setup
```bash
# Use defaults (32×25 land)
./scripts/setup_test_data.sh
```

### Custom Land Size
```bash
# Larger land for more gardens/trees
LAND_WIDTH=50 LAND_HEIGHT=40 ./scripts/setup_test_data.sh
```

### Custom User
```bash
# Use different test account
TEST_EMAIL=demo@example.com TEST_PASSWORD=demo123 ./scripts/setup_test_data.sh
```

## Verification

After running the script, verify features in the UI:

1. **Land Layout** (http://localhost:3000/layout)
   - See 3 gardens positioned on land
   - Enable "Show Seasonal Shadows" toggle
   - Select Winter/Equinox/Summer seasons
   - Click gardens to view sun exposure details

2. **Irrigation Dashboard** (http://localhost:3000/irrigation)
   - View 2 zones with assigned gardens
   - Check zone watering history
   - See 3 triggered alerts (FREQ_001, DUR_001, RESPONSE_001)

3. **Gardens List** (http://localhost:3000/gardens)
   - View 5 gardens with different types
   - Check planting events and health status

4. **Soil Health** (http://localhost:3000/soil-samples)
   - View samples with varying moisture levels
   - See low-moisture alert for Herb Garden

## API Testing

Use the generated token to test API endpoints:

```bash
# Save token from script output
TOKEN="<your-token-here>"

# Test sun exposure endpoint
curl -s http://localhost:8080/gardens/1/sun-exposure \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Test tree shadow extent
curl -s "http://localhost:8080/trees/1/shadow-extent?latitude=40.0" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Test irrigation insights
curl -s http://localhost:8080/irrigation-system/insights \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## Troubleshooting

If trees don't appear:
- Check if `/trees` endpoint exists: `curl -I http://localhost:8080/trees -H "Authorization: Bearer $TOKEN"`
- Verify trees are enabled in the API
- Check Docker logs: `docker compose logs api | grep tree`

If irrigation alerts don't show:
- Wait 30 seconds for rule engine to process
- Check insights endpoint directly (command above)
- Verify watering events were created

## Reset Data

To start fresh:
```bash
./scripts/reset-db.sh  # Clears entire database
./scripts/setup_test_user.sh  # Recreate test user
./scripts/setup_test_data.sh  # Recreate test data
```

Or just re-run setup_test_data.sh (it's idempotent and clears existing data).
