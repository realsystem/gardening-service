# GitHub Actions CI/CD Setup for Fly.io

**Automated deployment using GitHub Actions**

This guide sets up automatic deployments to Fly.io whenever you push to GitHub.

---

## Benefits

✅ **No local network issues** - Uses GitHub's infrastructure  
✅ **Automatic deployments** - Deploy on every push to `main`  
✅ **Manual control** - Trigger deployments with one click  
✅ **Built-in verification** - Automatic health checks after deployment  
✅ **Smoke tests** - Runs automated tests post-deployment  

---

## Setup (One-Time)

### Step 1: Get Fly.io API Token

Generate an API token from your Fly.io account:

```bash
# Login to Fly.io
flyctl auth login

# Generate a deploy token
flyctl tokens create deploy
```

**Copy the token** - you'll need it in the next step. It looks like:
```
FlyV1 fm1_abcdefghijklmnopqrstuvwxyz1234567890
```

### Step 2: Add Token to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `FLY_API_TOKEN`
5. Value: Paste the token from Step 1
6. Click **Add secret**

**GitHub URL:**
```
https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions
```

### Step 3: Push Workflows to GitHub

```bash
# Add workflow files
git add .github/workflows/

# Commit
git commit -m "Add GitHub Actions deployment workflows"

# Push to GitHub
git push origin main
```

**Done!** GitHub Actions is now set up.

---

## Usage

### Automatic Deployment

**Any push to `main` branch automatically deploys to production:**

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main
```

GitHub Actions will:
1. Build and deploy API
2. Build and deploy Frontend
3. Run health checks
4. Run smoke tests

**Watch progress:**
```
https://github.com/YOUR_USERNAME/YOUR_REPO/actions
```

### Manual Deployment

**Trigger deployment without pushing code:**

1. Go to **Actions** tab in GitHub
2. Click **Deploy to Production (Fly.io)**
3. Click **Run workflow**
4. Choose what to deploy:
   - Deploy API: yes/no
   - Deploy frontend: yes/no
5. Click **Run workflow**

### Staging Deployment

**Push to `develop` branch for staging:**

```bash
git checkout -b develop
git push origin develop
```

Or trigger manually from the Actions tab.

---

## Workflow Files

### Production Workflow (`.github/workflows/deploy-production.yml`)

**Triggers:**
- Push to `main` branch
- Manual trigger from Actions tab

**What it does:**
1. Deploys API to `gardening-service-api`
2. Verifies API health endpoint
3. Deploys Frontend to `gardening-service-ui`
4. Verifies Frontend is serving
5. Runs smoke tests
6. Reports success/failure

### Staging Workflow (`.github/workflows/deploy-staging.yml`)

**Triggers:**
- Push to `develop` branch
- Manual trigger from Actions tab

**What it does:**
- Deploys to staging environment
- Useful for testing before production

---

## Monitoring Deployments

### View Logs in GitHub

```
https://github.com/YOUR_USERNAME/YOUR_REPO/actions
```

Click on any workflow run to see:
- Build output
- Deployment logs
- Health check results
- Smoke test results

### View Logs in Fly.io

```bash
# API logs
flyctl logs --app gardening-service-api

# Frontend logs
flyctl logs --app gardening-service-ui
```

---

## Workflow Status Badges

Add status badges to your README:

```markdown
![Deploy Production](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/deploy-production.yml/badge.svg)
```

This shows the current deployment status:
- ✅ Green: Last deployment succeeded
- ❌ Red: Last deployment failed
- 🟡 Yellow: Deployment in progress

---

## Troubleshooting

### Deployment Fails with "FLY_API_TOKEN not set"

**Problem:** GitHub secret is missing or misnamed.

**Solution:**
1. Go to repository **Settings** → **Secrets**
2. Verify `FLY_API_TOKEN` exists (case-sensitive)
3. If missing, add it (see Step 2 above)

### Health Check Fails

**Problem:** API deployed but health check fails.

**Solution:**
```bash
# Check API logs in Fly.io
flyctl logs --app gardening-service-api

# Common issues:
# - Database migrations failed
# - Secrets not set
# - Application crashed on startup
```

### Build Fails on GitHub but Works Locally

**Problem:** Different build environment.

**Solution:**
- Check the full error in GitHub Actions logs
- Verify all dependencies are in `requirements.txt`
- Ensure Dockerfile doesn't rely on local files

### Workflow Doesn't Trigger

**Problem:** Workflow not running on push.

**Solution:**
1. Verify workflow file is in `.github/workflows/`
2. Check branch name matches (`main` vs `master`)
3. Ensure file has `.yml` extension
4. Check for YAML syntax errors

---

## Advanced Configuration

### Deploy Only on Tag

Modify `.github/workflows/deploy-production.yml`:

```yaml
on:
  push:
    tags:
      - 'v*'  # Only deploy on version tags (v1.0.0, v1.1.0, etc.)
```

### Require Manual Approval

Add an environment with protection rules:

1. Go to **Settings** → **Environments**
2. Create environment: `production`
3. Enable **Required reviewers**
4. Add yourself as reviewer

Update workflow:
```yaml
jobs:
  deploy-api:
    environment: production  # Requires approval before deploying
```

### Slack Notifications

Add Slack notification on deployment:

```yaml
- name: Notify Slack
  if: success()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Deployment successful! 🚀'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Deploy to Multiple Regions

```yaml
- name: Deploy to multiple regions
  run: |
    flyctl deploy --app gardening-service-api --region sjc
    flyctl deploy --app gardening-service-api --region iad
```

---

## Cost Implications

**GitHub Actions usage:**
- Free for public repositories (unlimited)
- Free for private repositories (2,000 minutes/month)
- This workflow uses ~5-10 minutes per deployment

**Fly.io costs:**
- Same as manual deployment (~$2-17/month)
- No additional charges for CI/CD

---

## Security Best Practices

### 1. Rotate Tokens Periodically

```bash
# Generate new token
flyctl tokens create deploy

# Update GitHub secret
# Settings → Secrets → FLY_API_TOKEN → Update

# Revoke old token
flyctl tokens list
flyctl tokens revoke <token-id>
```

### 2. Use Separate Tokens per Environment

```bash
# Production token
flyctl tokens create deploy --name "GitHub Actions Production"

# Staging token
flyctl tokens create deploy --name "GitHub Actions Staging"
```

Store as separate secrets:
- `FLY_API_TOKEN_PROD`
- `FLY_API_TOKEN_STAGING`

### 3. Limit Token Permissions

Fly.io deploy tokens have minimal permissions:
- Can deploy apps
- Cannot delete apps
- Cannot modify billing

This is safe for CI/CD.

---

## Comparison: GitHub Actions vs Local Deployment

| Feature | GitHub Actions | Local Deployment |
|---------|---------------|------------------|
| **Network** | GitHub infrastructure | Your local network |
| **Speed** | ~5-10 min | ~3-5 min |
| **Reliability** | Very high | Depends on local network |
| **Automation** | Automatic on push | Manual |
| **Logs** | Preserved in GitHub | Terminal only |
| **Team Access** | All team members | Individual |
| **Cost** | Free (for most usage) | Free |

---

## Next Steps

After setup:

1. ✅ **Test the workflow**
   ```bash
   # Make a small change
   echo "# Test" >> README.md
   git add README.md
   git commit -m "Test GitHub Actions"
   git push origin main
   
   # Watch it deploy automatically
   # https://github.com/YOUR_USERNAME/YOUR_REPO/actions
   ```

2. ✅ **Add status badge to README**
   ```markdown
   ![Deploy](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/deploy-production.yml/badge.svg)
   ```

3. ✅ **Set up notifications**
   - GitHub will email you on failures
   - Optionally add Slack/Discord webhooks

4. ✅ **Document your deployment process**
   - Update team wiki
   - Add deployment checklist

---

## Rollback with GitHub Actions

### Option 1: Revert Commit

```bash
# Revert the problematic commit
git revert HEAD

# Push (triggers automatic deployment of previous version)
git push origin main
```

### Option 2: Re-run Previous Successful Workflow

1. Go to **Actions** tab
2. Find the last successful workflow run
3. Click **Re-run jobs**
4. GitHub will deploy the old version

### Option 3: Manual Rollback (Fastest)

```bash
# From your local machine
flyctl releases --app gardening-service-api
flyctl deploy --app gardening-service-api --image registry.fly.io/gardening-service-api:v<previous-version>
```

---

## FAQ

**Q: Will this work for private repositories?**  
A: Yes, GitHub Actions works for both public and private repos.

**Q: Can I deploy to different environments?**  
A: Yes, create separate workflow files or use workflow inputs to choose environment.

**Q: What if I want to deploy from a branch other than main?**  
A: Edit the workflow file and change `branches: [main]` to your branch name.

**Q: Can I disable automatic deployments?**  
A: Yes, remove the `push:` trigger and keep only `workflow_dispatch:` for manual deployments.

**Q: How do I test the workflow without deploying?**  
A: Use workflow concurrency and `if` conditions to create a dry-run mode.

---

## Summary

**Setup time:** 5 minutes  
**Deployment time:** 5-10 minutes (automatic)  
**Reliability:** Very high  
**Best for:** Teams, production deployments, avoiding network issues

**You've now set up:**
- ✅ Automatic deployments on push
- ✅ Manual deployment triggers
- ✅ Health checks and smoke tests
- ✅ Deployment logs and history
- ✅ Secure token-based authentication

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-02  
**See Also:** [Fly.io Deployment Guide](flyio.md), [Automated Deployment](AUTOMATED_DEPLOYMENT.md)
