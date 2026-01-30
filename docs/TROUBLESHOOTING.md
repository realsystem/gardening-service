# Troubleshooting Guide

## For Docker Users 🐳

If you're using Docker, use these commands:

```bash
# Check service status
docker-compose ps

# Restart all services
docker-compose restart

# View logs
docker-compose logs -f api
docker-compose logs -f frontend
```

**Common Docker Issues:**
- Services still starting up (wait 30 seconds after `docker-compose up`)
- Port conflicts (another service using port 8080 or 3000)
- Network issues (check `docker network ls`)

---

## For Local Development (non-Docker)

Check backend health:
```bash
curl http://localhost:8080/health
# Should return: {"status":"healthy"}
```

---

## Common Issues & Solutions

### Issue 1: Backend Not Running ❌

**Symptoms:**
- "Failed to fetch" error in browser console
- No response from `curl http://localhost:8080/health`

**Solution:**
```bash
# Navigate to project root
cd /Users/segorov/Projects/t/gardening-service

# Activate virtual environment
source .venv/bin/activate

# Start backend on port 8080 (important!)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

**Verify it's working:**
```bash
curl http://localhost:8080/health
# Should return: {"status":"healthy"}
```

---

### Issue 2: Port Mismatch (Backend on 8000, Frontend expects 8080) ⚠️

**Symptoms:**
- Backend running but frontend can't connect
- `curl http://localhost:8000/health` works
- `curl http://localhost:8080/health` fails

**Solution A - Restart backend on port 8080 (Recommended):**
```bash
# Stop current backend (Ctrl+C)
# Start on correct port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

**Solution B - Update frontend to use port 8000:**
```bash
cd frontend

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Restart frontend
npm run dev
```

---

### Issue 3: CORS Error 🚫

**Symptoms:**
- Browser console shows CORS error
- Backend is running and accessible

**Check:**
The backend CORS is configured to allow all origins (`allow_origins=["*"]`), so this should not be an issue. But if you see CORS errors:

1. Verify backend is running with CORS enabled
2. Check browser console for specific CORS error message
3. Try accessing from `http://localhost:3000` (not `127.0.0.1`)

---

### Issue 4: Frontend Not Running 🌐

**Symptoms:**
- Can't access `http://localhost:3000`

**Solution:**
```bash
cd frontend
npm install
npm run dev
```

---

## Complete Startup Checklist ✅

### Backend:
```bash
cd /Users/segorov/Projects/t/gardening-service
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Application startup complete.
```

### Frontend (in a new terminal):
```bash
cd /Users/segorov/Projects/t/gardening-service/frontend
npm run dev
```

Expected output:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
```

### Verify Both Running:
```bash
# Backend
curl http://localhost:8080/health
# Should return: {"status":"healthy"}

# Frontend
curl http://localhost:3000
# Should return HTML
```

---

## Test Garden Creation (Backend Only)

If you want to verify the backend endpoint works independently:

```bash
source .venv/bin/activate
python << 'EOF'
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Login
response = client.post('/users/login', json={
    'email': 'your-email@example.com',
    'password': 'your-password'
})

if response.status_code == 200:
    token = response.json()['access_token']

    # Create garden
    garden_response = client.post('/gardens',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Test Garden', 'garden_type': 'outdoor'}
    )

    print(f"Status: {garden_response.status_code}")
    print(f"Response: {garden_response.json()}")
else:
    print(f"Login failed: {response.text}")
EOF
```

---

## Still Having Issues?

1. **Check browser console** (F12 → Console tab)
   - Look for specific error messages
   - Note the failing URL

2. **Check browser network tab** (F12 → Network tab)
   - Look at the failed request
   - Check request URL, headers, and response

3. **Check backend logs**
   - Look at terminal where backend is running
   - Check for errors or rejected requests

4. **Verify database connection**
   ```bash
   source .venv/bin/activate
   python -c "from app.database import get_db; next(get_db()); print('✅ Database connected')"
   ```

---

## Port Reference

- **Backend API**: `http://localhost:8080`
- **Frontend UI**: `http://localhost:3000`
- **API Docs**: `http://localhost:8080/docs`
- **Database**: `localhost:5432` (PostgreSQL)

---

## Need More Help?

Include this information when reporting the issue:
1. Output of `./check_connection.sh`
2. Browser console errors (F12 → Console)
3. Browser network tab details (F12 → Network)
4. Backend terminal output
5. Frontend terminal output
