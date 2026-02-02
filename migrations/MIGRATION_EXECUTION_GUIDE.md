# Database Constraint Migrations - Execution Guide

**Date:** 2026-02-01
**Author:** Database Schema Audit
**Purpose:** Guide for executing database constraint migrations (001-003)

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Pre-Migration Checklist](#pre-migration-checklist)
4. [Execution Plan](#execution-plan)
5. [Testing Procedures](#testing-procedures)
6. [Rollback Procedures](#rollback-procedures)
7. [Troubleshooting](#troubleshooting)
8. [Post-Migration Verification](#post-migration-verification)

---

## Overview

This guide covers the execution of three phased migrations that add critical database constraints:

| Phase | Migration | Focus | Risk Level |
|-------|-----------|-------|------------|
| 1 | `001_add_critical_constraints.sql` | Foreign keys, CASCADE, unique constraints | **HIGH** |
| 2 | `002_add_high_priority_constraints.sql` | ENUMs, NOT NULL, user-scoped unique names | **MEDIUM** |
| 3 | `003_add_check_constraints.sql` | Range checks, positive values, conditional rules | **LOW** |

**Estimated Total Time:** 30-45 minutes (including testing)

**Recommended Schedule:**
- Phase 1: Deploy immediately (critical data integrity)
- Phase 2: Deploy within 1 week (high priority)
- Phase 3: Deploy within 1 month (data quality improvement)

---

## Prerequisites

### 1. Database Backup

**CRITICAL:** Create a full database backup before proceeding.

```bash
# PostgreSQL backup
pg_dump -h localhost -U your_user -d gardening_service -F c -b -v -f backup_pre_constraints_$(date +%Y%m%d_%H%M%S).dump

# Verify backup was created
ls -lh backup_pre_constraints_*.dump
```

### 2. Database Access

Ensure you have:
- PostgreSQL superuser or database owner privileges
- Connection to the target database
- `psql` command-line tool installed

### 3. Application Downtime Window

**Phase 1 requires application downtime** due to foreign key validation:
- Estimated duration: 5-10 minutes
- Schedule during low-traffic period
- Notify users in advance

Phases 2 and 3 can be executed with minimal impact (brief locks during DDL).

### 4. Data Validation

Before migrating, verify data integrity:

```sql
-- Check for orphaned CompanionRelationship records
SELECT cr.id, cr.plant_a_id, cr.plant_b_id
FROM companion_relationships cr
LEFT JOIN plant_varieties pa ON cr.plant_a_id = pa.id
LEFT JOIN plant_varieties pb ON cr.plant_b_id = pb.id
WHERE pa.id IS NULL OR pb.id IS NULL;

-- Check for NULL values in columns that will become NOT NULL
SELECT 'planting_events' AS table_name, COUNT(*) AS null_count
FROM planting_events WHERE plant_count IS NULL
UNION ALL
SELECT 'germination_events', COUNT(*)
FROM germination_events WHERE seed_count IS NULL OR germinated IS NULL;

-- Check for duplicate sensor readings (same garden + date)
SELECT garden_id, reading_date, COUNT(*) AS count
FROM sensor_readings
GROUP BY garden_id, reading_date
HAVING COUNT(*) > 1;
```

**If any of these queries return rows, data must be cleaned up first.**

---

## Pre-Migration Checklist

- [ ] Full database backup completed and verified
- [ ] Database privileges confirmed (superuser/owner)
- [ ] Application downtime window scheduled (Phase 1 only)
- [ ] Data validation queries executed (no orphaned records or invalid data)
- [ ] Team notified of migration schedule
- [ ] Rollback scripts reviewed and ready
- [ ] Test environment migration successfully completed
- [ ] Monitoring/alerting configured for database errors

---

## Execution Plan

### Phase 1: Critical Constraints (IMMEDIATE)

**Estimated Duration:** 5-10 minutes
**Downtime Required:** Yes

#### Step 1: Stop Application

```bash
# Example for Docker Compose
docker-compose stop backend

# Example for systemd
sudo systemctl stop gardening-service
```

#### Step 2: Execute Migration

```bash
# Connect to database
psql -h localhost -U your_user -d gardening_service

# Execute migration
\i migrations/001_add_critical_constraints.sql

# Verify no errors
\echo 'Migration 001 completed'
```

#### Step 3: Verify Constraints

```sql
-- Verify CompanionRelationship foreign keys exist
SELECT conname, contype, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'companion_relationships'::regclass
AND conname LIKE 'fk_%';

-- Verify user_id CASCADE constraints
SELECT tc.table_name, rc.delete_rule
FROM information_schema.table_constraints tc
JOIN information_schema.referential_constraints rc
  ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.constraint_name LIKE '%user_id%'
AND rc.delete_rule = 'CASCADE'
ORDER BY tc.table_name;

-- Verify unique constraint on sensor_readings
SELECT indexname, indexdef
FROM pg_indexes
WHERE indexname = 'unique_sensor_reading_per_day';
```

#### Step 4: Start Application

```bash
# Restart application
docker-compose start backend

# Or for systemd
sudo systemctl start gardening-service
```

#### Step 5: Monitor Logs

```bash
# Check for database errors
tail -f /var/log/gardening-service/error.log

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

---

### Phase 2: High Priority Constraints (WITHIN 1 WEEK)

**Estimated Duration:** 10-15 minutes
**Downtime Required:** No (brief locks acceptable)

#### Step 1: Pre-Migration Data Cleanup

```sql
-- Set default values for NULL columns that will become NOT NULL
UPDATE irrigation_zones
SET delivery_type = 'manual'
WHERE delivery_type IS NULL OR delivery_type = '';

UPDATE irrigation_sources
SET source_type = 'municipal'
WHERE source_type IS NULL OR source_type = '';

UPDATE planting_events
SET plant_count = 1
WHERE plant_count IS NULL;

UPDATE germination_events
SET seed_count = 0
WHERE seed_count IS NULL;

UPDATE germination_events
SET germinated = FALSE
WHERE germinated IS NULL;

COMMIT;
```

#### Step 2: Execute Migration

```bash
psql -h localhost -U your_user -d gardening_service \
  -f migrations/002_add_high_priority_constraints.sql
```

#### Step 3: Verify Constraints

```sql
-- Verify ENUM types created
SELECT typname FROM pg_type
WHERE typname IN ('irrigation_delivery_type', 'irrigation_source_type');

-- Verify NOT NULL constraints
SELECT table_name, column_name, is_nullable
FROM information_schema.columns
WHERE table_name IN ('planting_events', 'germination_events')
AND column_name IN ('plant_count', 'seed_count', 'germinated')
AND is_nullable = 'NO';

-- Verify unique constraints
SELECT indexname
FROM pg_indexes
WHERE indexname LIKE 'unique_%'
ORDER BY indexname;
```

---

### Phase 3: Data Quality Constraints (WITHIN 1 MONTH)

**Estimated Duration:** 5-10 minutes
**Downtime Required:** No

#### Step 1: Validate Existing Data

```sql
-- Check for violations of CHECK constraints before applying them
-- Example: Check for negative garden sizes
SELECT id, name, size_sq_ft
FROM gardens
WHERE size_sq_ft <= 0;

-- Check for invalid pH values
SELECT id, name, ph_min, ph_max
FROM gardens
WHERE ph_min IS NOT NULL AND (ph_min < 0 OR ph_max > 14);

-- Check for humidity out of range
SELECT id, garden_id, humidity_percent
FROM sensor_readings
WHERE humidity_percent IS NOT NULL
AND (humidity_percent < 0 OR humidity_percent > 100);
```

**If any rows are returned, data must be corrected before migration.**

#### Step 2: Execute Migration

```bash
psql -h localhost -U your_user -d gardening_service \
  -f migrations/003_add_check_constraints.sql
```

#### Step 3: Verify Constraints

```sql
-- List all CHECK constraints added
SELECT conname, conrelid::regclass AS table_name,
       pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE contype = 'c'
AND conname LIKE 'check_%'
ORDER BY conrelid::regclass::text, conname;

-- Count constraints by table
SELECT conrelid::regclass AS table_name, COUNT(*) AS constraint_count
FROM pg_constraint
WHERE contype = 'c'
AND connamespace = 'public'::regnamespace
GROUP BY conrelid
ORDER BY constraint_count DESC;
```

---

## Testing Procedures

### Unit Test Execution

Run the constraint enforcement unit tests:

```bash
# Run all constraint tests
pytest tests/test_database_constraints.py -v

# Run specific phase tests
pytest tests/test_database_constraints.py::TestPhase1ForeignKeys -v
pytest tests/test_database_constraints.py::TestPhase2EnumConstraints -v
pytest tests/test_database_constraints.py::TestPhase3RangeConstraints -v

# Run with coverage
pytest tests/test_database_constraints.py --cov=app.models --cov-report=html
```

### Integration Testing

#### Test Foreign Key Cascade

```sql
-- Create test user and garden
BEGIN;
INSERT INTO users (email, hashed_password)
VALUES ('test_cascade@example.com', 'hashed');

INSERT INTO gardens (user_id, name, garden_type, size_sq_ft)
VALUES (currval('users_id_seq'), 'Test Garden', 'outdoor', 100);

-- Delete user and verify cascade
DELETE FROM users WHERE email = 'test_cascade@example.com';

-- Garden should be deleted automatically
SELECT COUNT(*) FROM gardens
WHERE name = 'Test Garden';  -- Should return 0

ROLLBACK;
```

#### Test Unique Constraints

```sql
-- Try to create duplicate sensor reading
BEGIN;
INSERT INTO sensor_readings (user_id, garden_id, reading_date, temperature_f)
VALUES (1, 1, '2026-02-01', 70.0);

-- This should fail with unique constraint violation
INSERT INTO sensor_readings (user_id, garden_id, reading_date, temperature_f)
VALUES (1, 1, '2026-02-01', 71.0);

ROLLBACK;
```

#### Test CHECK Constraints

```sql
-- Try to create garden with invalid pH
BEGIN;
INSERT INTO gardens (user_id, name, garden_type, size_sq_ft, ph_min, ph_max)
VALUES (1, 'Invalid Garden', 'outdoor', 100, 15.0, 16.0);  -- Should fail

ROLLBACK;
```

---

## Rollback Procedures

### When to Rollback

Roll back if:
- Migration causes unexpected application errors
- Performance degradation is unacceptable
- Data integrity issues are discovered
- Critical bugs are found in the constraints

### Rollback Execution

#### Phase 1 Rollback

```bash
# STOP APPLICATION FIRST
docker-compose stop backend

# Execute rollback
psql -h localhost -U your_user -d gardening_service \
  -f migrations/001_rollback_critical_constraints.sql

# Verify rollback
psql -h localhost -U your_user -d gardening_service -c "
SELECT COUNT(*) FROM pg_constraint
WHERE conname IN ('fk_companion_relationship_plant_a', 'fk_companion_relationship_plant_b');
"  # Should return 0

# Restart application
docker-compose start backend
```

#### Phase 2 Rollback

```bash
psql -h localhost -U your_user -d gardening_service \
  -f migrations/002_rollback_high_priority_constraints.sql

# Verify ENUM types are dropped
psql -h localhost -U your_user -d gardening_service -c "
SELECT COUNT(*) FROM pg_type
WHERE typname IN ('irrigation_delivery_type', 'irrigation_source_type');
"  # Should return 0
```

#### Phase 3 Rollback

```bash
psql -h localhost -U your_user -d gardening_service \
  -f migrations/003_rollback_check_constraints.sql

# Verify all CHECK constraints are removed
psql -h localhost -U your_user -d gardening_service -c "
SELECT COUNT(*) FROM pg_constraint
WHERE contype = 'c' AND conname LIKE 'check_%';
"  # Should return 0 (or only pre-existing checks)
```

---

## Troubleshooting

### Issue: Foreign Key Constraint Violation (Phase 1)

**Error:**
```
ERROR: insert or update on table "X" violates foreign key constraint "fk_X"
DETAIL: Key (column_id)=(123) is not present in table "Y".
```

**Solution:**
1. Identify orphaned records:
   ```sql
   SELECT * FROM X
   LEFT JOIN Y ON X.column_id = Y.id
   WHERE Y.id IS NULL;
   ```
2. Either:
   - Delete orphaned records, OR
   - Create missing parent records, OR
   - Set foreign key column to NULL (if allowed)

### Issue: Unique Constraint Violation

**Error:**
```
ERROR: duplicate key value violates unique constraint "unique_X"
```

**Solution:**
1. Identify duplicates:
   ```sql
   SELECT column1, column2, COUNT(*)
   FROM table_name
   GROUP BY column1, column2
   HAVING COUNT(*) > 1;
   ```
2. Resolve duplicates by:
   - Merging records
   - Deleting duplicates
   - Updating one to make it unique

### Issue: CHECK Constraint Violation (Phase 3)

**Error:**
```
ERROR: new row for relation "X" violates check constraint "check_Y"
```

**Solution:**
1. Review the constraint definition:
   ```sql
   SELECT pg_get_constraintdef(oid)
   FROM pg_constraint
   WHERE conname = 'check_Y';
   ```
2. Correct the data or application code

### Issue: Migration Takes Too Long

**Problem:** Migration exceeds maintenance window

**Solution:**
1. Cancel migration: `CTRL+C` in psql, then `ROLLBACK;`
2. Identify slow operations:
   ```sql
   SELECT pid, now() - query_start AS duration, state, query
   FROM pg_stat_activity
   WHERE state != 'idle'
   ORDER BY duration DESC;
   ```
3. Consider:
   - Adding indexes before migration
   - Running during off-peak hours
   - Splitting into smaller batches

---

## Post-Migration Verification

### Performance Check

```sql
-- Check for slow queries
SELECT mean_exec_time, calls, query
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- Queries slower than 1 second
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check table sizes
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Application Health Check

```bash
# Check application logs for errors
docker logs gardening-service-backend --since 30m | grep -i error

# Test critical API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/gardens
curl http://localhost:8000/api/plantings
```

### Constraint Verification Summary

Run this comprehensive check:

```sql
-- Summary of constraints added
WITH constraint_counts AS (
  SELECT 'Foreign Keys' AS constraint_type, COUNT(*) AS count
  FROM pg_constraint WHERE contype = 'f'
  UNION ALL
  SELECT 'Unique Constraints', COUNT(*)
  FROM pg_constraint WHERE contype = 'u'
  UNION ALL
  SELECT 'CHECK Constraints', COUNT(*)
  FROM pg_constraint WHERE contype = 'c'
)
SELECT * FROM constraint_counts;

-- Phase-specific checks
SELECT
  'Phase 1' AS phase,
  'CompanionRelationship FKs' AS check_name,
  COUNT(*) AS expected_value,
  CASE WHEN COUNT(*) = 2 THEN 'PASS' ELSE 'FAIL' END AS status
FROM pg_constraint
WHERE conrelid = 'companion_relationships'::regclass
AND conname LIKE 'fk_companion_relationship%'

UNION ALL

SELECT
  'Phase 2',
  'ENUM Types',
  COUNT(*),
  CASE WHEN COUNT(*) = 2 THEN 'PASS' ELSE 'FAIL' END
FROM pg_type
WHERE typname IN ('irrigation_delivery_type', 'irrigation_source_type')

UNION ALL

SELECT
  'Phase 3',
  'CHECK Constraints',
  COUNT(*),
  CASE WHEN COUNT(*) > 40 THEN 'PASS' ELSE 'FAIL' END
FROM pg_constraint
WHERE contype = 'c' AND conname LIKE 'check_%';
```

---

## Success Criteria

Migration is considered successful when:

- [ ] All migrations executed without errors
- [ ] All verification queries return expected results
- [ ] Unit tests pass (100% of constraint tests)
- [ ] Application starts and responds to requests
- [ ] No database errors in logs (30 minute window)
- [ ] Performance metrics within acceptable range
- [ ] Manual testing of create/update/delete operations succeeds

---

## Support and Escalation

If issues arise during migration:

1. **DO NOT PANIC** - Database backup exists
2. Capture error messages and query context
3. Check troubleshooting section above
4. If unresolvable, execute appropriate rollback script
5. Document issue for review

**Emergency Contact:**
- DBA Team: dba-team@example.com
- Database Slack: #database-support
- Escalation: Senior DB Engineer on-call

---

## Appendix: Quick Reference

### File Locations

```
migrations/
├── 001_add_critical_constraints.sql
├── 001_rollback_critical_constraints.sql
├── 002_add_high_priority_constraints.sql
├── 002_rollback_high_priority_constraints.sql
├── 003_add_check_constraints.sql
├── 003_rollback_check_constraints.sql
└── MIGRATION_EXECUTION_GUIDE.md (this file)

tests/
└── test_database_constraints.py

docs/
└── DATABASE_CONSTRAINTS_AUDIT_REPORT.md
```

### Quick Commands

```bash
# Backup
pg_dump -h localhost -U user -d gardening_service -F c -f backup.dump

# Restore
pg_restore -h localhost -U user -d gardening_service -c backup.dump

# Execute migration
psql -h localhost -U user -d gardening_service -f migrations/001_add_critical_constraints.sql

# Rollback
psql -h localhost -U user -d gardening_service -f migrations/001_rollback_critical_constraints.sql

# Run tests
pytest tests/test_database_constraints.py -v
```

---

**Document Version:** 1.0
**Last Updated:** 2026-02-01
**Next Review:** After Phase 3 deployment
