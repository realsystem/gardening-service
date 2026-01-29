# Database Enum Case Mismatch Fix

## Problem

After user registration and login, the main dashboard displayed **"Failed to fetch"** error.

### Root Cause

Database schema enums used **UPPERCASE** values, but Python code expected **lowercase** values:

**Database (incorrect):**
```sql
CREATE TYPE taskstatus AS ENUM ('PENDING', 'COMPLETED', 'SKIPPED');
```

**Python Code (correct):**
```python
class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"
```

### Error Message

```
sqlalchemy.exc.DataError: (psycopg2.errors.InvalidTextRepresentation)
invalid input value for enum taskstatus: "pending"
LINE 3: ...RE care_tasks.user_id = 1 AND care_tasks.status = 'pending' ...
```

## Affected Enums

The following database enums had case mismatches:

1. ❌ `taskstatus` - `PENDING` → `pending`
2. ❌ `plantingmethod` - `DIRECT_SOW` → `direct_sow`
3. ❌ `sunrequirement` - `FULL_SUN` → `full_sun`
4. ❌ `tasksource` - `AUTO_GENERATED` → `auto_generated`
5. ❌ `waterrequirement` - `LOW` → `low`
6. ❌ `tasktype` - `WATER` → `water` (had mixed case)

These enums were already correct:
- ✅ `gardentype`, `hydrosystemtype`, `irrigationmethod`, `lightsourcetype`
- ✅ `planthealth`, `recurrencefrequency`, `taskpriority`

## Solution

Fixed all enum definitions to use lowercase values matching the Python code.

### Migration Script

File: [`migrations/fix_enum_case_mismatch.sql`](migrations/fix_enum_case_mismatch.sql)

The script performs these steps for each affected enum:
1. Rename existing enum to `_old`
2. Create new enum with correct lowercase values
3. Convert column to use new enum (with `lower()` transformation)
4. Drop old enum type

### Applied Fix

```bash
# Execute migration
docker-compose exec db psql -U gardener -d gardening_db -f /migrations/fix_enum_case_mismatch.sql

# Restart API to clear connections
docker-compose restart api
```

## Verification

After the fix:

```sql
\dT+ taskstatus
-- Shows: pending, completed, skipped (lowercase ✓)
```

Dashboard now loads successfully without "Failed to fetch" errors.

## Why This Happened

**SQLAlchemy Enum Behavior:**
- When creating enums, SQLAlchemy can use either:
  - Enum **member names** (e.g., `PENDING`) - uppercase Python attribute
  - Enum **values** (e.g., `"pending"`) - the string value

**Our Configuration:**
```python
status = Column(SQLEnum(TaskStatus, values_callable=lambda x: [e.value for e in x]))
```

The `values_callable` tells SQLAlchemy to use enum **values** (lowercase), but the initial database creation may have used member names instead.

## Prevention

### 1. Always Use `values_callable`

```python
# ✅ CORRECT - uses lowercase values
status = Column(
    SQLEnum(TaskStatus, values_callable=lambda x: [e.value for e in x]),
    nullable=False
)

# ❌ INCORRECT - might use uppercase member names
status = Column(SQLEnum(TaskStatus), nullable=False)
```

### 2. Verify Enum Creation

After creating a new enum column, verify in database:

```sql
-- Check enum values
SELECT enumlabel FROM pg_enum
WHERE enumtypid = 'taskstatus'::regtype;

-- Should show: pending, completed, skipped (lowercase)
```

### 3. Test Immediately

After schema changes, test with actual data:
```python
# This should work without errors
task = CareTask(status=TaskStatus.PENDING)  # Uses "pending" value
db.add(task)
db.commit()
```

## Related Files

- [`app/models/care_task.py`](app/models/care_task.py) - TaskStatus, TaskType, TaskSource enums
- [`app/models/planting_event.py`](app/models/planting_event.py) - PlantingMethod enum
- [`app/models/plant_variety.py`](app/models/plant_variety.py) - SunRequirement, WaterRequirement enums
- [`migrations/fix_enum_case_mismatch.sql`](migrations/fix_enum_case_mismatch.sql) - Migration script

## Testing

Verify the fix works:

```bash
# 1. Register a new user
# 2. Login
# 3. Check dashboard loads without "Failed to fetch"
# 4. Check browser console has no errors
# 5. Check API logs show no enum errors
```

**Expected behavior:**
- ✅ Dashboard loads successfully
- ✅ No "Failed to fetch" errors
- ✅ No SQL enum errors in logs
- ✅ Tasks, gardens, and other data fetch correctly

## Impact

**Before fix:**
- ❌ Dashboard failed to load after login
- ❌ "Failed to fetch" error displayed
- ❌ SQLAlchemy DataError on any task query
- ❌ User couldn't use the application

**After fix:**
- ✅ Dashboard loads successfully
- ✅ All API endpoints work correctly
- ✅ Tasks can be created and queried
- ✅ Full application functionality restored

## Summary

This was a **schema mismatch** between database enum definitions (uppercase) and Python code expectations (lowercase). The fix aligns all database enums to use lowercase values matching the Python code, ensuring compatibility throughout the application.

**Key Lesson:** Always verify database schema matches application code expectations, especially for enums where SQLAlchemy's behavior can vary.
