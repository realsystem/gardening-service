#!/bin/bash

# Setup Test User for Irrigation API Tests

API_URL="http://localhost:8080"
EMAIL="${TEST_EMAIL:-test@example.com}"
PASSWORD="${TEST_PASSWORD:-password123}"

echo "Creating Test User"
echo "=================="
echo "Email: $EMAIL"
echo ""

# Create user
RESPONSE=$(curl -s -X POST "${API_URL}/users" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"${EMAIL}\", \"password\": \"${PASSWORD}\"}")

# Check if successful
if echo "$RESPONSE" | grep -q "id"; then
    echo "✅ Test user created successfully!"
    echo ""
    echo "Response:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    echo "You can now run the test scripts:"
    echo "  ./scripts/quick_test_irrigation.sh"
    echo "  ./scripts/test_irrigation_api.sh"
else
    echo "Response:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""

    if echo "$RESPONSE" | grep -q "already registered"; then
        echo "ℹ️  User already exists - you can proceed with testing"
    else
        echo "❌ Failed to create user"
        echo ""
        echo "Possible issues:"
        echo "  - API is not running (run: docker-compose up -d)"
        echo "  - Database connection issue"
    fi
fi
