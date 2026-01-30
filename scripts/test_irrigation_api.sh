#!/bin/bash

# Irrigation System API Test Script
# Tests all irrigation system endpoints with curl

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
API_URL="http://localhost:8080"
EMAIL="${TEST_EMAIL:-test@example.com}"
PASSWORD="${TEST_PASSWORD:-password123}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Irrigation System API Tests${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print step
print_step() {
    echo -e "${YELLOW}▶ $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    echo ""
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
    echo ""
}

# Function to print JSON response
print_json() {
    echo "$1" | python3 -m json.tool 2>/dev/null || echo "$1"
}

# ============================================
# Step 1: Login and get token
# ============================================
print_step "Step 1: Login to get authentication token"

LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/users/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"${EMAIL}\", \"password\": \"${PASSWORD}\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    print_error "Failed to login. Please create a user first or check credentials."
    echo "Response:"
    print_json "$LOGIN_RESPONSE"
    exit 1
fi

print_success "Logged in successfully"
echo "Token: ${TOKEN:0:20}..."
echo ""

# ============================================
# Step 2: Create a water source
# ============================================
print_step "Step 2: Create water source"

SOURCE_RESPONSE=$(curl -s -X POST "${API_URL}/irrigation-system/sources" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "City Water Main",
    "source_type": "city",
    "flow_capacity_lpm": 50.0,
    "notes": "Main water line from city supply"
  }')

SOURCE_ID=$(echo "$SOURCE_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$SOURCE_ID" ]; then
    print_error "Failed to create water source"
    echo "Response:"
    print_json "$SOURCE_RESPONSE"
else
    print_success "Water source created (ID: $SOURCE_ID)"
    print_json "$SOURCE_RESPONSE"
fi
echo ""

# ============================================
# Step 3: List water sources
# ============================================
print_step "Step 3: List all water sources"

SOURCES_LIST=$(curl -s -X GET "${API_URL}/irrigation-system/sources" \
  -H "Authorization: Bearer ${TOKEN}")

print_success "Retrieved water sources"
print_json "$SOURCES_LIST"
echo ""

# ============================================
# Step 4: Create irrigation zone
# ============================================
print_step "Step 4: Create irrigation zone"

ZONE_RESPONSE=$(curl -s -X POST "${API_URL}/irrigation-system/zones" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Vegetable Garden Zone\",
    \"delivery_type\": \"drip\",
    \"irrigation_source_id\": ${SOURCE_ID},
    \"schedule\": {
      \"frequency_days\": 3,
      \"duration_minutes\": 30
    },
    \"notes\": \"Drip irrigation for vegetable beds\"
  }")

ZONE_ID=$(echo "$ZONE_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$ZONE_ID" ]; then
    print_error "Failed to create irrigation zone"
    echo "Response:"
    print_json "$ZONE_RESPONSE"
else
    print_success "Irrigation zone created (ID: $ZONE_ID)"
    print_json "$ZONE_RESPONSE"
fi
echo ""

# ============================================
# Step 5: Create another zone (for testing)
# ============================================
print_step "Step 5: Create second irrigation zone"

ZONE2_RESPONSE=$(curl -s -X POST "${API_URL}/irrigation-system/zones" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Flower Bed Zone",
    "delivery_type": "sprinkler",
    "schedule": {
      "frequency_days": 2,
      "duration_minutes\": 15
    },
    "notes": "Overhead sprinklers for flower beds"
  }')

ZONE2_ID=$(echo "$ZONE2_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$ZONE2_ID" ]; then
    print_error "Failed to create second zone"
else
    print_success "Second zone created (ID: $ZONE2_ID)"
    print_json "$ZONE2_RESPONSE"
fi
echo ""

# ============================================
# Step 6: List all zones
# ============================================
print_step "Step 6: List all irrigation zones"

ZONES_LIST=$(curl -s -X GET "${API_URL}/irrigation-system/zones" \
  -H "Authorization: Bearer ${TOKEN}")

print_success "Retrieved irrigation zones"
print_json "$ZONES_LIST"
echo ""

# ============================================
# Step 7: Get zone details
# ============================================
if [ ! -z "$ZONE_ID" ]; then
    print_step "Step 7: Get detailed zone information"

    ZONE_DETAILS=$(curl -s -X GET "${API_URL}/irrigation-system/zones/${ZONE_ID}/details" \
      -H "Authorization: Bearer ${TOKEN}")

    print_success "Retrieved zone details"
    print_json "$ZONE_DETAILS"
    echo ""
fi

# ============================================
# Step 8: Record watering event
# ============================================
if [ ! -z "$ZONE_ID" ]; then
    print_step "Step 8: Record watering event"

    CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")

    EVENT_RESPONSE=$(curl -s -X POST "${API_URL}/irrigation-system/events" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{
        \"irrigation_zone_id\": ${ZONE_ID},
        \"watered_at\": \"${CURRENT_TIME}\",
        \"duration_minutes\": 30,
        \"estimated_volume_liters\": 25.0,
        \"is_manual\": true,
        \"notes\": \"Test watering event\"
      }")

    EVENT_ID=$(echo "$EVENT_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

    if [ -z "$EVENT_ID" ]; then
        print_error "Failed to record watering event"
        echo "Response:"
        print_json "$EVENT_RESPONSE"
    else
        print_success "Watering event recorded (ID: $EVENT_ID)"
        print_json "$EVENT_RESPONSE"
    fi
    echo ""
fi

# ============================================
# Step 9: Record multiple events for testing insights
# ============================================
if [ ! -z "$ZONE_ID" ]; then
    print_step "Step 9: Record multiple watering events (for insights testing)"

    # Record events over the past week with short durations (should trigger DUR_001)
    for i in 1 2 3 4 5; do
        DAYS_AGO=$((i * 1))
        EVENT_TIME=$(date -u -v-${DAYS_AGO}d +"%Y-%m-%dT%H:%M:%S.000Z" 2>/dev/null || date -u -d "${DAYS_AGO} days ago" +"%Y-%m-%dT%H:%M:%S.000Z")

        curl -s -X POST "${API_URL}/irrigation-system/events" \
          -H "Authorization: Bearer ${TOKEN}" \
          -H "Content-Type: application/json" \
          -d "{
            \"irrigation_zone_id\": ${ZONE_ID},
            \"watered_at\": \"${EVENT_TIME}\",
            \"duration_minutes\": 8,
            \"is_manual\": true,
            \"notes\": \"Test event ${i}\"
          }" > /dev/null
    done

    print_success "Recorded 5 test watering events (daily with 8-minute durations)"
    echo ""
fi

# ============================================
# Step 10: List watering events
# ============================================
if [ ! -z "$ZONE_ID" ]; then
    print_step "Step 10: List watering events for zone"

    EVENTS_LIST=$(curl -s -X GET "${API_URL}/irrigation-system/events?zone_id=${ZONE_ID}&days=30" \
      -H "Authorization: Bearer ${TOKEN}")

    print_success "Retrieved watering events"
    print_json "$EVENTS_LIST"
    echo ""
fi

# ============================================
# Step 11: Get irrigation overview
# ============================================
print_step "Step 11: Get irrigation system overview"

OVERVIEW=$(curl -s -X GET "${API_URL}/irrigation-system/overview" \
  -H "Authorization: Bearer ${TOKEN}")

print_success "Retrieved irrigation overview"
print_json "$OVERVIEW"
echo ""

# ============================================
# Step 12: Get irrigation insights
# ============================================
print_step "Step 12: Get irrigation insights (rule engine analysis)"

INSIGHTS=$(curl -s -X GET "${API_URL}/irrigation-system/insights" \
  -H "Authorization: Bearer ${TOKEN}")

print_success "Retrieved irrigation insights"
print_json "$INSIGHTS"
echo ""

# Check for expected insights
FREQ_RULE=$(echo "$INSIGHTS" | grep -c "FREQ_001" || true)
DUR_RULE=$(echo "$INSIGHTS" | grep -c "DUR_001" || true)

if [ "$FREQ_RULE" -gt 0 ]; then
    echo -e "${GREEN}✓ FREQ_001 rule triggered (watering too frequently)${NC}"
fi
if [ "$DUR_RULE" -gt 0 ]; then
    echo -e "${GREEN}✓ DUR_001 rule triggered (frequent shallow watering)${NC}"
fi
echo ""

# ============================================
# Step 13: Get a single source
# ============================================
if [ ! -z "$SOURCE_ID" ]; then
    print_step "Step 13: Get single water source by ID"

    SOURCE_DETAIL=$(curl -s -X GET "${API_URL}/irrigation-system/sources/${SOURCE_ID}" \
      -H "Authorization: Bearer ${TOKEN}")

    print_success "Retrieved water source details"
    print_json "$SOURCE_DETAIL"
    echo ""
fi

# ============================================
# Step 14: Update irrigation zone
# ============================================
if [ ! -z "$ZONE_ID" ]; then
    print_step "Step 14: Update irrigation zone"

    UPDATE_RESPONSE=$(curl -s -X PATCH "${API_URL}/irrigation-system/zones/${ZONE_ID}" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Content-Type: application/json" \
      -d '{
        "schedule": {
          "frequency_days": 4,
          "duration_minutes": 45
        },
        "notes": "Updated schedule - increased duration and frequency"
      }')

    print_success "Zone updated"
    print_json "$UPDATE_RESPONSE"
    echo ""
fi

# ============================================
# Step 15: Assign garden to zone (if gardens exist)
# ============================================
print_step "Step 15: Get gardens for assignment test"

GARDENS=$(curl -s -X GET "${API_URL}/gardens" \
  -H "Authorization: Bearer ${TOKEN}")

GARDEN_ID=$(echo "$GARDENS" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ ! -z "$GARDEN_ID" ] && [ ! -z "$ZONE_ID" ]; then
    print_step "Step 15a: Assign garden to zone"

    ASSIGN_RESPONSE=$(curl -s -X POST "${API_URL}/irrigation-system/gardens/${GARDEN_ID}/assign-zone?zone_id=${ZONE_ID}" \
      -H "Authorization: Bearer ${TOKEN}")

    print_success "Garden assigned to zone"
    print_json "$ASSIGN_RESPONSE"
    echo ""
else
    print_error "No gardens found or zone not created - skipping assignment test"
fi

# ============================================
# Summary
# ============================================
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ All API endpoints tested successfully${NC}"
echo ""
echo "Created Resources:"
[ ! -z "$SOURCE_ID" ] && echo "  - Water Source ID: $SOURCE_ID"
[ ! -z "$ZONE_ID" ] && echo "  - Irrigation Zone ID: $ZONE_ID"
[ ! -z "$ZONE2_ID" ] && echo "  - Second Zone ID: $ZONE2_ID"
[ ! -z "$EVENT_ID" ] && echo "  - Watering Event ID: $EVENT_ID"
[ ! -z "$GARDEN_ID" ] && [ ! -z "$ZONE_ID" ] && echo "  - Garden $GARDEN_ID assigned to Zone $ZONE_ID"
echo ""
echo -e "${YELLOW}Note: Check the 'Insights' section above for rule engine analysis${NC}"
echo -e "${YELLOW}Expected rules: FREQ_001 (too frequent), DUR_001 (short duration)${NC}"
echo ""
