# Fly.io Deployment Guide - Gardening Service Platform

**Production-Ready Deployment Configuration**

This guide provides step-by-step instructions for deploying the Gardening Service platform to Fly.io with proper database management, secrets handling, health checks, and rollback procedures.

---

## Table of Contents

1. [Platform Overview](#platform-overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Initial Setup](#initial-setup)
5. [Database Setup](#database-setup)
6. [Secrets Configuration](#secrets-configuration)
7. [Deployment Process](#deployment-process)
8. [Health Verification](#health-verification)
9. [Smoke Tests](#smoke-tests)
10. [Rollback Procedures](#rollback-procedures)
11. [Common Failures](#common-failures)
12. [Cost Expectations](#cost-expectations)
13. [Maintenance & Operations](#maintenance--operations)

---

## Platform Overview

### Why Fly.io?

**Deployment Architecture:**
- **API Backend**: FastAPI application with auto-scaling
- **Frontend UI**: Static Vite build served by nginx
- **Database**: Managed Postgres with automatic backups
- **Secrets**: Encrypted secret management
- **SSL**: Automatic HTTPS with free certificates

**Key Features:**
- ✅ Global edge deployment with auto-scaling
- ✅ Automatic HTTPS/SSL certificates
- ✅ Managed Postgres with daily backups
- ✅ Scale-to-zero for cost optimization
- ✅ Rolling deployments with health checks
- ✅ Built-in metrics and monitoring
- ✅ Simple rollback with version history

---

## Prerequisites

### 1. Install Fly CLI

```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows (PowerShell)
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

Verify installation:
```bash
flyctl version
```

### 2. Create Fly.io Account

```bash
fly auth signup
# Or if you already have an account:
fly auth login
```

### 3. Verify Prerequisites

Ensure you have:
- [ ] Fly CLI installed and authenticated
- [ ] Git repository cloned locally
- [ ] Docker installed (for local testing)
- [ ] Access to the project root directory

---

## Architecture

### Application Structure

```
gardening-service/
├── fly.toml                 # API backend configuration
├── Dockerfile               # API backend Docker image
├── start.sh                 # API startup script (migrations + server)
├── alembic.ini             # Database migration configuration
├── migrations/             # Alembic migration files
│   └── versions/           # Version-controlled schema changes
├── frontend/
│   ├── fly.toml            # Frontend configuration
│   └── Dockerfile          # Frontend Docker image (nginx)
└── docs/
    └── deployment/
        └── flyio.md        # This file
```

### Deployment Flow

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   API App   │─────▶│  Fly Postgres│◀─────│ Frontend App│
│  (FastAPI)  │      │  (Managed DB)│      │   (nginx)   │
└─────────────┘      └──────────────┘      └─────────────┘
      │                      │                     │
      └──────────────────────┴─────────────────────┘
                       Fly.io Global Network
```

---

## Initial Setup

### Step 1: Prepare Configuration

The project includes pre-configured `fly.toml` files:

**API Backend** (`fly.toml`):
- App name: `gardening-service-api`
- Region: `sjc` (San Jose)
- Port: 8080
- Resources: 1 CPU, 512MB RAM
- Auto-scaling: Enabled
- Health checks: `/health` endpoint
- Release command: `alembic upgrade head` (runs migrations)

**Frontend UI** (`frontend/fly.toml`):
- App name: `gardening-service-ui`
- Region: `sjc` (San Jose)
- Port: 3000
- Resources: 1 CPU, 256MB RAM
- Auto-scaling: Enabled

### Step 2: Customize App Names (Optional)

Edit app names in `fly.toml` and `frontend/fly.toml` if needed:

```toml
app = "your-custom-api-name"
```

```toml
app = "your-custom-frontend-name"
```

**IMPORTANT**: If you change the API app name, update the frontend's `VITE_API_URL`:

```toml
# frontend/fly.toml
[build.args]
  VITE_API_URL = "https://your-custom-api-name.fly.dev"
```

### Step 3: Choose Region

Update `primary_region` in both `fly.toml` files:

**Available Regions:**
- `sjc` - San Jose, California
- `lax` - Los Angeles, California
- `ord` - Chicago, Illinois
- `iad` - Ashburn, Virginia
- `lhr` - London, United Kingdom
- `fra` - Frankfurt, Germany
- `nrt` - Tokyo, Japan
- `syd` - Sydney, Australia

---

## Database Setup

### Step 1: Create Fly Postgres Cluster

```bash
# Create a Postgres cluster in the same region as your API
fly postgres create \
  --name gardening-db \
  --region sjc \
  --initial-cluster-size 1 \
  --vm-size shared-cpu-1x \
  --volume-size 1
```

**Options Explained:**
- `--name`: Database cluster name
- `--region`: Must match API region for low latency
- `--initial-cluster-size 1`: Single instance (dev/staging)
- `--vm-size shared-cpu-1x`: ~$2/month shared CPU
- `--volume-size 1`: 1GB storage ($0.15/month)

**Production Recommendation:**
For production, use `--initial-cluster-size 2` for high availability:
```bash
fly postgres create \
  --name gardening-db-prod \
  --region sjc \
  --initial-cluster-size 2 \
  --vm-size shared-cpu-1x \
  --volume-size 3
```

### Step 2: Attach Database to API App

```bash
# Attach Postgres to the API app
fly postgres attach gardening-db --app gardening-service-api
```

This command:
- ✅ Creates a database named after your app
- ✅ Sets `DATABASE_URL` secret automatically
- ✅ Configures SSL connection
- ✅ Creates a dedicated user with proper permissions

### Step 3: Verify Database Connection

```bash
# Check database connection string (redacted)
fly secrets list --app gardening-service-api

# Connect to database directly (for debugging)
fly postgres connect --app gardening-db
```

### Step 4: SSL Enforcement

Fly Postgres enforces SSL by default. Verify your connection string:

```bash
# Should contain sslmode=require or sslmode=verify-full
fly ssh console --app gardening-service-api -C "echo \$DATABASE_URL"
```

Expected format:
```
postgres://user:password@db-hostname.internal:5432/dbname?sslmode=require
```

---

## Secrets Configuration

### Required Secrets

| Secret Name | Description | How to Generate |
|------------|-------------|-----------------|
| `DATABASE_URL` | Postgres connection string | Auto-set by `fly postgres attach` |
| `SECRET_KEY` | JWT signing key (HS256) | `openssl rand -hex 32` |

### Optional Secrets

| Secret Name | Description | Example |
|------------|-------------|---------|
| `ADMIN_BOOTSTRAP_EMAIL` | Initial admin user email | `admin@example.com` |

### Step 1: Generate SECRET_KEY

```bash
# Generate a cryptographically secure random key
openssl rand -hex 32
```

Output example: `a7f3e9c8b2d4f6e1a9c3d5b7e2f4a6c8d1e3f5a7b9c2d4e6f8a1c3e5b7d9f2`

### Step 2: Set Secrets

```bash
# Set JWT secret key
fly secrets set SECRET_KEY="$(openssl rand -hex 32)" --app gardening-service-api

# Optional: Set admin bootstrap email
fly secrets set ADMIN_BOOTSTRAP_EMAIL="admin@yourdomain.com" --app gardening-service-api
```

**CRITICAL SECURITY RULES:**
- ❌ NEVER commit secrets to git
- ❌ NEVER log secrets in application code
- ❌ NEVER share secrets in chat/email
- ✅ Generate unique secrets per environment
- ✅ Rotate secrets periodically
- ✅ Use `fly secrets set` exclusively

### Step 3: Verify Secrets

```bash
# List all secrets (values are redacted)
fly secrets list --app gardening-service-api
```

Expected output:
```
NAME                    DIGEST                  CREATED AT
DATABASE_URL            a7f3e9c8b2d4f6e1a9c3    2026-02-02T18:00:00Z
SECRET_KEY              d1e3f5a7b9c2d4e6f8a1    2026-02-02T18:01:00Z
ADMIN_BOOTSTRAP_EMAIL   c3e5b7d9f2a4c6e8d1f3    2026-02-02T18:02:00Z
```

### Step 4: Remove Secrets (If Needed)

```bash
# Remove a secret
fly secrets unset SECRET_NAME --app gardening-service-api
```

---

## Deployment Process

### Step 1: Deploy API Backend

```bash
# Navigate to project root
cd /path/to/gardening-service

# Deploy the API (first deployment or updates)
fly deploy
```

**What Happens:**
1. Fly.io builds Docker image from `Dockerfile`
2. Image is pushed to Fly.io registry
3. Release command runs: `alembic upgrade head` (migrations)
4. New instance starts with rolling deployment
5. Health checks verify `/health` endpoint
6. Old instance shuts down after health checks pass

**Expected Output:**
```
==> Building image
...
==> Pushing image
...
==> Running release command: alembic upgrade head
INFO  [alembic.runtime.migration] Running upgrade -> c001108a6d8e, Initial schema
INFO  [alembic.runtime.migration] Running upgrade c001108a6d8e -> a1b2c3d4e5f6, add_user_profiles
...
==> Deploying
...
--> v1 deployed successfully
```

### Step 2: Verify API Deployment

```bash
# Check app status
fly status --app gardening-service-api

# View logs
fly logs --app gardening-service-api

# Test health endpoint
curl https://gardening-service-api.fly.dev/health
```

Expected response:
```json
{"status": "healthy"}
```

### Step 3: Deploy Frontend UI

```bash
# Navigate to frontend directory
cd frontend

# Deploy the frontend
fly deploy
```

**What Happens:**
1. Vite build runs with `VITE_API_URL` from `fly.toml`
2. Static assets are built into Docker image
3. nginx serves static files
4. Rolling deployment with health checks

**Expected Output:**
```
==> Building image
...
Build arg: VITE_API_URL=https://gardening-service-api.fly.dev
...
==> Deploying
...
--> v1 deployed successfully
```

### Step 4: Verify Frontend Deployment

```bash
# Check app status
fly status --app gardening-service-ui

# Open in browser
fly open --app gardening-service-ui
```

---

## Health Verification

### Automated Health Checks

Fly.io automatically monitors:

**API Backend:**
- HTTP check: `GET /health` every 30 seconds
- Expected: 2xx status code
- Grace period: 10 seconds after deployment

**Frontend UI:**
- HTTP check: `GET /` every 30 seconds
- Expected: 2xx status code (nginx serves index.html)
- Grace period: 5 seconds after deployment

### Manual Health Verification

```bash
# 1. Check API health endpoint
curl https://gardening-service-api.fly.dev/health

# Expected: {"status": "healthy"}

# 2. Check API docs
curl https://gardening-service-api.fly.dev/docs

# Expected: HTML with OpenAPI documentation

# 3. Check frontend loads
curl https://gardening-service-ui.fly.dev

# Expected: HTML with React app

# 4. Check database connectivity
fly ssh console --app gardening-service-api -C "python -c \"import psycopg2; psycopg2.connect('$DATABASE_URL'); print('DB OK')\""

# Expected: DB OK
```

### Monitoring Dashboard

```bash
# Open Fly.io dashboard
fly dashboard
```

Monitor:
- Instance health status
- Response times
- Error rates
- Resource usage (CPU, memory)
- Request volume

---

## Smoke Tests

After deployment, perform these critical smoke tests to verify functionality:

### 1. User Registration

```bash
# Register a new user
curl -X POST https://gardening-service-api.fly.dev/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "zip_code": "94102"
  }'
```

Expected: `201 Created` with user object

### 2. User Login

```bash
# Login to get JWT token
curl -X POST https://gardening-service-api.fly.dev/api/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=SecurePassword123!"
```

Expected: `{"access_token": "eyJ...", "token_type": "bearer"}`

Save the token:
```bash
TOKEN="<access_token_from_response>"
```

### 3. Create Garden

```bash
# Create a garden
curl -X POST https://gardening-service-api.fly.dev/api/gardens \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Test Garden",
    "garden_type": "outdoor",
    "size_sq_ft": 100
  }'
```

Expected: `201 Created` with garden object

### 4. Get Plant Varieties

```bash
# Fetch available plants
curl https://gardening-service-api.fly.dev/api/plant-varieties \
  -H "Authorization: Bearer $TOKEN"
```

Expected: `200 OK` with array of plant varieties

### 5. Create Planting Event

```bash
# Add a plant to the garden
curl -X POST https://gardening-service-api.fly.dev/api/plantings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "garden_id": 1,
    "plant_variety_id": 1,
    "planted_date": "2026-02-01",
    "plant_count": 3
  }'
```

Expected: `201 Created` with planting event

### 6. Verify Feature Gating

```bash
# Check rule insights (should work for all users)
curl https://gardening-service-api.fly.dev/api/rule-insights/garden/1 \
  -H "Authorization: Bearer $TOKEN"
```

Expected: `200 OK` with watering/care recommendations (advisory mode)

### 7. Frontend Smoke Test

Open https://gardening-service-ui.fly.dev and verify:
- [ ] Login page loads
- [ ] Registration works
- [ ] Dashboard shows after login
- [ ] Gardens can be created
- [ ] Plants can be added
- [ ] API calls work (check browser console)

---

## Rollback Procedures

### Why Rollback?

Rollback if:
- Deployment causes runtime errors
- Database migration fails
- Health checks fail repeatedly
- Performance degrades significantly
- Security vulnerability discovered

### Quick Rollback (Last Working Version)

```bash
# Rollback API to previous version
fly releases --app gardening-service-api
# Note the version number of the last working release (e.g., v5)

fly deploy --image registry.fly.io/gardening-service-api:v5 --app gardening-service-api
```

### Database Migration Rollback

**CRITICAL**: Alembic migrations are one-way by default. Rollback requires manual intervention.

#### Step 1: Identify Migration to Rollback

```bash
# SSH into API instance
fly ssh console --app gardening-service-api

# Check current migration version
alembic current

# Example output: c3d4e5f6g7h8 (head)
```

#### Step 2: Find Rollback Script

Check `migrations/` directory for rollback SQL:
```bash
ls migrations/rollback_*.sql
```

#### Step 3: Execute Rollback (if available)

```bash
# Connect to database
fly postgres connect --app gardening-db

# Execute rollback script
\i /path/to/rollback_script.sql

# Verify
\dt  -- List tables
```

#### Step 4: Downgrade Alembic Version

```bash
# SSH into API instance
fly ssh console --app gardening-service-api

# Downgrade to specific version
alembic downgrade <revision_id>

# Example:
alembic downgrade c001108a6d8e
```

### Full Rollback (Code + Database)

1. **Rollback code** to previous version
2. **Rollback database** using migration scripts
3. **Verify** with smoke tests
4. **Monitor** logs for errors

### Emergency Rollback

```bash
# Stop the problematic app immediately
fly scale count 0 --app gardening-service-api

# Rollback to last known good version
fly deploy --image registry.fly.io/gardening-service-api:v<last-good-version>

# Scale back up
fly scale count 1 --app gardening-service-api
```

---

## Common Failures

### 1. Migration Failure During Deployment

**Symptom:**
```
Error: Migration failed: ... violates foreign key constraint
Release command failed, deployment aborted
```

**Cause:** Database constraint violation in migration

**Solution:**
```bash
# SSH into API instance
fly ssh console --app gardening-service-api

# Check database for data issues
python -c "
from app.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
# Run diagnostic queries from migration guide
"

# Fix data issues, then redeploy
fly deploy
```

### 2. Health Check Failures

**Symptom:**
```
Health check failed: Connection refused on :8080/health
```

**Cause:** App didn't start or port mismatch

**Solution:**
```bash
# Check logs for startup errors
fly logs --app gardening-service-api

# Common issues:
# - DATABASE_URL not set: Run `fly postgres attach`
# - SECRET_KEY not set: Run `fly secrets set SECRET_KEY=...`
# - Port mismatch: Verify PORT=8080 in fly.toml
```

### 3. Database Connection Errors

**Symptom:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Cause:** Database not attached or SSL issue

**Solution:**
```bash
# Verify DATABASE_URL is set
fly secrets list --app gardening-service-api

# If missing, attach database
fly postgres attach gardening-db --app gardening-service-api

# Verify SSL mode
fly ssh console --app gardening-service-api -C "echo \$DATABASE_URL | grep sslmode"
```

### 4. Frontend Can't Reach API

**Symptom:** Frontend loads but API calls fail (CORS errors)

**Cause:** VITE_API_URL misconfigured or CORS not enabled

**Solution:**
```bash
# 1. Verify frontend build arg
cat frontend/fly.toml | grep VITE_API_URL
# Should match: https://gardening-service-api.fly.dev

# 2. Check CORS in API
curl -i https://gardening-service-api.fly.dev/health
# Should include: Access-Control-Allow-Origin: *

# 3. Rebuild frontend with correct API URL
cd frontend
fly deploy
```

### 5. Out of Memory Errors

**Symptom:**
```
Error: Container killed (OOM - Out of Memory)
```

**Cause:** Memory limit too low (256MB not enough)

**Solution:**
```bash
# Increase memory in fly.toml
# Edit: memory_mb = 512

# Redeploy
fly deploy
```

### 6. Secret Not Found

**Symptom:**
```
KeyError: 'SECRET_KEY'
Config validation failed
```

**Cause:** Required secret not set

**Solution:**
```bash
# Set missing secret
fly secrets set SECRET_KEY="$(openssl rand -hex 32)" --app gardening-service-api

# App will auto-restart with new secret
```

---

## Cost Expectations

### Monthly Cost Breakdown (Production)

**Scenario 1: Low Traffic (Scale-to-Zero)**

| Resource | Configuration | Cost/Month |
|----------|--------------|------------|
| API Backend | 1x shared-cpu-1x, 512MB, auto-stop | ~$0 (with free tier credits) |
| Frontend UI | 1x shared-cpu-1x, 256MB, auto-stop | ~$0 (with free tier credits) |
| Postgres DB | 1x shared-cpu-1x, 1GB volume | ~$2.15 |
| **TOTAL** | | **~$2.15/month** |

**Scenario 2: Medium Traffic (1 Instance Always On)**

| Resource | Configuration | Cost/Month |
|----------|--------------|------------|
| API Backend | 1x shared-cpu-1x, 512MB, 24/7 | ~$3.88 |
| Frontend UI | 1x shared-cpu-1x, 256MB, 24/7 | ~$1.94 |
| Postgres DB | 1x shared-cpu-1x, 3GB volume | ~$2.45 |
| **TOTAL** | | **~$8.27/month** |

**Scenario 3: Production (HA with 2 Instances)**

| Resource | Configuration | Cost/Month |
|----------|--------------|------------|
| API Backend | 2x shared-cpu-1x, 512MB, 24/7 | ~$7.76 |
| Frontend UI | 2x shared-cpu-1x, 256MB, 24/7 | ~$3.88 |
| Postgres DB | 2x shared-cpu-1x (HA), 10GB volume | ~$5.50 |
| **TOTAL** | | **~$17.14/month** |

### Cost Optimization Tips

1. **Use Auto-Stop for Development**
   ```toml
   auto_stop_machines = true
   auto_start_machines = true
   min_machines_running = 0
   ```

2. **Monitor Resource Usage**
   ```bash
   fly dashboard
   # Check CPU and memory usage
   # Scale down if underutilized
   ```

3. **Use Smaller Database for Dev**
   ```bash
   # Dev: 1GB volume
   fly postgres create --volume-size 1
   
   # Prod: Scale up as needed
   fly volumes extend <volume-id> --size 10
   ```

4. **Enable Metrics (Free Tier)**
   - 10M series
   - 13-month retention
   - No additional cost

### Free Tier Limits

Fly.io offers $5/month in free credits (trial), which covers:
- 3 shared-cpu-1x VMs with 256MB RAM
- 160GB outbound data transfer
- Enough for development and staging environments

**After free credits:**
- Pay only for what you use
- No minimum charges
- Prorated hourly billing

---

## Maintenance & Operations

### Viewing Logs

```bash
# Real-time logs
fly logs --app gardening-service-api

# Last 100 lines
fly logs --app gardening-service-api -n 100

# Filter by severity
fly logs --app gardening-service-api | grep ERROR
```

### SSH Access

```bash
# SSH into running instance
fly ssh console --app gardening-service-api

# Run a command
fly ssh console --app gardening-service-api -C "alembic current"
```

### Database Backups

```bash
# List backups (daily automatic backups)
fly postgres backups list --app gardening-db

# Create manual backup
fly postgres backup create --app gardening-db

# Restore from backup
fly postgres restore --app gardening-db --backup <backup-id>
```

### Scaling

```bash
# Scale instances (horizontal)
fly scale count 2 --app gardening-service-api

# Scale resources (vertical)
fly scale vm shared-cpu-2x --memory 1024 --app gardening-service-api

# Check current scaling
fly scale show --app gardening-service-api
```

### Monitoring

```bash
# Open Grafana dashboard
fly dashboard

# View metrics
fly metrics --app gardening-service-api

# Check instance health
fly status --app gardening-service-api
```

### Updating Secrets

```bash
# Update a secret (triggers app restart)
fly secrets set SECRET_KEY="$(openssl rand -hex 32)" --app gardening-service-api

# Remove a secret
fly secrets unset OLD_SECRET --app gardening-service-api
```

### Restarting App

```bash
# Restart all instances
fly apps restart gardening-service-api

# Restart specific instance
fly machine restart <machine-id> --app gardening-service-api
```

---

## Deployment Checklist

Use this checklist for each deployment:

### Pre-Deployment

- [ ] Code changes reviewed and tested locally
- [ ] Database migrations tested in staging
- [ ] Secrets configured (no secrets in code)
- [ ] Health checks passing locally
- [ ] Rollback plan documented

### Deployment

- [ ] Backup database before migration
  ```bash
  fly postgres backup create --app gardening-db
  ```
- [ ] Deploy API backend
  ```bash
  fly deploy
  ```
- [ ] Verify API health
  ```bash
  curl https://gardening-service-api.fly.dev/health
  ```
- [ ] Deploy frontend (if changed)
  ```bash
  cd frontend && fly deploy
  ```
- [ ] Monitor logs for errors
  ```bash
  fly logs --app gardening-service-api
  ```

### Post-Deployment

- [ ] Run smoke tests (see [Smoke Tests](#smoke-tests))
- [ ] Verify all critical features work
- [ ] Check error rates in dashboard
- [ ] Monitor performance metrics
- [ ] Document any issues or changes

---

## Support & Troubleshooting

### Fly.io Resources

- **Documentation**: https://fly.io/docs
- **Community Forum**: https://community.fly.io
- **Status Page**: https://status.fly.io

### Application Logs

```bash
# View structured logs
fly logs --app gardening-service-api

# Export logs for analysis
fly logs --app gardening-service-api > deployment.log
```

### Getting Help

1. Check this guide for common issues
2. Review application logs
3. Search Fly.io community forum
4. Open an issue in project repository
5. Contact Fly.io support (paid plans)

---

## Summary

**You have successfully deployed the Gardening Service platform to Fly.io!**

**Key URLs:**
- API: https://gardening-service-api.fly.dev
- Frontend: https://gardening-service-ui.fly.dev
- API Docs: https://gardening-service-api.fly.dev/docs
- Metrics: https://gardening-service-api.fly.dev/metrics

**Next Steps:**
1. Run smoke tests to verify functionality
2. Set up monitoring and alerts
3. Configure custom domain (optional)
4. Enable automatic deployments from CI/CD
5. Scale resources based on traffic

**Remember:**
- Database migrations run automatically on deploy
- Secrets are encrypted and never logged
- Health checks ensure zero-downtime deployments
- Auto-scaling saves costs when idle
- Backups are created daily automatically

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-02  
**Maintainer:** Infrastructure Team
