#!/bin/bash
# Smoke Tests for Deployed Gardening Service
# Usage: ./scripts/smoke-test.sh <api-url>
# Example: ./scripts/smoke-test.sh https://gardening-service-api.fly.dev

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get API URL from argument or use default
API_URL="${1:-https://gardening-service-api.fly.dev}"

echo "=== Gardening Service Smoke Tests ==="
echo "API URL: $API_URL"
echo ""

# Test counter
PASSED=0
FAILED=0

# Helper function to run tests
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected="$3"
    
    echo -n "$test_name... "
    
    if eval "$test_command" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
        return 1
    fi
}

# Test 1: Health Check
echo "=== Test 1: Health Check ==="
run_test "Health endpoint" "curl -s $API_URL/health" "healthy"
echo ""

# Test 2: API Documentation
echo "=== Test 2: API Documentation ==="
run_test "OpenAPI docs" "curl -s $API_URL/docs" "<title>"
echo ""

# Test 3: User Registration
echo "=== Test 3: User Registration ==="
TEST_EMAIL="smoketest-$(date +%s)@example.com"
TEST_PASSWORD="TestPassword123!"

echo "Registering test user: $TEST_EMAIL"
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/api/users" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"zip_code\": \"94102\"
  }")

if echo "$REGISTER_RESPONSE" | grep -q "id"; then
    echo -e "User registration: ${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "User registration: ${RED}✗ FAIL${NC}"
    echo "Response: $REGISTER_RESPONSE"
    ((FAILED++))
fi
echo ""

# Test 4: User Login
echo "=== Test 4: User Login ==="
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/users/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$TEST_EMAIL&password=$TEST_PASSWORD")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "User login: ${GREEN}✓ PASS${NC}"
    ((PASSED++))
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")
else
    echo -e "User login: ${RED}✗ FAIL${NC}"
    echo "Response: $LOGIN_RESPONSE"
    ((FAILED++))
    TOKEN=""
fi
echo ""

if [ -z "$TOKEN" ]; then
    echo -e "${RED}Cannot continue tests without authentication token${NC}"
    echo ""
    echo "=== Test Results ==="
    echo -e "Passed: ${GREEN}$PASSED${NC}"
    echo -e "Failed: ${RED}$FAILED${NC}"
    exit 1
fi

# Test 5: Create Garden
echo "=== Test 5: Create Garden ==="
GARDEN_RESPONSE=$(curl -s -X POST "$API_URL/api/gardens" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Smoke Test Garden",
    "garden_type": "outdoor",
    "size_sq_ft": 100
  }')

if echo "$GARDEN_RESPONSE" | grep -q "id"; then
    echo -e "Create garden: ${GREEN}✓ PASS${NC}"
    ((PASSED++))
    GARDEN_ID=$(echo "$GARDEN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "1")
else
    echo -e "Create garden: ${RED}✗ FAIL${NC}"
    echo "Response: $GARDEN_RESPONSE"
    ((FAILED++))
    GARDEN_ID="1"
fi
echo ""

# Test 6: Get Plant Varieties
echo "=== Test 6: Get Plant Varieties ==="
VARIETIES_RESPONSE=$(curl -s -X GET "$API_URL/api/plant-varieties" \
  -H "Authorization: Bearer $TOKEN")

if echo "$VARIETIES_RESPONSE" | grep -q "common_name"; then
    echo -e "Get plant varieties: ${GREEN}✓ PASS${NC}"
    ((PASSED++))
    VARIETY_ID=$(echo "$VARIETIES_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)[0]['id'])" 2>/dev/null || echo "1")
else
    echo -e "Get plant varieties: ${RED}✗ FAIL${NC}"
    echo "Response: $VARIETIES_RESPONSE"
    ((FAILED++))
    VARIETY_ID="1"
fi
echo ""

# Test 7: Create Planting Event
echo "=== Test 7: Create Planting Event ==="
PLANTING_RESPONSE=$(curl -s -X POST "$API_URL/api/plantings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"garden_id\": $GARDEN_ID,
    \"plant_variety_id\": $VARIETY_ID,
    \"planted_date\": \"2026-02-01\",
    \"plant_count\": 3
  }")

if echo "$PLANTING_RESPONSE" | grep -q "id"; then
    echo -e "Create planting: ${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "Create planting: ${RED}✗ FAIL${NC}"
    echo "Response: $PLANTING_RESPONSE"
    ((FAILED++))
fi
echo ""

# Test 8: Get Rule Insights (Advisory Mode)
echo "=== Test 8: Get Rule Insights (Advisory Mode) ==="
INSIGHTS_RESPONSE=$(curl -s -X GET "$API_URL/api/rule-insights/garden/$GARDEN_ID" \
  -H "Authorization: Bearer $TOKEN")

if echo "$INSIGHTS_RESPONSE" | grep -q "watering"; then
    echo -e "Get rule insights: ${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "Get rule insights: ${YELLOW}⚠ WARN${NC} (may be expected if no rules match)"
    echo "Response: $INSIGHTS_RESPONSE"
fi
echo ""

# Test 9: Dashboard Endpoint
echo "=== Test 9: Dashboard Endpoint ==="
run_test "Dashboard data" "curl -s -H 'Authorization: Bearer $TOKEN' $API_URL/api/dashboard" "gardens"
echo ""

# Test 10: Metrics Endpoint
echo "=== Test 10: Metrics Endpoint (Prometheus) ==="
run_test "Prometheus metrics" "curl -s $API_URL/metrics" "http_requests_total"
echo ""

# Summary
echo "=== Test Results ==="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All smoke tests passed! 🎉${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Check the output above for details.${NC}"
    exit 1
fi
