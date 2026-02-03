# Automated Deployment Guide

**One-Command Production Deployment**

The deployment scripts have been enhanced to fully automate the entire setup and deployment process.

---

## What's Automated

### API Deployment (`scripts/deploy-api.sh`)

✅ **Automatically handles:**
1. App creation (if doesn't exist)
2. Database creation (if doesn't exist)
3. Database attachment (if not attached)
4. Secret generation and configuration
5. Database backup before deployment
6. Application deployment
7. Health check verification

### Frontend Deployment (`scripts/deploy-frontend.sh`)

✅ **Automatically handles:**
1. App creation (if doesn't exist)
2. API URL validation
3. API health check (pre-deployment)
4. Application deployment
5. Frontend verification

---

## Quick Start (First Deployment)

### Prerequisites

```bash
# 1. Install Fly CLI
brew install flyctl

# 2. Login to Fly.io
flyctl auth login
```

### Deploy Everything

```bash
# From project root

# 1. Deploy API (creates everything automatically)
./scripts/deploy-api.sh

# 2. Deploy Frontend
./scripts/deploy-frontend.sh

# 3. Run smoke tests
./scripts/smoke-test.sh https://gardening-service-api.fly.dev
```

That's it! The scripts handle all the setup automatically.

---

## Interactive Mode (Default)

By default, scripts ask for confirmation at key steps:

```bash
./scripts/deploy-api.sh
```

**You'll be prompted to confirm:**
- Database creation (~$2/month cost)
- Final deployment

**Example output:**
```
=== Gardening Service API Deployment ===

Target App: gardening-service-api
Region: sjc

=== Step 1: App Setup ===
Checking if app exists... ⚠ App does not exist

Creating app: gardening-service-api
✓ App created successfully

=== Step 2: Database Setup ===
Checking if database exists... ⚠ Database does not exist

Creating Postgres database: gardening-db
  Region: sjc
  Size: 1GB
  VM: shared-cpu-1x (~$2/month)

Create database now? (y/N) y
✓ Database created successfully

=== Step 3: Database Attachment ===
Checking if database is attached... ⚠ Database not attached
✓ Database attached successfully

=== Step 4: Secrets Configuration ===
Checking SECRET_KEY... ⚠ SECRET_KEY not set
✓ SECRET_KEY set successfully

=== Step 5: Database Backup ===
✓ Backup created

=== Step 6: Deployment Summary ===
  App Name: gardening-service-api
  Database: gardening-db (attached)
  Secrets: DATABASE_URL, SECRET_KEY

Deploy now? (y/N) y

=== Step 7: Deploying Application ===
[deployment output]

╔═══════════════════════════════════════════════════════╗
║           DEPLOYMENT SUCCESSFUL! 🚀                   ║
╚═══════════════════════════════════════════════════════╝

=== Step 8: Health Check ===
✓ API is healthy!
```

---

## Fully Automated Mode

Skip all prompts with `--auto` flag:

```bash
# Deploy without any prompts
./scripts/deploy-api.sh --auto
./scripts/deploy-frontend.sh --auto
```

**Use cases:**
- CI/CD pipelines
- Automated deployments
- Scripted workflows

---

## What Gets Created

### First-Time API Deployment

The script creates:

| Resource | Name | Configuration | Monthly Cost |
|----------|------|---------------|--------------|
| Fly App | `gardening-service-api` | 1 CPU, 512MB RAM | ~$0 (scale-to-zero) |
| Postgres DB | `gardening-db` | 1 CPU, 1GB storage | ~$2.15 |
| Secret | `DATABASE_URL` | Auto-generated | Free |
| Secret | `SECRET_KEY` | 64-char hex | Free |

**Total first-time cost:** ~$2-3/month

### First-Time Frontend Deployment

The script creates:

| Resource | Name | Configuration | Monthly Cost |
|----------|------|---------------|--------------|
| Fly App | `gardening-service-ui` | 1 CPU, 256MB RAM | ~$0 (scale-to-zero) |

**Total cost:** ~$0 (auto-stops when idle)

---

## Script Features

### Smart Checks

Both scripts perform intelligent pre-flight checks:

**API Script Checks:**
- ✅ Fly CLI installed
- ✅ Authenticated with Fly.io
- ✅ App exists (creates if not)
- ✅ Database exists (creates if not)
- ✅ Database attached (attaches if not)
- ✅ Secrets configured (generates if not)
- ✅ Backup created before deployment

**Frontend Script Checks:**
- ✅ Fly CLI installed
- ✅ Authenticated with Fly.io
- ✅ App exists (creates if not)
- ✅ API URL configured
- ✅ API URL format valid
- ✅ API is reachable (optional check)

### Idempotent Operations

Scripts are safe to run multiple times:
- Won't recreate existing apps
- Won't recreate existing database
- Won't re-set existing secrets
- Always safe to re-run

### Error Handling

Scripts fail fast with clear error messages:
- Missing Fly CLI → Installation instructions
- Not authenticated → Login instructions
- App creation fails → Error details
- Deployment fails → Troubleshooting steps

---

## Subsequent Deployments

After first deployment, scripts are even faster:

```bash
# Just deploy (everything already exists)
./scripts/deploy-api.sh
```

**Output:**
```
=== Step 1: App Setup ===
✓ App exists

=== Step 2: Database Setup ===
✓ Database exists

=== Step 3: Database Attachment ===
✓ Database attached

=== Step 4: Secrets Configuration ===
✓ SECRET_KEY is set

=== Step 5: Database Backup ===
✓ Backup created

Deploy now? (y/N) y

[deploys immediately]
```

---

## Manual Setup (Alternative)

If you prefer manual setup instead of using scripts:

```bash
# 1. Create app
flyctl apps create gardening-service-api --org personal

# 2. Create database
flyctl postgres create \
  --name gardening-db \
  --region sjc \
  --initial-cluster-size 1 \
  --vm-size shared-cpu-1x \
  --volume-size 1

# 3. Attach database
flyctl postgres attach gardening-db --app gardening-service-api

# 4. Set secrets
flyctl secrets set SECRET_KEY="$(openssl rand -hex 32)" --app gardening-service-api

# 5. Deploy
flyctl deploy --app gardening-service-api
```

---

## Configuration

Scripts read configuration from `fly.toml` files:

**API (`fly.toml`):**
```toml
app = "gardening-service-api"
primary_region = "sjc"
```

**Frontend (`frontend/fly.toml`):**
```toml
app = "gardening-service-ui"
primary_region = "sjc"

[build.args]
  VITE_API_URL = "https://gardening-service-api.fly.dev"
```

**To customize:**
1. Edit app names in `fly.toml` files
2. Update region if needed
3. Run scripts (they read the config automatically)

---

## Troubleshooting

### "flyctl: command not found"

**Solution:**
```bash
brew install flyctl
```

### "Not authenticated with Fly.io"

**Solution:**
```bash
flyctl auth login
```

### "App name already taken"

**Solution:**
Edit `fly.toml` and change app name:
```toml
app = "your-unique-name-here"
```

### "Database creation failed"

**Possible causes:**
- Insufficient credits/quota
- Invalid region
- Network issues

**Solution:**
Check Fly.io dashboard and billing settings.

### Deployment fails with "release command failed"

**Cause:** Database migration error

**Solution:**
```bash
# Check logs
flyctl logs --app gardening-service-api

# SSH and debug
flyctl ssh console --app gardening-service-api
alembic current
alembic history
```

---

## CI/CD Integration

Use `--auto` mode in CI/CD pipelines:

**GitHub Actions Example:**
```yaml
name: Deploy to Fly.io

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Fly CLI
        uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Deploy API
        run: ./scripts/deploy-api.sh --auto
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

      - name: Deploy Frontend
        run: ./scripts/deploy-frontend.sh --auto
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

      - name: Run Smoke Tests
        run: ./scripts/smoke-test.sh https://gardening-service-api.fly.dev
```

---

## Cost Monitoring

Monitor your costs in Fly.io dashboard:

```bash
# Open dashboard
flyctl dashboard

# Check current usage
flyctl apps list
flyctl postgres list
```

**Expected costs:**
- Development: ~$2-3/month
- Production (single instance): ~$8/month
- Production (HA): ~$17/month

---

## Next Steps

After successful deployment:

1. **Verify deployment:**
   ```bash
   ./scripts/smoke-test.sh https://gardening-service-api.fly.dev
   ```

2. **Open frontend:**
   ```bash
   flyctl open --app gardening-service-ui
   ```

3. **Monitor logs:**
   ```bash
   flyctl logs --app gardening-service-api
   ```

4. **Set up custom domain** (optional):
   ```bash
   flyctl certs create yourdomain.com --app gardening-service-api
   ```

5. **Enable CI/CD** for automatic deployments

---

## Summary

**Before automation:**
- 10+ manual commands
- Easy to miss steps
- Requires Fly.io documentation
- Error-prone

**With automation:**
- 1 command: `./scripts/deploy-api.sh`
- All setup handled automatically
- Clear progress messages
- Safe to re-run

**Time saved:** 10-15 minutes per deployment

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-02  
**See Also:** [Complete Deployment Guide](flyio.md), [Quick Start](QUICK_START.md)
