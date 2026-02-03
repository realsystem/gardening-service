# GitHub Actions Workflows

This directory contains CI/CD workflows for automatic deployment to Fly.io.

## Available Workflows

### `deploy-production.yml`
- **Triggers:** Push to `main` branch or manual trigger
- **Deploys:** API + Frontend to production
- **Includes:** Health checks and smoke tests

### `deploy-staging.yml`
- **Triggers:** Push to `develop` branch or manual trigger
- **Deploys:** To staging environment

## Quick Setup

1. Get Fly.io API token:
   ```bash
   flyctl tokens create deploy
   ```

2. Add to GitHub Secrets:
   - Go to: Settings → Secrets → Actions
   - Add secret: `FLY_API_TOKEN`

3. Push to GitHub:
   ```bash
   git push origin main
   ```

4. Watch deployment:
   - Go to: Actions tab
   - Click on the running workflow

## Full Documentation

See: [docs/deployment/GITHUB_ACTIONS_SETUP.md](../../docs/deployment/GITHUB_ACTIONS_SETUP.md)
