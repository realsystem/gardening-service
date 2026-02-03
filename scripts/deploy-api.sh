#!/bin/bash
# Fully Automated API Deployment to Fly.io
# Usage: ./scripts/deploy-api.sh [--auto]
#
# This script automatically:
# - Creates app if it doesn't exist
# - Creates database if it doesn't exist
# - Attaches database if not attached
# - Generates and sets secrets if not set
# - Deploys the application

set -e  # Exit on error

echo "=== Gardening Service API Deployment ==="
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

# Verify we're in the project root
if [ ! -f "fly.toml" ]; then
    echo -e "${RED}Error: fly.toml not found${NC}"
    echo "Run this script from the project root directory"
    exit 1
fi

# Get configuration from fly.toml
APP_NAME=$(grep -E "^app\s*=\s*\"" fly.toml | cut -d'"' -f2)
REGION=$(grep -E "^primary_region\s*=\s*\"" fly.toml | cut -d'"' -f2)
DB_NAME="gardening-db"

if [ -z "$APP_NAME" ]; then
    echo -e "${RED}Error: App name not set in fly.toml${NC}"
    echo "Edit fly.toml and set: app = \"your-app-name\""
    exit 1
fi

echo -e "${BLUE}Target App: $APP_NAME${NC}"
echo -e "${BLUE}Region: $REGION${NC}"
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
# STEP 2: Ensure Database Exists
# ============================================================================
echo "=== Step 2: Database Setup ==="
echo -n "Checking if database exists... "

if flyctl apps list 2>/dev/null | grep -q "^$DB_NAME"; then
    echo -e "${GREEN}✓ Database exists${NC}"
else
    echo -e "${YELLOW}⚠ Database does not exist${NC}"
    echo ""
    echo "Creating Postgres database: $DB_NAME"
    echo "  Region: $REGION"
    echo "  Size: 1GB"
    echo "  VM: shared-cpu-1x (~$2/month)"
    echo ""

    if [ "$AUTO_MODE" = false ]; then
        read -p "Create database now? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Database creation skipped. Run manually:"
            echo "  flyctl postgres create --name $DB_NAME --region $REGION --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 1"
            exit 1
        fi
    fi

    if flyctl postgres create \
        --name "$DB_NAME" \
        --region "$REGION" \
        --initial-cluster-size 1 \
        --vm-size shared-cpu-1x \
        --volume-size 1; then
        echo -e "${GREEN}✓ Database created successfully${NC}"
    else
        echo -e "${RED}✗ Failed to create database${NC}"
        exit 1
    fi
fi
echo ""

# ============================================================================
# STEP 3: Ensure Database is Attached
# ============================================================================
echo "=== Step 3: Database Attachment ==="
echo -n "Checking if database is attached... "

if flyctl secrets list --app "$APP_NAME" 2>/dev/null | grep -q "DATABASE_URL"; then
    echo -e "${GREEN}✓ Database attached${NC}"
else
    echo -e "${YELLOW}⚠ Database not attached${NC}"
    echo ""
    echo "Attaching database to app..."

    if flyctl postgres attach "$DB_NAME" --app "$APP_NAME"; then
        echo -e "${GREEN}✓ Database attached successfully${NC}"
        echo "  DATABASE_URL secret has been set automatically"
    else
        echo -e "${RED}✗ Failed to attach database${NC}"
        exit 1
    fi
fi
echo ""

# ============================================================================
# STEP 4: Ensure Secrets are Set
# ============================================================================
echo "=== Step 4: Secrets Configuration ==="

# Check SECRET_KEY
echo -n "Checking SECRET_KEY... "
if flyctl secrets list --app "$APP_NAME" 2>/dev/null | grep -q "SECRET_KEY"; then
    echo -e "${GREEN}✓ SECRET_KEY is set${NC}"
else
    echo -e "${YELLOW}⚠ SECRET_KEY not set${NC}"
    echo ""
    echo "Generating and setting SECRET_KEY..."

    SECRET_KEY=$(openssl rand -hex 32)
    if flyctl secrets set SECRET_KEY="$SECRET_KEY" --app "$APP_NAME"; then
        echo -e "${GREEN}✓ SECRET_KEY set successfully${NC}"
    else
        echo -e "${RED}✗ Failed to set SECRET_KEY${NC}"
        exit 1
    fi
fi
echo ""

# ============================================================================
# STEP 5: Backup Database
# ============================================================================
echo "=== Step 5: Database Backup ==="
echo -n "Creating backup... "

if flyctl postgres backup create --app "$DB_NAME" 2>/dev/null; then
    echo -e "${GREEN}✓ Backup created${NC}"
else
    echo -e "${YELLOW}⚠ Backup failed (continuing anyway)${NC}"
fi
echo ""

# ============================================================================
# STEP 6: Summary and Confirmation
# ============================================================================
echo "=== Step 6: Deployment Summary ==="
echo "  App Name: $APP_NAME"
echo "  Region: $REGION"
echo "  Database: $DB_NAME (attached)"
echo "  Secrets: DATABASE_URL, SECRET_KEY"
echo "  Resources: 1 CPU, 512MB RAM"
echo "  Migration: Will run 'alembic upgrade head' before deployment"
echo ""

if [ "$AUTO_MODE" = false ]; then
    read -p "Deploy now? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled"
        exit 0
    fi
fi

echo ""
echo "=== Step 7: Deploying Application ==="

if flyctl deploy --app "$APP_NAME"; then
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           DEPLOYMENT SUCCESSFUL! 🚀                   ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Application URLs:${NC}"
    echo "  Main:    https://$APP_NAME.fly.dev"
    echo "  Health:  https://$APP_NAME.fly.dev/health"
    echo "  Docs:    https://$APP_NAME.fly.dev/docs"
    echo "  Metrics: https://$APP_NAME.fly.dev/metrics"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  Logs:    flyctl logs --app $APP_NAME"
    echo "  Status:  flyctl status --app $APP_NAME"
    echo "  SSH:     flyctl ssh console --app $APP_NAME"
    echo "  Scale:   flyctl scale count 2 --app $APP_NAME"
    echo ""

    # Test health endpoint
    echo "=== Step 8: Health Check ==="
    echo -n "Testing health endpoint... "
    sleep 5  # Wait for app to start

    if curl -s "https://$APP_NAME.fly.dev/health" | grep -q "healthy"; then
        echo -e "${GREEN}✓ API is healthy!${NC}"
        echo ""
        echo -e "${GREEN}Next steps:${NC}"
        echo "  1. Deploy frontend: ./scripts/deploy-frontend.sh"
        echo "  2. Run smoke tests: ./scripts/smoke-test.sh https://$APP_NAME.fly.dev"
    else
        echo -e "${RED}✗ Health check failed${NC}"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Check logs: flyctl logs --app $APP_NAME"
        echo "  2. Check status: flyctl status --app $APP_NAME"
        echo "  3. View releases: flyctl releases --app $APP_NAME"
    fi
else
    echo ""
    echo -e "${RED}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║           DEPLOYMENT FAILED ✗                         ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Check logs: flyctl logs --app $APP_NAME"
    echo "  2. Verify secrets: flyctl secrets list --app $APP_NAME"
    echo "  3. Check database: flyctl postgres connect --app $DB_NAME"
    echo "  4. Review config: cat fly.toml"
    exit 1
fi
