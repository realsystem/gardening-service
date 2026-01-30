# Database Schema Fixes

## Overview

This document tracks all database schema mismatches discovered between the database and Python code, along with their fixes.

---

## Issue 1: Enum Case Mismatch (Fixed)

**Problem:** Dashboard showed "Failed to fetch" after login

**Root Cause:** Database enums used UPPERCASE values but Python expected lowercase

**Error:**
```
sqlalchemy.exc.DataError: invalid input value for enum taskstatus: "pending"
```

**Affected Enums:**
- `taskstatus`: `PENDING` → `pending`
- `plantingmethod`: `DIRECT_SOW` → `direct_sow`
- `sunrequirement`: `FULL_SUN` → `full_sun`
- `tasksource`: `AUTO_GENERATED` → `auto_generated`
- `waterrequirement`: `LOW` → `low`
- `tasktype`: `WATER` → `water`

**Fix:** [`migrations/fix_enum_case_mismatch.sql`](migrations/fix_enum_case_mismatch.sql)

**Details:** See [`ENUM_CASE_FIX.md`](ENUM_CASE_FIX.md)

---

## Issue 2: Boolean Column Type Mismatch (Fixed)

**Problem:** "Failed to fetch" when adding a new garden

**Root Cause:** `is_hydroponic` column was type `integer` but Python code expected `boolean`

**Error:**
```
sqlalchemy.exc.ProgrammingError: column "is_hydroponic" is of type integer
but expression is of type boolean
```

**Database Schema (incorrect):**
```sql
is_hydroponic integer NOT NULL DEFAULT 0
```

**Python Model (correct):**
```python
is_hydroponic = Column(Boolean, nullable=False, default=False)
```

**Impact:**
- ❌ Could not create any gardens
- ❌ Garden creation form failed with "Failed to fetch"
- ❌ Application unusable for primary feature

**Fix Applied:**
```sql
ALTER TABLE gardens ALTER COLUMN is_hydroponic DROP DEFAULT;
ALTER TABLE gardens ALTER COLUMN is_hydroponic TYPE boolean
  USING (is_hydroponic::integer != 0);
ALTER TABLE gardens ALTER COLUMN is_hydroponic SET DEFAULT false;
```

**Migration Script:** [`migrations/fix_boolean_column_types.sql`](migrations/fix_boolean_column_types.sql)

**Verification:**
```sql
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'gardens' AND column_name = 'is_hydroponic';

-- Result:
-- is_hydroponic | boolean | false ✓
```

**Other Boolean Columns Checked:**
- ✅ `care_tasks.is_recurring` - already `boolean` (correct)

---

## Root Cause Analysis

### Why Did This Happen?

Both issues stem from **SQLAlchemy's schema generation behavior**:

1. **Enum Case:**
   - SQLAlchemy can use either enum member names (uppercase) or values (lowercase)
   - Initial migrations may have used member names instead of values
   - Code expects values due to `values_callable` parameter

2. **Boolean Type:**
   - Some database migrations created boolean columns as `integer`
   - Likely due to SQLite compatibility (SQLite uses integers for booleans)
   - PostgreSQL supports native `boolean` type

### How to Prevent

#### For Enums:
```python
# ✅ ALWAYS use values_callable
status = Column(
    SQLEnum(TaskStatus, values_callable=lambda x: [e.value for e in x]),
    nullable=False
)

# ❌ NEVER omit values_callable
status = Column(SQLEnum(TaskStatus), nullable=False)  # May use member names!
```

#### For Booleans:
```python
# ✅ Use SQLAlchemy Boolean type
is_hydroponic = Column(Boolean, nullable=False, default=False)

# ❌ Don't use Integer for booleans
is_hydroponic = Column(Integer, nullable=False, default=0)  # Wrong!
```

#### Verification After Migration:
```bash
# Always verify schema matches code
docker-compose exec db psql -U gardener -d gardening_db

# Check enum values
\dT+ taskstatus

# Check column types
\d gardens
```

---

## Testing After Fixes

### Test 1: Dashboard Loads ✅
```
1. Login to application
2. Dashboard should load without "Failed to fetch"
3. Tasks, gardens, sensors should all fetch successfully
```

### Test 2: Create Garden ✅
```
1. Click "Add Garden"
2. Fill in garden name
3. Select garden type (outdoor/indoor)
4. Submit form
5. Garden should be created successfully
```

### Test 3: Create Tasks ✅
```
1. Create a planting event
2. View tasks generated
3. Complete/skip tasks
4. Status changes should save correctly
```

---

## Migration History

| Date | Issue | Migration Script | Status |
|------|-------|------------------|--------|
| 2026-01-29 | Enum case mismatch | `fix_enum_case_mismatch.sql` | ✅ Applied |
| 2026-01-29 | Boolean type mismatch | `fix_boolean_column_types.sql` | ✅ Applied |

---

## Verification Commands

### Check All Enums Are Lowercase
```sql
SELECT
    t.typname AS enum_name,
    e.enumlabel AS enum_value
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
WHERE t.typname IN (
    'taskstatus', 'tasktype', 'tasksource', 'taskpriority',
    'plantingmethod', 'sunrequirement', 'waterrequirement'
)
ORDER BY t.typname, e.enumsortorder;
```

### Check All Boolean Columns
```sql
SELECT
    table_name,
    column_name,
    data_type,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND data_type = 'boolean'
ORDER BY table_name, column_name;
```

### Expected Results:
- All enum values should be lowercase
- All `is_*` columns should be type `boolean`
- No `integer` columns being used as booleans

---

## Related Files

- [`migrations/fix_enum_case_mismatch.sql`](migrations/fix_enum_case_mismatch.sql)
- [`migrations/fix_boolean_column_types.sql`](migrations/fix_boolean_column_types.sql)
- [`ENUM_CASE_FIX.md`](ENUM_CASE_FIX.md) - Detailed enum fix documentation
- [`app/models/garden.py`](app/models/garden.py) - Garden model definition
- [`app/models/care_task.py`](app/models/care_task.py) - Task model with enums

---

## Summary

Both schema issues have been **identified and fixed**:

✅ **Enum case mismatch** - All enums now use lowercase values
✅ **Boolean type mismatch** - `is_hydroponic` is now proper boolean

**Result:**
- Dashboard loads successfully
- Gardens can be created
- Tasks work correctly
- Full application functionality restored

**Lessons Learned:**
1. Always use `values_callable` for SQLAlchemy enums
2. Use proper `Boolean` type, not `Integer` for boolean columns
3. Verify database schema after migrations
4. Test immediately after schema changes
