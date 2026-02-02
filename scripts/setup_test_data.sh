#!/bin/bash

# Setup Comprehensive Test Data
# Creates gardens, land layout, trees, soil samples, and plantings
# Demonstrates companion planting analysis and nutrient optimization

set -e

# Configuration
API_URL="http://localhost:8080"
EMAIL="${TEST_EMAIL:-test@example.com}"
PASSWORD="${TEST_PASSWORD:-password123}"

echo "================================================"
echo "Setting Up Comprehensive Test Data"
echo "================================================"
echo "Email: $EMAIL"
echo "Land Size: ${LAND_WIDTH:-32}x${LAND_HEIGHT:-25} ft (set LAND_WIDTH/LAND_HEIGHT to customize)"
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

# Step 2: Cleanup existing resources (idempotent)
echo "Step 2: Cleaning up existing resources..."

# Get and delete all gardens
GARDENS=$(curl -s -X GET "${API_URL}/gardens" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -c "import sys, json; data=json.load(sys.stdin); print(' '.join([str(g['id']) for g in data]))" 2>/dev/null || echo "")
if [ ! -z "$GARDENS" ]; then
  for GARDEN_ID in $GARDENS; do
    curl -s -X DELETE "${API_URL}/gardens/${GARDEN_ID}" \
      -H "Authorization: Bearer ${TOKEN}" > /dev/null 2>&1
  done
  echo "✓ Deleted $(echo $GARDENS | wc -w | tr -d ' ') garden(s)"
fi

# Get and delete all lands
LANDS=$(curl -s -X GET "${API_URL}/lands" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -c "import sys, json; data=json.load(sys.stdin); print(' '.join([str(l['id']) for l in data]))" 2>/dev/null || echo "")
if [ ! -z "$LANDS" ]; then
  for LAND_ID_DEL in $LANDS; do
    curl -s -X DELETE "${API_URL}/lands/${LAND_ID_DEL}" \
      -H "Authorization: Bearer ${TOKEN}" > /dev/null 2>&1
  done
  echo "✓ Deleted $(echo $LANDS | wc -w | tr -d ' ') land(s)"
fi

# Get and delete all trees
TREES=$(curl -s -X GET "${API_URL}/trees" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -c "import sys, json; data=json.load(sys.stdin); print(' '.join([str(t['id']) for t in data]))" 2>/dev/null || echo "")
if [ ! -z "$TREES" ]; then
  for TREE_ID in $TREES; do
    curl -s -X DELETE "${API_URL}/trees/${TREE_ID}" \
      -H "Authorization: Bearer ${TOKEN}" > /dev/null 2>&1
  done
  echo "✓ Deleted $(echo $TREES | wc -w | tr -d ' ') tree(s)"
fi

echo "✓ Cleanup complete - ready for fresh setup"
echo ""

# Step 3: Create Land
echo "Step 3: Creating land parcel..."
# Configurable land size (very compact for screen display)
LAND_WIDTH="${LAND_WIDTH:-32}"
LAND_HEIGHT="${LAND_HEIGHT:-25}"

LAND_RESPONSE=$(curl -s -X POST "${API_URL}/lands" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Main Property\",
    \"width\": ${LAND_WIDTH},
    \"height\": ${LAND_HEIGHT}
  }")

LAND_ID=$(echo "$LAND_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null || echo "$LAND_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ Land created (ID: $LAND_ID) - ${LAND_WIDTH}x${LAND_HEIGHT} ft"
echo ""

# Step 4: Create Gardens
echo "Step 4: Creating gardens..."

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
    "is_hydroponic": true,
    "hydro_system_type": "nft",
    "reservoir_size_liters": 50,
    "sun_exposure": "artificial_light",
    "notes": "NFT system for lettuce and microgreens - demonstrates low EC for leafy greens"
  }')
GARDEN5_ID=$(echo "$GARDEN5_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ Hydroponic Greens created (ID: $GARDEN5_ID) - NFT, 50L reservoir"

# Garden 6: Hydroponic Tomatoes (DWC Hydroponics)
GARDEN6_RESPONSE=$(curl -s -X POST "${API_URL}/gardens" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hydroponic Tomatoes",
    "garden_type": "indoor",
    "location": "grow tent",
    "is_hydroponic": true,
    "hydro_system_type": "dwc",
    "reservoir_size_liters": 80,
    "sun_exposure": "artificial_light",
    "notes": "Deep Water Culture for high-nutrient demand fruiting crops"
  }')
GARDEN6_ID=$(echo "$GARDEN6_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ Hydroponic Tomatoes created (ID: $GARDEN6_ID) - DWC, 80L reservoir"

# Garden 7: Container Garden (Fertigation)
GARDEN7_RESPONSE=$(curl -s -X POST "${API_URL}/gardens" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Patio Container Garden",
    "garden_type": "outdoor",
    "location": "patio",
    "is_hydroponic": false,
    "hydro_system_type": "container",
    "soil_type": "potting_mix",
    "reservoir_size_liters": 30,
    "sun_exposure": "full_sun",
    "notes": "Container growing with drip fertigation system"
  }')
GARDEN7_ID=$(echo "$GARDEN7_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ Patio Container Garden created (ID: $GARDEN7_ID) - Container system, 30L reservoir"
echo ""

# Step 5: Place Gardens on Land
echo "Step 5: Positioning gardens on land..."

# Very compact layout for 32x25 land with better margins
PATCH1_RESPONSE=$(curl -s -X PUT "${API_URL}/gardens/${GARDEN1_ID}/layout" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"land_id\": ${LAND_ID}, \"x\": 1, \"y\": 1, \"width\": 14, \"height\": 10}")
echo "✓ Vegetable Garden positioned (1, 1) - 14x10 ft"
if echo "$PATCH1_RESPONSE" | grep -q "error"; then
  echo "  Warning: $PATCH1_RESPONSE"
fi

PATCH2_RESPONSE=$(curl -s -X PUT "${API_URL}/gardens/${GARDEN2_ID}/layout" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"land_id\": ${LAND_ID}, \"x\": 17, \"y\": 1, \"width\": 14, \"height\": 10}")
echo "✓ Herb Garden positioned (17, 1) - 14x10 ft"
if echo "$PATCH2_RESPONSE" | grep -q "error"; then
  echo "  Warning: $PATCH2_RESPONSE"
fi

PATCH3_RESPONSE=$(curl -s -X PUT "${API_URL}/gardens/${GARDEN3_ID}/layout" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"land_id\": ${LAND_ID}, \"x\": 1, \"y\": 13, \"width\": 30, \"height\": 11}")
echo "✓ Flower Garden positioned (1, 13) - 30x11 ft"
if echo "$PATCH3_RESPONSE" | grep -q "error"; then
  echo "  Warning: $PATCH3_RESPONSE"
fi
echo ""

# Step 6: Create Trees for Sun-Path Visualization
echo "Step 6: Creating trees for seasonal shadow analysis..."

# Tree 1: Large Oak south of Vegetable Garden (creates significant shading)
# Garden is at (1,1) with size 14x10, so placing tree at x=8, y=-5 (south of garden)
TREE1_RESPONSE=$(curl -s -X POST "${API_URL}/trees" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"land_id\": ${LAND_ID},
    \"name\": \"Mature Oak\",
    \"x\": 8.0,
    \"y\": -5.0,
    \"height\": 18.0,
    \"canopy_radius\": 4.5
  }" 2>/dev/null)
TREE1_ID=$(echo "$TREE1_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
if [ ! -z "$TREE1_ID" ] && [ "$TREE1_ID" != "" ]; then
  echo "✓ Mature Oak created (ID: $TREE1_ID) - 18ft tall, 4.5ft radius"
  echo "  Position: (8, -5) - South of Vegetable Garden (demonstrates significant shading)"
else
  echo "✗ Failed to create Mature Oak - trees feature may not be enabled"
fi

# Tree 2: Medium Maple east of Herb Garden (partial shading)
# Garden is at (17,1) with size 14x10, so placing tree at x=33, y=6 (east side)
TREE2_RESPONSE=$(curl -s -X POST "${API_URL}/trees" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"land_id\": ${LAND_ID},
    \"name\": \"Red Maple\",
    \"x\": 33.0,
    \"y\": 6.0,
    \"height\": 12.0,
    \"canopy_radius\": 3.0
  }" 2>/dev/null)
TREE2_ID=$(echo "$TREE2_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
if [ ! -z "$TREE2_ID" ] && [ "$TREE2_ID" != "" ]; then
  echo "✓ Red Maple created (ID: $TREE2_ID) - 12ft tall, 3ft radius"
  echo "  Position: (33, 6) - East of Herb Garden (minimal shading)"
fi

# Tree 3: Tall Pine north of Flower Garden (no shading - shadows cast away)
# Garden is at (1,13) with size 30x11, so placing tree at x=16, y=26 (north of garden)
TREE3_RESPONSE=$(curl -s -X POST "${API_URL}/trees" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"land_id\": ${LAND_ID},
    \"name\": \"White Pine\",
    \"x\": 16.0,
    \"y\": 26.0,
    \"height\": 22.0,
    \"canopy_radius\": 3.5
  }" 2>/dev/null)
TREE3_ID=$(echo "$TREE3_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
if [ ! -z "$TREE3_ID" ] && [ "$TREE3_ID" != "" ]; then
  echo "✓ White Pine created (ID: $TREE3_ID) - 22ft tall, 3.5ft radius"
  echo "  Position: (16, 26) - North of Flower Garden (demonstrates zero shading)"
fi

# Tree 4: Small decorative tree in corner (minimal impact)
TREE4_RESPONSE=$(curl -s -X POST "${API_URL}/trees" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"land_id\": ${LAND_ID},
    \"name\": \"Ornamental Cherry\",
    \"x\": 31.0,
    \"y\": 23.0,
    \"height\": 8.0,
    \"canopy_radius\": 2.0
  }" 2>/dev/null)
TREE4_ID=$(echo "$TREE4_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
if [ ! -z "$TREE4_ID" ] && [ "$TREE4_ID" != "" ]; then
  echo "✓ Ornamental Cherry created (ID: $TREE4_ID) - 8ft tall, 2ft radius"
  echo "  Position: (31, 23) - Southeast corner (small shadows)"
fi

# Tree 5: Medium tree south-southwest of Flower Garden (moderate shading)
TREE5_RESPONSE=$(curl -s -X POST "${API_URL}/trees" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"land_id\": ${LAND_ID},
    \"name\": \"Sugar Maple\",
    \"x\": 10.0,
    \"y\": 9.0,
    \"height\": 15.0,
    \"canopy_radius\": 3.5
  }" 2>/dev/null)
TREE5_ID=$(echo "$TREE5_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
if [ ! -z "$TREE5_ID" ] && [ "$TREE5_ID" != "" ]; then
  echo "✓ Sugar Maple created (ID: $TREE5_ID) - 15ft tall, 3.5ft radius"
  echo "  Position: (10, 9) - Between gardens (moderate shading on Flower Garden)"
fi

echo ""
echo "Sun-Path Visualization Tips:"
echo "  • Mature Oak (south of Vegetable Garden): Demonstrates heavy winter shading"
echo "  • Red Maple (east): Shows minimal shading (east-west position)"
echo "  • White Pine (north): Demonstrates zero shading in Northern Hemisphere"
echo "  • Toggle 'Show Seasonal Shadows' to see Winter/Equinox/Summer projections"
echo "  • Gardens will be color-coded: Green (Full Sun), Orange (Partial), Gray (Shade)"
echo ""

# Step 7: Add Soil Samples
echo "Step 7: Creating soil samples..."

# Create soil samples for Herb Garden
curl -s -X POST "${API_URL}/soil-samples" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN2_ID},
    \"ph\": 6.8,
    \"nitrogen_ppm\": 45,
    \"phosphorus_ppm\": 30,
    \"potassium_ppm\": 150,
    \"moisture_percent\": 35,
    \"organic_matter_percent\": 4.2,
    \"date_collected\": \"$(date -u +"%Y-%m-%d")\",
    \"notes\": \"Sandy soil - good drainage\"
  }" > /dev/null
echo "✓ Created soil sample for Herb Garden (healthy)"

# Create soil samples for other gardens
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

# Step 8: Create Plantings with Different Varieties
echo "Step 8: Creating plantings with companion planting demonstrations..."

# Get plant variety IDs (query first few to find IDs)
VARIETIES=$(curl -s -X GET "${API_URL}/plant-varieties" \
  -H "Authorization: Bearer ${TOKEN}")

# Extract variety IDs (using grep for simplicity, assuming IDs are in order)
TOMATO_CHERRY_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Tomato' and v['variety_name']=='Cherry'), 1))" 2>/dev/null || echo "1")
PEPPER_BELL_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Pepper' and v['variety_name']=='Bell Pepper'), 7))" 2>/dev/null || echo "7")
LETTUCE_ROMAINE_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Lettuce' and v['variety_name']=='Romaine'), 14))" 2>/dev/null || echo "14")
CUCUMBER_SLICING_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Cucumber' and v['variety_name']=='Slicing'), 22))" 2>/dev/null || echo "22")
BASIL_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Basil'), 41))" 2>/dev/null || echo "41")
CILANTRO_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Cilantro'), 43))" 2>/dev/null || echo "43")
MINT_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Mint'), 45))" 2>/dev/null || echo "45")
PARSLEY_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Parsley'), 46))" 2>/dev/null || echo "46")
MARIGOLD_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Marigold'), 85))" 2>/dev/null || echo "85")
ZINNIA_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Zinnia'), 86))" 2>/dev/null || echo "86")
SUNFLOWER_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Sunflower'), 87))" 2>/dev/null || echo "87")
LETTUCE_BUTTER_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Lettuce' and v['variety_name']=='Butterhead'), 13))" 2>/dev/null || echo "13")
MICROGREENS_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Microgreens'), 94))" 2>/dev/null || echo "94")
# Additional varieties for companion planting demonstrations
CARROT_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Carrot'), 19))" 2>/dev/null || echo "19")
ONION_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Onion'), 33))" 2>/dev/null || echo "33")
RADISH_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Radish'), 18))" 2>/dev/null || echo "18")
BROCCOLI_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Broccoli'), 5))" 2>/dev/null || echo "5")
BEAN_ID=$(echo "$VARIETIES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(next((v['id'] for v in data if v['common_name']=='Bean'), 23))" 2>/dev/null || echo "23")

# Plantings for Vegetable Garden - with positions for companion planting analysis
PLANTING_DATE_30D=$(date -u -v-30d +"%Y-%m-%d" 2>/dev/null || date -u -d '30 days ago' +"%Y-%m-%d")
PLANTING_DATE_45D=$(date -u -v-45d +"%Y-%m-%d" 2>/dev/null || date -u -d '45 days ago' +"%Y-%m-%d")
PLANTING_DATE_20D=$(date -u -v-20d +"%Y-%m-%d" 2>/dev/null || date -u -d '20 days ago' +"%Y-%m-%d")
PLANTING_DATE_15D=$(date -u -v-15d +"%Y-%m-%d" 2>/dev/null || date -u -d '15 days ago' +"%Y-%m-%d")

# Tomato at (2.0, 2.0) - will pair with Basil (beneficial) and conflict with Broccoli
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN1_ID},
    \"plant_variety_id\": ${TOMATO_CHERRY_ID},
    \"planting_date\": \"${PLANTING_DATE_45D}\",
    \"planting_method\": \"transplant\",
    \"plant_count\": 6,
    \"location_in_garden\": \"North bed, rows 1-2\",
    \"health_status\": \"healthy\",
    \"x\": 2.0,
    \"y\": 2.0,
    \"notes\": \"Cherry tomatoes for summer harvest, planted with basil companion\"
  }" > /dev/null
echo "✓ Planted Cherry Tomatoes at (2.0, 2.0) - companion planting with Basil"

# Basil at (2.4, 2.0) - beneficial companion to Tomato (0.4m distance)
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN1_ID},
    \"plant_variety_id\": ${BASIL_ID},
    \"planting_date\": \"${PLANTING_DATE_45D}\",
    \"planting_method\": \"transplant\",
    \"plant_count\": 8,
    \"location_in_garden\": \"North bed, with tomatoes\",
    \"health_status\": \"healthy\",
    \"x\": 2.4,
    \"y\": 2.0,
    \"notes\": \"Sweet basil as tomato companion - improves flavor and deters pests\"
  }" > /dev/null
echo "✓ Planted Basil at (2.4, 2.0) - 0.4m from Tomatoes (beneficial pair)"

# Carrot at (1.0, 3.5) - will pair with Onion (beneficial)
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN1_ID},
    \"plant_variety_id\": ${CARROT_ID},
    \"planting_date\": \"${PLANTING_DATE_30D}\",
    \"planting_method\": \"direct_sow\",
    \"plant_count\": 20,
    \"location_in_garden\": \"South bed, row 1\",
    \"health_status\": \"healthy\",
    \"x\": 1.0,
    \"y\": 3.5,
    \"notes\": \"Carrots interplanted with onions to deter carrot fly\"
  }" > /dev/null
echo "✓ Planted Carrots at (1.0, 3.5) - companion planting with Onions"

# Onion at (1.3, 3.5) - beneficial companion to Carrot (0.3m distance)
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN1_ID},
    \"plant_variety_id\": ${ONION_ID},
    \"planting_date\": \"${PLANTING_DATE_30D}\",
    \"planting_method\": \"transplant\",
    \"plant_count\": 15,
    \"location_in_garden\": \"South bed, row 1\",
    \"health_status\": \"healthy\",
    \"x\": 1.3,
    \"y\": 3.5,
    \"notes\": \"Onions as carrot companion - mutual pest deterrence\"
  }" > /dev/null
echo "✓ Planted Onions at (1.3, 3.5) - 0.3m from Carrots (beneficial pair)"

# Lettuce at (3.2, 3.2) - will pair with Radish (beneficial)
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN1_ID},
    \"plant_variety_id\": ${LETTUCE_ROMAINE_ID},
    \"planting_date\": \"${PLANTING_DATE_20D}\",
    \"planting_method\": \"direct_sow\",
    \"plant_count\": 12,
    \"location_in_garden\": \"South bed, succession planting\",
    \"health_status\": \"healthy\",
    \"x\": 3.2,
    \"y\": 3.2,
    \"notes\": \"Cut-and-come-again harvesting, planted with radishes\"
  }" > /dev/null
echo "✓ Planted Romaine Lettuce at (3.2, 3.2) - companion planting with Radishes"

# Radish at (3.5, 3.2) - beneficial companion to Lettuce (0.3m distance)
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN1_ID},
    \"plant_variety_id\": ${RADISH_ID},
    \"planting_date\": \"${PLANTING_DATE_20D}\",
    \"planting_method\": \"direct_sow\",
    \"plant_count\": 30,
    \"location_in_garden\": \"South bed, interplanted\",
    \"health_status\": \"healthy\",
    \"x\": 3.5,
    \"y\": 3.2,
    \"notes\": \"Fast-growing radishes as lettuce companion\"
  }" > /dev/null
echo "✓ Planted Radishes at (3.5, 3.2) - 0.3m from Lettuce (beneficial pair)"

# Cucumber at (0.5, 1.5) - on trellis
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN1_ID},
    \"plant_variety_id\": ${CUCUMBER_SLICING_ID},
    \"planting_date\": \"${PLANTING_DATE_30D}\",
    \"planting_method\": \"direct_sow\",
    \"plant_count\": 3,
    \"location_in_garden\": \"Trellis along west side\",
    \"health_status\": \"healthy\",
    \"x\": 0.5,
    \"y\": 1.5,
    \"notes\": \"Vertical growing on trellis\"
  }" > /dev/null
echo "✓ Planted Slicing Cucumbers at (0.5, 1.5)"

# Broccoli at (3.5, 2.5) - antagonistic to Tomato (~1.8m distance, within 3m threshold)
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN1_ID},
    \"plant_variety_id\": ${BROCCOLI_ID},
    \"planting_date\": \"${PLANTING_DATE_45D}\",
    \"planting_method\": \"transplant\",
    \"plant_count\": 4,
    \"location_in_garden\": \"North bed, row 4\",
    \"health_status\": \"healthy\",
    \"x\": 3.5,
    \"y\": 2.5,
    \"notes\": \"Broccoli for fall harvest - may compete with nearby tomatoes\"
  }" > /dev/null
echo "✓ Planted Broccoli at (3.5, 2.5) - demonstrates conflict with Tomato"

# Bean at (0.8, 3.5) - antagonistic to Onion (~0.5m distance, within 2m threshold)
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN1_ID},
    \"plant_variety_id\": ${BEAN_ID},
    \"planting_date\": \"${PLANTING_DATE_30D}\",
    \"planting_method\": \"direct_sow\",
    \"plant_count\": 12,
    \"location_in_garden\": \"South bed, row 2\",
    \"health_status\": \"healthy\",
    \"x\": 0.8,
    \"y\": 3.5,
    \"notes\": \"Bush beans for nitrogen fixing\"
  }" > /dev/null
echo "✓ Planted Beans at (0.8, 3.5) - demonstrates conflict with Onions"

# Bell Peppers at (3.8, 1.2) - separate area
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN1_ID},
    \"plant_variety_id\": ${PEPPER_BELL_ID},
    \"planting_date\": \"${PLANTING_DATE_45D}\",
    \"planting_method\": \"transplant\",
    \"plant_count\": 4,
    \"location_in_garden\": \"North bed, row 5\",
    \"health_status\": \"healthy\",
    \"x\": 3.8,
    \"y\": 1.2,
    \"notes\": \"Bell peppers - multiple colors\"
  }" > /dev/null
echo "✓ Planted Bell Peppers at (3.8, 1.2)"

# Plantings for Herb Garden
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN2_ID},
    \"plant_variety_id\": ${BASIL_ID},
    \"planting_date\": \"${PLANTING_DATE_30D}\",
    \"planting_method\": \"transplant\",
    \"plant_count\": 8,
    \"location_in_garden\": \"Center rows\",
    \"health_status\": \"healthy\",
    \"notes\": \"Sweet basil for culinary use\"
  }" > /dev/null
echo "✓ Planted Basil in Herb Garden (8 plants)"

curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN2_ID},
    \"plant_variety_id\": ${CILANTRO_ID},
    \"planting_date\": \"${PLANTING_DATE_20D}\",
    \"planting_method\": \"direct_sow\",
    \"plant_count\": 20,
    \"location_in_garden\": \"North section\",
    \"health_status\": \"healthy\",
    \"notes\": \"Succession planting for continuous harvest\"
  }" > /dev/null
echo "✓ Planted Cilantro in Herb Garden (20 plants)"

curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN2_ID},
    \"plant_variety_id\": ${MINT_ID},
    \"planting_date\": \"${PLANTING_DATE_45D}\",
    \"planting_method\": \"transplant\",
    \"plant_count\": 3,
    \"location_in_garden\": \"South section (contained)\",
    \"health_status\": \"healthy\",
    \"notes\": \"In buried containers to prevent spreading\"
  }" > /dev/null
echo "✓ Planted Mint in Herb Garden (3 plants, contained)"

# Plantings for Flower Garden
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN3_ID},
    \"plant_variety_id\": ${MARIGOLD_ID},
    \"planting_date\": \"${PLANTING_DATE_30D}\",
    \"planting_method\": \"transplant\",
    \"plant_count\": 15,
    \"location_in_garden\": \"Border rows\",
    \"health_status\": \"healthy\",
    \"notes\": \"Pest deterrent and companion planting\"
  }" > /dev/null
echo "✓ Planted Marigolds in Flower Garden (15 plants)"

curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN3_ID},
    \"plant_variety_id\": ${ZINNIA_ID},
    \"planting_date\": \"${PLANTING_DATE_30D}\",
    \"planting_method\": \"direct_sow\",
    \"plant_count\": 25,
    \"location_in_garden\": \"Center mass planting\",
    \"health_status\": \"healthy\",
    \"notes\": \"Mixed colors for pollinators\"
  }" > /dev/null
echo "✓ Planted Zinnias in Flower Garden (25 plants)"

curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN3_ID},
    \"plant_variety_id\": ${SUNFLOWER_ID},
    \"planting_date\": \"${PLANTING_DATE_45D}\",
    \"planting_method\": \"direct_sow\",
    \"plant_count\": 6,
    \"location_in_garden\": \"Back row, north side\",
    \"health_status\": \"healthy\",
    \"notes\": \"Tall variety for birds and beauty\"
  }" > /dev/null
echo "✓ Planted Sunflowers in Flower Garden (6 plants)"

# Plantings for Indoor Herb Garden
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN4_ID},
    \"plant_variety_id\": ${BASIL_ID},
    \"planting_date\": \"${PLANTING_DATE_15D}\",
    \"planting_method\": \"transplant\",
    \"plant_count\": 4,
    \"location_in_garden\": \"South-facing window\",
    \"health_status\": \"healthy\",
    \"notes\": \"Fresh basil year-round\"
  }" > /dev/null
echo "✓ Planted Basil in Indoor Herb Garden (4 plants)"

curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN4_ID},
    \"plant_variety_id\": ${PARSLEY_ID},
    \"planting_date\": \"${PLANTING_DATE_15D}\",
    \"planting_method\": \"direct_sow\",
    \"plant_count\": 6,
    \"location_in_garden\": \"Kitchen counter\",
    \"health_status\": \"healthy\",
    \"notes\": \"Flat-leaf Italian parsley\"
  }" > /dev/null
echo "✓ Planted Parsley in Indoor Herb Garden (6 plants)"

# Plantings for Hydroponic Greens
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN5_ID},
    \"plant_variety_id\": ${LETTUCE_ROMAINE_ID},
    \"planting_date\": \"${PLANTING_DATE_20D}\",
    \"planting_method\": \"transplant\",
    \"plant_count\": 12,
    \"location_in_garden\": \"NFT channels 1-2\",
    \"health_status\": \"healthy\",
    \"notes\": \"Hydroponic romaine for salads\"
  }" > /dev/null
echo "✓ Planted Romaine Lettuce in Hydroponic System (12 plants)"

curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN5_ID},
    \"plant_variety_id\": ${LETTUCE_BUTTER_ID},
    \"planting_date\": \"${PLANTING_DATE_20D}\",
    \"planting_method\": \"transplant\",
    \"plant_count\": 8,
    \"location_in_garden\": \"NFT channel 3\",
    \"health_status\": \"healthy\",
    \"notes\": \"Butterhead for variety\"
  }" > /dev/null
echo "✓ Planted Butterhead Lettuce in Hydroponic System (8 plants)"

curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN5_ID},
    \"plant_variety_id\": ${MICROGREENS_ID},
    \"planting_date\": \"$(date -u -v-5d +"%Y-%m-%d" 2>/dev/null || date -u -d '5 days ago' +"%Y-%m-%d")\",
    \"planting_method\": \"direct_sow\",
    \"plant_count\": 100,
    \"location_in_garden\": \"Tray 1\",
    \"health_status\": \"healthy\",
    \"notes\": \"Quick-growing microgreens, ready in 7-14 days\"
  }" > /dev/null
echo "✓ Planted Microgreens in Hydroponic System (100+ seeds, almost ready)"

# Plantings for Hydroponic Tomatoes (Garden 6) - Fruiting Stage
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN6_ID},
    \"plant_variety_id\": ${TOMATO_CHERRY_ID},
    \"planting_date\": \"${PLANTING_DATE_45D}\",
    \"planting_method\": \"transplant\",
    \"plant_count\": 4,
    \"location_in_garden\": \"DWC buckets 1-4\",
    \"health_status\": \"healthy\",
    \"notes\": \"Hydroponic cherry tomatoes in fruiting stage - high EC demand (2.5-3.0 mS/cm)\"
  }" > /dev/null
echo "✓ Planted Cherry Tomatoes in Hydroponic DWC (4 plants, fruiting stage - HIGH EC)"

# Plantings for Container Garden (Garden 7) - Flowering Stage
curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN7_ID},
    \"plant_variety_id\": ${PEPPER_BELL_ID},
    \"planting_date\": \"${PLANTING_DATE_30D}\",
    \"planting_method\": \"transplant\",
    \"plant_count\": 6,
    \"location_in_garden\": \"Large containers with drip lines\",
    \"health_status\": \"healthy\",
    \"notes\": \"Bell peppers in flowering stage with fertigation - medium EC demand (1.5-2.0 mS/cm)\"
  }" > /dev/null
echo "✓ Planted Bell Peppers in Container Garden (6 plants, flowering - MEDIUM EC)"

curl -s -X POST "${API_URL}/planting-events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"garden_id\": ${GARDEN7_ID},
    \"plant_variety_id\": ${BASIL_ID},
    \"planting_date\": \"${PLANTING_DATE_20D}\",
    \"planting_method\": \"transplant\",
    \"plant_count\": 8,
    \"location_in_garden\": \"Small containers\",
    \"health_status\": \"healthy\",
    \"notes\": \"Basil companion plants in vegetative stage - low EC demand (1.0-1.6 mS/cm)\"
  }" > /dev/null
echo "✓ Planted Basil in Container Garden (8 plants, vegetative - LOW EC)"
echo ""

# Summary
echo "================================================"
echo "Test Data Setup Complete!"
echo "================================================"
echo ""
echo "Created Resources:"
echo "  • 1 Land: Main Property (${LAND_WIDTH}x${LAND_HEIGHT} ft)"
echo "  • 5 Trees for Sun-Path Visualization:"
echo "    - Mature Oak (18ft, south of Vegetable Garden) - Heavy shading demo"
echo "    - Red Maple (12ft, east of Herb Garden) - Minimal shading"
echo "    - White Pine (22ft, north of Flower Garden) - Zero shading (NH)"
echo "    - Ornamental Cherry (8ft, southeast corner) - Small shadows"
echo "    - Sugar Maple (15ft, between gardens) - Moderate shading"
echo "  • 7 Gardens:"
echo "    - Vegetable Garden (Outdoor, Loam) - ID: $GARDEN1_ID"
echo "    - Herb Garden (Outdoor, Sandy) - ID: $GARDEN2_ID"
echo "    - Flower Garden (Outdoor, Clay) - ID: $GARDEN3_ID"
echo "    - Indoor Herb Garden (Indoor) - ID: $GARDEN4_ID"
echo "    - Hydroponic Greens (NFT, 50L) - ID: $GARDEN5_ID"
echo "    - Hydroponic Tomatoes (DWC, 80L) - ID: $GARDEN6_ID"
echo "    - Patio Container Garden (Container, 30L) - ID: $GARDEN7_ID"
echo "  • 27 Planting Events (with companion planting demonstrations):"
echo "    - Vegetable Garden: 10 varieties with positions demonstrating:"
echo "      ✓ Tomato + Basil (beneficial pair at 0.4m)"
echo "      ✓ Carrot + Onion (beneficial pair at 0.3m)"
echo "      ✓ Lettuce + Radish (beneficial pair at 0.3m)"
echo "      ⚠️  Tomato + Broccoli (conflict within 3m)"
echo "      ⚠️  Bean + Onion (conflict within 2m)"
echo "    - Herb Garden: 3 varieties (Basil, Cilantro, Mint)"
echo "    - Flower Garden: 3 varieties (Marigold, Zinnia, Sunflower)"
echo "    - Indoor Herb Garden: 2 varieties (Basil, Parsley)"
echo "    - Hydroponic Greens: 3 varieties (Romaine, Butterhead, Microgreens)"
echo "    - Hydroponic Tomatoes: Cherry tomatoes in fruiting stage"
echo "    - Container Garden: Bell peppers + Basil (mixed EC demands)"
echo "  • 3 Soil Samples (healthy data for outdoor gardens)"
echo ""
echo "🌱 Companion Planting Analysis:"
echo "  Test companion planting insights for Vegetable Garden (ID: $GARDEN1_ID)"
echo "  View beneficial pairs and conflicts:"
echo "    curl -s http://localhost:8080/gardens/${GARDEN1_ID}/companion-planting-analysis \\"
echo "      -H \"Authorization: Bearer \$TOKEN\" | python3 -m json.tool"
echo ""
echo "  Beneficial Pairs Demonstrated:"
echo "     • Tomato + Basil (0.4m): Basil deters aphids, improves tomato flavor"
echo "     • Carrot + Onion (0.3m): Onion scent confuses carrot fly"
echo "     • Lettuce + Radish (0.3m): Radishes loosen soil for lettuce roots"
echo ""
echo "  Conflicts Demonstrated:"
echo "     • Tomato + Broccoli (~1.8m, within 3m threshold): Competition for nutrients"
echo "     • Bean + Onion (~0.5m, within 2m threshold): Onions inhibit bean growth"
echo ""
echo "🧪 Nutrient Optimization (Hydroponic/Fertigation/Container Systems):"
echo "  Three systems demonstrating different EC/pH requirements:"
echo "     • Hydroponic Greens (NFT): Lettuce in vegetative stage"
echo "       → Low EC 0.8-1.2 mS/cm, pH 5.5-6.5"
echo "     • Hydroponic Tomatoes (DWC): Fruiting stage (45 days old)"
echo "       → HIGH EC 2.5-3.0 mS/cm, pH 5.5-6.5"
echo "     • Container Garden (Fertigation): Mixed crops (peppers flowering + basil vegetative)"
echo "       → Medium EC 1.5-2.0 mS/cm (max demand wins)"
echo ""
echo "  View nutrient recommendations:"
echo "    curl -s http://localhost:8080/gardens/${GARDEN5_ID}/nutrient-optimization \\"
echo "      -H \"Authorization: Bearer \$TOKEN\" | python3 -m json.tool"
echo ""
echo "    curl -s http://localhost:8080/gardens/${GARDEN6_ID}/nutrient-optimization \\"
echo "      -H \"Authorization: Bearer \$TOKEN\" | python3 -m json.tool"
echo ""
echo "    curl -s http://localhost:8080/gardens/${GARDEN7_ID}/nutrient-optimization \\"
echo "      -H \"Authorization: Bearer \$TOKEN\" | python3 -m json.tool"
echo ""
echo "  Features demonstrated:"
echo "     - Growth stage-dependent EC recommendations (seedling→vegetative→flowering→fruiting)"
echo "     - pH optimization for nutrient availability"
echo "     - Solution replacement schedules based on reservoir size"
echo "     - Mixed-crop EC calculation (highest demand wins)"
echo ""
echo "☀️  Sun-Path & Seasonal Shadow Analysis:"
echo "  Go to Layout view and enable 'Show Seasonal Shadows'"
echo "  Select Winter/Equinox/Summer to see shadow projections"
echo "  Gardens color-coded: Green=Full Sun, Orange=Partial, Gray=Shade"
echo "  Click gardens to view detailed seasonal sun exposure data"
echo "  Note: Trees to the south cast shadows northward (Northern Hemisphere)"
echo ""
echo "🌍 View in app: http://localhost:3000"
echo ""
echo "🔄 IMPORTANT: Refresh your browser (Cmd+R / Ctrl+R) to see the updated land layout!"
echo ""
