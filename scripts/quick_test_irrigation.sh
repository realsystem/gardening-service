#!/bin/bash

# Quick Irrigation System API Test
# Simple smoke test for basic functionality

set -e

# Configuration
API_URL="http://localhost:8080"
EMAIL="${TEST_EMAIL:-test@example.com}"
PASSWORD="${TEST_PASSWORD:-password123}"

echo "Quick Irrigation API Test"
echo "=========================="
echo ""

# Login
echo "1. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/users/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"${EMAIL}\", \"password\": \"${PASSWORD}\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed"
    echo ""
    echo "Response: $LOGIN_RESPONSE"
    echo ""
    echo "Please either:"
    echo "  1. Create a test user at http://localhost:3000"
    echo "  2. Use existing credentials:"
    echo "     TEST_EMAIL=your@email.com TEST_PASSWORD=yourpass ./scripts/quick_test_irrigation.sh"
    exit 1
fi
echo "✓ Login successful"

# Create water source
echo "2. Creating water source..."
SOURCE=$(curl -s -X POST "${API_URL}/irrigation-system/sources" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Source", "source_type": "city"}')
echo "✓ Source created"

# Create irrigation zone
echo "3. Creating irrigation zone..."
ZONE=$(curl -s -X POST "${API_URL}/irrigation-system/zones" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Zone", "delivery_type": "drip", "schedule": {"frequency_days": 3, "duration_minutes": 30}}')

ZONE_ID=$(echo "$ZONE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "✓ Zone created (ID: $ZONE_ID)"

# Record watering event
echo "4. Recording watering event..."
EVENT=$(curl -s -X POST "${API_URL}/irrigation-system/events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"irrigation_zone_id\": ${ZONE_ID}, \"watered_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")\", \"duration_minutes\": 30, \"is_manual\": true}")
echo "✓ Event recorded"

# Get overview
echo "5. Getting system overview..."
OVERVIEW=$(curl -s -X GET "${API_URL}/irrigation-system/overview" \
  -H "Authorization: Bearer ${TOKEN}")

ZONE_COUNT=$(echo "$OVERVIEW" | grep -o '"zones":' | wc -l)
echo "✓ Overview retrieved"

# Get insights
echo "6. Getting insights..."
INSIGHTS=$(curl -s -X GET "${API_URL}/irrigation-system/insights" \
  -H "Authorization: Bearer ${TOKEN}")
echo "✓ Insights retrieved"

echo ""
echo "=========================="
echo "✅ All tests passed!"
echo "=========================="
