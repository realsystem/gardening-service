# UI Deployment Guide

## Quick Reference

| Environment | UI URL | API URL |
|------------|--------|---------|
| Local Dev | http://localhost:3000 | http://localhost:8080 |
| Production | https://your-ui-app.fly.dev | https://your-api-app.fly.dev |

## Local Development

### Option 1: Docker Compose (Recommended)

Start entire stack:
```bash
docker-compose up
```

Access:
- UI: http://localhost:3000
- API: http://localhost:8080
- API Docs: http://localhost:8080/docs

### Option 2: Native Development

Terminal 1 (Backend):
```bash
uvicorn app.main:app --reload --port 8080
```

Terminal 2 (Frontend):
```bash
cd frontend
npm install
npm run dev
```

## Production Deployment (Fly.io)

### Prerequisites

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login
```

### Deploy Backend First

```bash
# 1. Deploy backend (from root directory)
fly launch --no-deploy
fly postgres create --name gardening-db
fly postgres attach gardening-db
fly secrets set SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
fly deploy

# 2. Note your backend URL
fly info
# Example: https://gardening-api.fly.dev
```

### Deploy Frontend

```bash
# 1. Navigate to frontend
cd frontend

# 2. Update fly.toml with your backend URL
# Edit: VITE_API_URL = "https://gardening-api.fly.dev"

# 3. Launch frontend app
fly launch --no-deploy

# 4. Deploy
fly deploy

# 5. Open in browser
fly open
```

## Environment Variables

### Frontend (.env)

```bash
# Development
VITE_API_URL=http://localhost:8080

# Production (set in fly.toml)
VITE_API_URL=https://your-backend-app.fly.dev
```

### Backend

Already configured in main `fly.toml` - no changes needed.

## Troubleshooting

### UI can't connect to API

**Symptom**: Login fails, tasks don't load

**Check**:
1. Verify API URL in browser console
2. Check CORS settings in backend
3. Ensure backend is running: `curl https://your-api.fly.dev/health`

**Fix**:
```bash
# Update VITE_API_URL in frontend/fly.toml
# Redeploy frontend
cd frontend
fly deploy
```

### UI shows blank page

**Check**:
1. Browser console for errors
2. Nginx logs: `fly logs`

**Fix**:
```bash
# Rebuild and redeploy
cd frontend
fly deploy
```

### Authentication issues

**Remember**:
- JWT stored in memory only
- User must re-login on page refresh
- This is intentional for security

## Cost Optimization

Frontend deployment:
- **Memory**: 256MB (minimal)
- **Scale to zero**: Enabled
- **Estimated cost**: $0-2/month

Total cost (API + DB + UI): **$0-7/month**

## Testing

```bash
cd frontend

# Run tests
npm test

# Build for production
npm run build

# Preview production build
npm run preview
```

## Architecture

```
┌─────────────┐
│   Browser   │
└─────┬───────┘
      │ HTTP
┌─────▼────────┐     ┌──────────────┐
│ Frontend     │────▶│  Backend API │
│ (Nginx)      │     │  (FastAPI)   │
│ :3000        │     │  :8080       │
└──────────────┘     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │  PostgreSQL  │
                     │  :5432       │
                     └──────────────┘
```

- Frontend: Static React SPA served by nginx
- Backend: FastAPI Python application
- Database: PostgreSQL managed by Fly
- Communication: HTTP/JSON
- Auth: JWT (in-memory, no persistence)

## Security Notes

✅ **Secure**:
- JWT in memory only (cleared on refresh)
- HTTPS enforced in production
- No secrets in frontend build
- CORS properly configured

⚠️ **MVP Limitations**:
- No persistent auth (re-login required)
- No CSRF protection (stateless API)
- No rate limiting on frontend

## Next Steps After Deployment

1. **Load seed data** (one-time):
   ```bash
   fly ssh console -a your-backend-app
   python -m seed_data.plant_varieties
   exit
   ```

2. **Test the flow**:
   - Register new account
   - Create garden
   - Create planting event
   - Verify tasks are generated

3. **Monitor**:
   ```bash
   # Backend logs
   fly logs -a your-backend-app

   # Frontend logs
   fly logs -a your-frontend-app
   ```

## Production Checklist

- [ ] Backend deployed and healthy
- [ ] Database created and attached
- [ ] Seed data loaded
- [ ] Frontend VITE_API_URL updated
- [ ] Frontend deployed
- [ ] HTTPS working
- [ ] Login/Register working
- [ ] Task creation working
- [ ] Task completion working
