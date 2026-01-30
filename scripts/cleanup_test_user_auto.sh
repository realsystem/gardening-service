#!/bin/bash

# Automated Test User Cleanup (no confirmation)
# Uses API endpoint DELETE /users/me to delete user and all associated data

# Configuration
API_URL="http://localhost:8080"
EMAIL="${TEST_EMAIL:-test@example.com}"
PASSWORD="${TEST_PASSWORD:-password123}"

# Login
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/users/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"${EMAIL}\", \"password\": \"${PASSWORD}\"}" 2>/dev/null)

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "No test user to clean up (or login failed)"
    exit 0
fi

# Delete user
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "${API_URL}/users/me" \
  -H "Authorization: Bearer ${TOKEN}")

if [ "$HTTP_CODE" = "204" ]; then
    echo "Test user '$EMAIL' deleted"
else
    echo "Failed to delete test user (HTTP $HTTP_CODE)"
    exit 1
fi
