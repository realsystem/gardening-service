#!/bin/bash

# Setup Comprehensive Test Data
# Creates gardens, land layout, irrigation system, and soil samples
# Includes data that triggers irrigation alerts

set -e

# Configuration
API_URL="http://localhost:8080"
EMAIL="${TEST_EMAIL:-test@example.com}"
PASSWORD="${TEST_PASSWORD:-password123}"

echo "================================================"
echo "Setting Up Comprehensive Test Data"
echo "================================================"
echo "Email: $EMAIL"
echo ""

# Step 1: Login
echo "Step 1: Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/users/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"${EMAIL}\", \"password\": \"${PASSWORD}\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed - please create test user first"
    echo "Run: ./scripts/setup_test_user.sh"
    exit 1
fi

echo "✓ Login successful"
echo ""

# Step 2: Create Land
echo "Step 2: Creating land parcel..."
LAND_RESPONSE=$(curl -s -X POST "${API_URL}/lands" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Property",
    "width_feet": 100,
    "length_feet": 80,
    "notes": "Primary gardening area with indoor and outdoor spaces"
  }')

LAND_ID=$(echo "$LAND_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ Land created (ID: $LAND_ID)"
echo ""

# Step 3: Create Gardens
echo "Step 3: Creating gardens..."

# Garden 1: Vegetable Garden (Outdoor)
GARDEN1_RESPONSE=$(curl -s -X POST "${API_URL}/gardens" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vegetable Garden",
    "garden_type": "outdoor",
    "location": "backyard",
    "soil_type": "loam",
    "sun_exposure": "full_sun",
    "notes": "Main vegetable production area"
  }')
GARDEN1_ID=$(echo "$GARDEN1_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ Vegetable Garden created (ID: $GARDEN1_ID)"

# Garden 2: Herb Garden (Outdoor)
GARDEN2_RESPONSE=$(curl -s -X POST "${API_URL}/gardens" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Herb Garden",
    "garden_type": "outdoor",
    "location": "near kitchen",
    "soil_type": "sandy",
    "sun_exposure": "full_sun",
    "notes": "Culinary herbs and aromatics"
  }')
GARDEN2_ID=$(echo "$GARDEN2_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ Herb Garden created (ID: $GARDEN2_ID)"

# Garden 3: Flower Garden (Outdoor)
GARDEN3_RESPONSE=$(curl -s -X POST "${API_URL}/gardens" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Flower Garden",
    "garden_type": "outdoor",
    "location": "front yard",
    "soil_type": "clay",
    "sun_exposure": "partial_sun",
    "notes": "Ornamental flowers and perennials"
  }')
GARDEN3_ID=$(echo "$GARDEN3_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ Flower Garden created (ID: $GARDEN3_ID)"

# Garden 4: Indoor Herbs (Indoor)
GARDEN4_RESPONSE=$(curl -s -X POST "${API_URL}/gardens" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Indoor Herb Garden",
    "garden_type": "indoor",
    "location": "kitchen window",
    "soil_type": "potting_mix",
    "sun_exposure": "partial_sun",
    "notes": "Year-round fresh herbs"
  }')
GARDEN4_ID=$(echo "$GARDEN4_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ Indoor Herb Garden created (ID: $GARDEN4_ID)"

# Garden 5: Hydroponic Greens (Indoor Hydroponics)
GARDEN5_RESPONSE=$(curl -s -X POST "${API_URL}/gardens" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hydroponic Greens",
    "garden_type": "indoor",
    "location": "basement",
    "hydroponic_system_type": "nft",
    "sun_exposure": "artificial_light",
    "notes": "NFT system for lettuce and microgreens"
  }')
GARDEN5_ID=$(echo "$GARDEN5_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ Hydroponic Greens created (ID: $GARDEN5_ID)"
echo ""

# Step 4: Place Gardens on Land
echo "Step 4: Positioning gardens on land..."

curl -s -X PATCH "${API_URL}/gardens/${GARDEN1_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"land_id\": ${LAND_ID}, \"position_x_feet\": 10, \"position_y_feet\": 10, \"width_feet\": 30, \"length_feet\": 20}" > /dev/null
echo "✓ Vegetable Garden positioned (10, 10) - 30x20 ft"

curl -s -X PATCH "${API_URL}/gardens/${GARDEN2_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"land_id\": ${LAND_ID}, \"position_x_feet\": 45, \"position_y_feet\": 10, \"width_feet\": 15, \"length_feet\": 10}" > /dev/null
echo "✓ Herb Garden positioned (45, 10) - 15x10 ft"

curl -s -X PATCH "${API_URL}/gardens/${GARDEN3_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"land_id\": ${LAND_ID}, \"position_x_feet\": 10, \"position_y_feet\": 35, \"width_feet\": 40, \"length_feet\": 15}" > /dev/null
echo "✓ Flower Garden positioned (10, 35) - 40x15 ft"
echo ""

# Step 5: Create Irrigation Sources
echo "Step 5: Creating irrigation sources..."

SOURCE1_RESPONSE=$(curl -s -X POST "${API_URL}/irrigation-system/sources" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "City Water - Main Line",
    "source_type": "city",
    "flow_capacity_lpm": 60,
    "notes": "Main water supply"
  }')
SOURCE1_ID=$(echo "$SOURCE1_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ City water source created (ID: $SOURCE1_ID, 60 L/min)"

SOURCE2_RESPONSE=$(curl -s -X POST "${API_URL}/irrigation-system/sources" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rain Barrel Collection",
    "source_type": "well",
    "flow_capacity_lpm": 20,
    "notes": "Rainwater collection system"
  }')
SOURCE2_ID=$(echo "$SOURCE2_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ Rain barrel source created (ID: $SOURCE2_ID, 20 L/min)"
echo ""

# Step 6: Create Irrigation Zones
echo "Step 6: Creating irrigation zones..."

ZONE1_RESPONSE=$(curl -s -X POST "${API_URL}/irrigation-system/zones" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Vegetable Zone\",
    \"delivery_type\": \"drip\",
    \"water_source_id\": ${SOURCE1_ID},
    \"schedule\": {
      \"frequency_days\": 3,
      \"duration_minutes\": 30
    },
    \"notes\": \"Drip irrigation for vegetables\"
  }")
ZONE1_ID=$(echo "$ZONE1_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ Vegetable Zone created (ID: $ZONE1_ID) - Drip, every 3 days, 30 min"

ZONE2_RESPONSE=$(curl -s -X POST "${API_URL}/irrigation-system/zones" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Herb & Flower Zone\",
    \"delivery_type\": \"drip\",
    \"water_source_id\": ${SOURCE2_ID},
    \"schedule\": {
      \"frequency_days\": 2,
      \"duration_minutes\": 20
    },
    \"notes\": \"Combined zone for herbs and flowers\"
  }")
ZONE2_ID=$(echo "$ZONE2_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ Herb & Flower Zone created (ID: $ZONE2_ID) - Drip, every 2 days, 20 min"
echo ""

# Step 7: Assign Gardens to Zones
echo "Step 7: Assigning gardens to irrigation zones..."

curl -s -X POST "${API_URL}/irrigation-system/gardens/${GARDEN1_ID}/assign-zone?zone_id=${ZONE1_ID}" \
  -H "Authorization: Bearer ${TOKEN}" > /dev/null
echo "✓ Vegetable Garden → Vegetable Zone"

curl -s -X POST "${API_URL}/irrigation-system/gardens/${GARDEN2_ID}/assign-zone?zone_id=${ZONE2_ID}" \
  -H "Authorization: Bearer ${TOKEN}" > /dev/null
echo "✓ Herb Garden → Herb & Flower Zone"

curl -s -X POST "${API_URL}/irrigation-system/gardens/${GARDEN3_ID}/assign-zone?zone_id=${ZONE2_ID}" \
  -H "Authorization: Bearer ${TOKEN}" > /dev/null
echo "✓ Flower Garden → Herb & Flower Zone"
echo ""

# Step 8: Create Watering Events (to trigger frequency alert)
echo "Step 8: Creating watering history (will trigger FREQ_001 alert)..."

# Create daily watering events for the past 7 days on Herb & Flower Zone
# This will trigger FREQ_001 (watering too frequently)
for i in {0..6}; do
  WATERED_AT=$(date -u -v-${i}d +"%Y-%m-%dT12:00:00.000Z" 2>/dev/null || date -u -d "${i} days ago" +"%Y-%m-%dT12:00:00.000Z")
  curl -s -X POST "${API_URL}/irrigation-system/events" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{
      \"irrigation_zone_id\": ${ZONE2_ID},
      \"watered_at\": \"${WATERED_AT}\",
      \"duration_minutes\": 8,
      \"is_manual\": false
    }" > /dev/null
done
echo "✓ Created 7 daily watering events (8 min each) - will trigger FREQ_001 & DUR_001"

# Create proper watering events for Vegetable Zone
curl -s -X POST "${API_URL}/irrigation-system/events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"irrigation_zone_id\": ${ZONE1_ID},
    \"watered_at\": \"$(date -u -v-3d +"%Y-%m-%dT12:00:00.000Z" 2>/dev/null || date -u -d '3 days ago' +"%Y-%m-%dT12:00:00.000Z")\",
    \"duration_minutes\": 30,
    \"is_manual\": false
  }" > /dev/null
echo "✓ Created proper watering event for Vegetable Zone"
echo ""

# Step 9: Add Soil Samples (with low moisture to trigger alert)
echo "Step 9: Creating soil samples (will trigger RESPONSE_001 alert)..."

# Create 3 low-moisture samples for Herb Garden to trigger RESPONSE_001
for i in {0..2}; do
  SAMPLE_DATE=$(date -u -v-${i}d +"%Y-%m-%d" 2>/dev/null || date -u -d "${i} days ago" +"%Y-%m-%d")
  curl -s -X POST "${API_URL}/soil-samples" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{
      \"garden_id\": ${GARDEN2_ID},
      \"ph\": 6.8,
      \"nitrogen_ppm\": 45,
      \"phosphorus_ppm\": 30,
      \"potassium_ppm\": 150,
      \"moisture_percent\": 12,
      \"date_collected\": \"${SAMPLE_DATE}\",
      \"notes\": \"Low moisture despite recent watering\"
    }" > /dev/null
done
echo "✓ Created 3 soil samples for Herb Garden (12% moisture) - will trigger RESPONSE_001"

# Create normal soil samples for other gardens
curl -s -X POST "${API_URL}/soil-samples" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN1_ID},
    \"ph\": 6.5,
    \"nitrogen_ppm\": 60,
    \"phosphorus_ppm\": 40,
    \"potassium_ppm\": 200,
    \"moisture_percent\": 45,
    \"organic_matter_percent\": 5.2,
    \"date_collected\": \"$(date -u +"%Y-%m-%d")\",
    \"notes\": \"Good soil health\"
  }" > /dev/null
echo "✓ Created soil sample for Vegetable Garden (healthy)"

curl -s -X POST "${API_URL}/soil-samples" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN3_ID},
    \"ph\": 7.2,
    \"nitrogen_ppm\": 35,
    \"phosphorus_ppm\": 25,
    \"potassium_ppm\": 180,
    \"moisture_percent\": 38,
    \"organic_matter_percent\": 3.8,
    \"date_collected\": \"$(date -u +"%Y-%m-%d")\",
    \"notes\": \"Clay soil - good drainage needed\"
  }" > /dev/null
echo "✓ Created soil sample for Flower Garden (healthy)"
echo ""

# Summary
echo "================================================"
echo "Test Data Setup Complete!"
echo "================================================"
echo ""
echo "Created Resources:"
echo "  • 1 Land: Main Property (100x80 ft)"
echo "  • 5 Gardens:"
echo "    - Vegetable Garden (Outdoor, Loam) - ID: $GARDEN1_ID"
echo "    - Herb Garden (Outdoor, Sandy) - ID: $GARDEN2_ID"
echo "    - Flower Garden (Outdoor, Clay) - ID: $GARDEN3_ID"
echo "    - Indoor Herb Garden (Indoor) - ID: $GARDEN4_ID"
echo "    - Hydroponic Greens (Indoor/Hydro) - ID: $GARDEN5_ID"
echo "  • 2 Water Sources:"
echo "    - City Water - ID: $SOURCE1_ID"
echo "    - Rain Barrel - ID: $SOURCE2_ID"
echo "  • 2 Irrigation Zones:"
echo "    - Vegetable Zone - ID: $ZONE1_ID"
echo "    - Herb & Flower Zone - ID: $ZONE2_ID"
echo "  • 8 Watering Events"
echo "  • 5 Soil Samples"
echo ""
echo "Expected Irrigation Alerts:"
echo "  ⚠️  FREQ_001: Watering too frequently (Herb & Flower Zone - daily watering)"
echo "  ⚠️  DUR_001: Short duration watering (Herb & Flower Zone - 8 min)"
echo "  🔴 RESPONSE_001: Low moisture despite watering (Herb Garden - 12% moisture)"
echo ""
echo "View in app: http://localhost:3000"
echo "Check irrigation insights:"
echo "  curl -s http://localhost:8080/irrigation-system/insights \\"
echo "    -H \"Authorization: Bearer $TOKEN\" | python3 -m json.tool"
echo ""
