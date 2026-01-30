# Database Reset Instructions

## Why Reset?

If your database was created with the old migrations (before the `is_hydroponic` fix), you need to recreate it to get the correct schema.

---

## Option 1: Docker (Recommended for Development)

### Full Reset with Rebuild

```bash
# Stop all services
docker-compose down

# Remove database volume (THIS DELETES ALL DATA!)
docker volume rm gardening-service_postgres_data
# Or remove the local data directory
rm -rf .data/postgres

# Rebuild and start fresh
docker-compose up -d --build

# Wait for services to be ready (30 seconds)
sleep 30

# Verify database schema
docker-compose exec -T db psql -U gardener -d gardening_db -c "\d gardens" | grep is_hydroponic
```

**Expected output:**
```
is_hydroponic         | boolean                  |           | not null | false
```

---

## Option 2: Local Development (Non-Docker)

### Reset Local Database

```bash
# Activate virtual environment
source .venv/bin/activate

# Drop and recreate database
psql -U postgres << EOF
DROP DATABASE IF EXISTS gardening_db;
CREATE DATABASE gardening_db;
GRANT ALL PRIVILEGES ON DATABASE gardening_db TO gardener;
EOF

# Run migrations
alembic upgrade head

# Load seed data
python -m seed_data.plant_varieties

# Verify
psql -U gardener -d gardening_db -c "\d gardens" | grep is_hydroponic
```

---

## Option 3: Manual Fix (For Existing Data)

If you have important data and can't reset:

```bash
# Fix the column type in running database
docker-compose exec -T db psql -U gardener -d gardening_db << 'EOF'
ALTER TABLE gardens ALTER COLUMN is_hydroponic DROP DEFAULT;
ALTER TABLE gardens ALTER COLUMN is_hydroponic TYPE boolean USING is_hydroponic::boolean;
ALTER TABLE gardens ALTER COLUMN is_hydroponic SET DEFAULT false;
EOF

# Verify
docker-compose exec -T db psql -U gardener -d gardening_db -c "\d gardens" | grep is_hydroponic
```

---

## Verification

After reset, verify the fix worked:

### 1. Check Database Schema

```bash
docker-compose exec -T db psql -U gardener -d gardening_db -c "\d gardens" | grep is_hydroponic
```

**Should show:**
```
is_hydroponic         | boolean                  |           | not null | false
```

### 2. Test Garden Creation

Open http://localhost:3000 and try creating a garden. Should work without errors.

### 3. Check API Logs

```bash
docker-compose logs api --tail=10
```

Should NOT show any `ProgrammingError` about boolean/integer mismatch.

---

## What Was Fixed

**Before (❌ Wrong):**
```python
op.add_column('gardens', sa.Column('is_hydroponic', sa.Integer(), nullable=False, server_default='0'))
```

**After (✅ Correct):**
```python
op.add_column('gardens', sa.Column('is_hydroponic', sa.Boolean(), nullable=False, server_default='false'))
```

**Files Changed:**
- [migrations/versions/20260128_2315_c3d4e5f6g7h8_add_hydroponics_support.py](migrations/versions/20260128_2315_c3d4e5f6g7h8_add_hydroponics_support.py:38)

---

## Testing

After reset, test these operations:

1. ✅ Create outdoor garden
2. ✅ Create indoor garden
3. ✅ Create hydroponic garden
4. ✅ Create land
5. ✅ Place garden on land (drag and drop)
6. ✅ Remove garden from land

All should work without errors.

---

## Need Help?

If you encounter issues:

1. **Check logs:**
   ```bash
   docker-compose logs -f api
   ```

2. **Verify services:**
   ```bash
   ./docker-status.sh
   ```

3. **Check database:**
   ```bash
   docker-compose exec db psql -U gardener -d gardening_db
   ```

4. **See troubleshooting guide:**
   [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
