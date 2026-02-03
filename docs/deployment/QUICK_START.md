# Fly.io Deployment - Quick Start Guide

**5-Minute Production Deployment**

---

## Prerequisites Checklist

- [ ] Fly CLI installed (`brew install flyctl`)
- [ ] Fly.io account created (`fly auth signup`)
- [ ] Project cloned locally
- [ ] Docker installed (optional, for local testing)

---

## Step-by-Step Deployment

### 1. Install and Login (One-Time Setup)

```bash
# Install Fly CLI
brew install flyctl

# Login to Fly.io
fly auth login
```

### 2. Create Database

```bash
# Create Postgres cluster
fly postgres create \
  --name gardening-db \
  --region sjc \
  --initial-cluster-size 1 \
  --vm-size shared-cpu-1x \
  --volume-size 1
```

**Cost:** ~$2.15/month

### 3. Configure App Names

Edit `fly.toml`:
```toml
app = "your-api-name"  # Must be globally unique
```

Edit `frontend/fly.toml`:
```toml
app = "your-frontend-name"  # Must be globally unique

[build.args]
  VITE_API_URL = "https://your-api-name.fly.dev"
```

### 4. Deploy API Backend

```bash
# From project root

# Attach database (auto-sets DATABASE_URL)
fly postgres attach gardening-db --app your-api-name

# Set JWT secret
fly secrets set SECRET_KEY="$(openssl rand -hex 32)" --app your-api-name

# Deploy
fly deploy
```

**Deployment time:** 2-3 minutes

### 5. Deploy Frontend

```bash
# From project root
cd frontend

# Deploy
fly deploy
```

**Deployment time:** 1-2 minutes

### 6. Verify Deployment

```bash
# Check API health
curl https://your-api-name.fly.dev/health

# Expected: {"status":"healthy"}

# Open frontend
fly open --app your-frontend-name
```

### 7. Run Smoke Tests

```bash
# From project root
./scripts/smoke-test.sh https://your-api-name.fly.dev
```

---

## URLs

After deployment, your services will be available at:

- **API**: `https://your-api-name.fly.dev`
- **API Docs**: `https://your-api-name.fly.dev/docs`
- **Frontend**: `https://your-frontend-name.fly.dev`
- **Metrics**: `https://your-api-name.fly.dev/metrics`

---

## Common Commands

```bash
# View logs
fly logs --app your-api-name

# Check status
fly status --app your-api-name

# SSH into instance
fly ssh console --app your-api-name

# Scale resources
fly scale vm shared-cpu-2x --memory 1024 --app your-api-name

# Restart app
fly apps restart your-api-name

# Create database backup
fly postgres backup create --app gardening-db
```

---

## Rollback

```bash
# View release history
fly releases --app your-api-name

# Rollback to previous version
fly deploy --image registry.fly.io/your-api-name:v<previous-version>
```

---

## Cost Estimate

**Minimal Setup (Scale-to-Zero):**
- API: ~$0 (auto-stops when idle)
- Frontend: ~$0 (auto-stops when idle)
- Database: ~$2.15/month

**Total: ~$2-3/month**

**Production Setup (Always-On):**
- API (2 instances): ~$7.76/month
- Frontend (2 instances): ~$3.88/month
- Database (HA): ~$5.50/month

**Total: ~$17/month**

---

## Troubleshooting

**Problem:** Health check failed
```bash
# Check logs for errors
fly logs --app your-api-name

# Common issues:
# - Missing SECRET_KEY: fly secrets set SECRET_KEY="..."
# - Database not attached: fly postgres attach ...
```

**Problem:** Frontend can't reach API
```bash
# Verify VITE_API_URL in frontend/fly.toml matches API app name
# Rebuild frontend: cd frontend && fly deploy
```

**Problem:** Database connection error
```bash
# Verify DATABASE_URL is set
fly secrets list --app your-api-name

# Reattach database if needed
fly postgres attach gardening-db --app your-api-name
```

---

## Next Steps

1. ✅ Run smoke tests
2. ✅ Configure custom domain (optional)
3. ✅ Set up monitoring and alerts
4. ✅ Enable CI/CD for automatic deployments
5. ✅ Review security settings

---

## Full Documentation

For detailed documentation, see:
- [Complete Deployment Guide](flyio.md)
- [Secrets Template](secrets-template.env)

---

**Need Help?**
- Documentation: https://fly.io/docs
- Community: https://community.fly.io
- Project Issues: Check repository issues page
