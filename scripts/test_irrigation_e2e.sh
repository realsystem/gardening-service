#!/bin/bash

# End-to-End Irrigation System Test
# Automatically cleans up, creates test user, runs tests, and cleans up again

set -e

echo "================================================"
echo "Irrigation System End-to-End Test"
echo "================================================"
echo ""

# Step 1: Cleanup any existing test user
echo "Step 1: Cleaning up existing test user..."
./scripts/cleanup_test_user_auto.sh
echo ""

# Step 2: Create fresh test user
echo "Step 2: Creating fresh test user..."
./scripts/setup_test_user.sh
echo ""

# Step 3: Run quick test
echo "Step 3: Running quick smoke test..."
echo "================================================"
./scripts/quick_test_irrigation.sh
echo ""

# Step 4: Ask if user wants to run full test suite
read -p "Run full test suite? (yes/no): " -r
echo ""

if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Step 4: Running full test suite..."
    echo "================================================"
    ./scripts/test_irrigation_api.sh
fi

echo ""
echo "================================================"
echo "End-to-End Test Complete!"
echo "================================================"
echo ""
echo "To cleanup the test user:"
echo "  ./scripts/cleanup_test_user.sh"
