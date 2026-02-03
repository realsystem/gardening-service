#!/bin/bash
# Fully Automated Frontend Deployment to Fly.io
# Usage: ./scripts/deploy-frontend.sh [--auto]
#
# This script automatically:
# - Creates app if it doesn't exist
# - Verifies API URL configuration
# - Deploys the frontend application

set -e  # Exit on error

echo "=== Gardening Service Frontend Deployment ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
AUTO_MODE=false
if [[ "$1" == "--auto" ]]; then
    AUTO_MODE=true
fi

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo -e "${RED}Error: flyctl is not installed${NC}"
    echo "Install with: brew install flyctl"
    exit 1
fi

# Check if authenticated
if ! flyctl auth whoami &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with Fly.io${NC}"
    echo "Run: flyctl auth login"
    exit 1
fi

# Navigate to frontend directory
if [ ! -d "frontend" ]; then
    echo -e "${RED}Error: frontend directory not found${NC}"
    echo "Run this script from the project root directory"
    exit 1
fi

cd frontend

# Verify fly.toml exists
if [ ! -f "fly.toml" ]; then
    echo -e "${RED}Error: fly.toml not found in frontend directory${NC}"
    exit 1
fi

# Get configuration from fly.toml
APP_NAME=$(grep -E "^app\s*=\s*\"" fly.toml | cut -d'"' -f2)
REGION=$(grep -E "^primary_region\s*=\s*\"" fly.toml | cut -d'"' -f2)
API_URL=$(grep -A2 "\[build.args\]" fly.toml | grep VITE_API_URL | cut -d'"' -f2)

if [ -z "$APP_NAME" ]; then
    echo -e "${RED}Error: App name not set in frontend/fly.toml${NC}"
    echo "Edit frontend/fly.toml and set: app = \"your-frontend-app-name\""
    exit 1
fi

echo -e "${BLUE}Target App: $APP_NAME${NC}"
echo -e "${BLUE}Region: $REGION${NC}"
echo -e "${BLUE}API URL: $API_URL${NC}"
echo ""

# ============================================================================
# STEP 1: Ensure App Exists
# ============================================================================
echo "=== Step 1: App Setup ==="
echo -n "Checking if app exists... "

if flyctl apps list 2>/dev/null | grep -q "^$APP_NAME"; then
    echo -e "${GREEN}✓ App exists${NC}"
else
    echo -e "${YELLOW}⚠ App does not exist${NC}"
    echo ""
    echo "Creating app: $APP_NAME"

    if flyctl apps create "$APP_NAME" --org personal; then
        echo -e "${GREEN}✓ App created successfully${NC}"
    else
        echo -e "${RED}✗ Failed to create app${NC}"
        exit 1
    fi
fi
echo ""

# ============================================================================
# STEP 2: Verify API URL Configuration
# ============================================================================
echo "=== Step 2: Configuration Validation ==="

if [ -z "$API_URL" ]; then
    echo -e "${RED}✗ VITE_API_URL not set in fly.toml${NC}"
    echo ""
    echo "Edit frontend/fly.toml and set:"
    echo "  [build.args]"
    echo "    VITE_API_URL = \"https://your-api-app.fly.dev\""
    exit 1
else
    echo -e "${GREEN}✓ VITE_API_URL is configured${NC}"
    echo "  API URL: $API_URL"

    # Verify API URL format
    if [[ ! "$API_URL" =~ ^https:// ]]; then
        echo -e "${YELLOW}⚠ Warning: API URL should start with https://${NC}"
    fi

    # Check if API is reachable (optional)
    echo -n "  Checking API health... "
    if curl -s --max-time 5 "$API_URL/health" 2>/dev/null | grep -q "healthy"; then
        echo -e "${GREEN}✓ API is healthy${NC}"
    else
        echo -e "${YELLOW}⚠ API not responding (may not be deployed yet)${NC}"
    fi
fi
echo ""

# ============================================================================
# STEP 3: Summary and Confirmation
# ============================================================================
echo "=== Step 3: Deployment Summary ==="
echo "  App Name: $APP_NAME"
echo "  Region: $REGION"
echo "  API URL: $API_URL"
echo "  Resources: 1 CPU, 256MB RAM"
echo "  Build: Vite production build → nginx"
echo ""

if [ "$AUTO_MODE" = false ]; then
    read -p "Deploy now? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled"
        cd ..
        exit 0
    fi
fi

echo ""
echo "=== Step 4: Deploying Frontend ==="

# Deploy
if flyctl deploy --app "$APP_NAME"; then
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║       FRONTEND DEPLOYMENT SUCCESSFUL! 🎉              ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Application URL:${NC}"
    echo "  Main:   https://$APP_NAME.fly.dev"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  Logs:   flyctl logs --app $APP_NAME"
    echo "  Status: flyctl status --app $APP_NAME"
    echo "  Open:   flyctl open --app $APP_NAME"
    echo ""

    # Test if frontend loads
    echo "=== Step 5: Frontend Check ==="
    echo -n "Testing frontend... "
    sleep 3  # Wait for app to start

    if curl -s "https://$APP_NAME.fly.dev" | grep -q "<title>"; then
        echo -e "${GREEN}✓ Frontend is serving!${NC}"
        echo ""
        echo -e "${GREEN}Next steps:${NC}"
        echo "  1. Open in browser: https://$APP_NAME.fly.dev"
        echo "  2. Run smoke tests: ./scripts/smoke-test.sh $API_URL"
        echo "  3. Monitor logs: flyctl logs --app $APP_NAME"
    else
        echo -e "${RED}✗ Frontend not responding${NC}"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Check logs: flyctl logs --app $APP_NAME"
        echo "  2. Check status: flyctl status --app $APP_NAME"
        echo "  3. Verify build: Check for build errors in logs"
    fi
else
    echo ""
    echo -e "${RED}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║       FRONTEND DEPLOYMENT FAILED ✗                    ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Check logs: flyctl logs --app $APP_NAME"
    echo "  2. Verify config: cat fly.toml"
    echo "  3. Check API URL: Ensure VITE_API_URL is correct"
    echo "  4. Review build errors in logs"
    cd ..
    exit 1
fi

cd ..
