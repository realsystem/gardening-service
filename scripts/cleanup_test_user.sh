#!/bin/bash

# Cleanup Test User
# Uses API endpoint DELETE /users/me to delete user and all associated data

set -e

# Configuration
API_URL="http://localhost:8080"
EMAIL="${TEST_EMAIL:-test@example.com}"
PASSWORD="${TEST_PASSWORD:-password123}"

echo "Cleanup Test User"
echo "=================="
echo "Email: $EMAIL"
echo ""

# Confirm deletion
read -p "This will DELETE the user '$EMAIL' and ALL associated data. Continue? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/users/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"${EMAIL}\", \"password\": \"${PASSWORD}\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed - user may not exist or wrong password"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "✓ Login successful"
echo ""

echo "Deleting user account..."
DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "${API_URL}/users/me" \
  -H "Authorization: Bearer ${TOKEN}")

HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" = "204" ]; then
    echo ""
    echo "✅ User '$EMAIL' deleted successfully!"
    echo ""
    echo "All associated data has been removed:"
    echo "  - User account"
    echo "  - All gardens"
    echo "  - All planting events"
    echo "  - All care tasks"
    echo "  - All seed batches"
    echo "  - All soil samples"
    echo "  - All irrigation zones, sources, and watering events"
    echo "  - All sensor readings"
    echo "  - All lands"
    echo ""
    echo "You can create a fresh test user with:"
    echo "  ./scripts/setup_test_user.sh"
else
    echo ""
    echo "❌ Failed to delete user (HTTP $HTTP_CODE)"
    echo "Response: $DELETE_RESPONSE"
    exit 1
fi
