# Database Migration Rollback Procedures

## Overview

This document provides procedures for safely rolling back database migrations in case of failures or issues. All migrations have corresponding rollback scripts for reversibility.

## Quick Reference

### All Migrations and Their Rollbacks

| Migration | Rollback Script | Risk Level | Data Loss |
|-----------|----------------|------------|-----------|
| `000_create_migration_version_table.sql` | `rollback_000_create_migration_version_table.sql` | LOW | Migration history |
| `001_add_critical_constraints.sql` | `001_rollback_critical_constraints.sql` | HIGH | None |
| `002_add_high_priority_constraints.sql` | `002_rollback_high_priority_constraints.sql` | MEDIUM | None |
| `003_add_check_constraints.sql` | `003_rollback_check_constraints.sql` | MEDIUM | None |
| `add_compliance_audit_fields.sql` | `rollback_add_compliance_audit_fields.sql` | LOW | Compliance audit data |
| `add_is_admin_column.sql` | `rollback_add_is_admin_column.sql` | HIGH | Admin role assignments |
| `add_nutrient_profiles.sql` | `rollback_add_nutrient_profiles.sql` | LOW | Nutrient profile data |

## General Rollback Workflow

### 1. Identify the Problem

Before rolling back, confirm:
- Which migration is causing issues?
- What symptoms are occurring?
- Is rollback necessary or can the issue be fixed forward?

### 2. Check Application State

```bash
# Stop the application
systemctl stop gardening-api

# Verify no active connections
psql -U gardener -d gardening_db -c "SELECT * FROM pg_stat_activity WHERE datname = 'gardening_db';"
```

### 3. Backup Database

**ALWAYS backup before rollback:**

```bash
# Create timestamped backup
pg_dump -U gardener gardening_db > backup_before_rollback_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
ls -lh backup_before_rollback_*.sql
```

### 4. Apply Rollback

```bash
# Apply specific rollback script
psql -U gardener -d gardening_db -f migrations/rollback_<migration_name>.sql

# Check for errors
echo $?  # Should be 0 for success
```

### 5. Update Migration Version Table

```bash
# Remove migration from version table
psql -U gardener -d gardening_db -c "DELETE FROM schema_migrations WHERE version = '<version>';"
```

### 6. Verify Rollback

```bash
# Check schema
psql -U gardener -d gardening_db -c "\d+ users"  # Example table

# Verify application starts
systemctl start gardening-api
systemctl status gardening-api

# Check logs
journalctl -u gardening-api -n 50
```

## Specific Rollback Procedures

### Rollback Critical Constraints (001)

**Risk**: HIGH - Removes foreign key and NOT NULL constraints
**Data Loss**: None

```bash
# Backup
pg_dump -U gardener gardening_db > backup_rollback_001_$(date +%Y%m%d_%H%M%S).sql

# Apply rollback
psql -U gardener -d gardening_db -f migrations/001_rollback_critical_constraints.sql

# Update version
psql -U gardener -d gardening_db -c "DELETE FROM schema_migrations WHERE version = '001';"

# Verify
psql -U gardener -d gardening_db -c "
  SELECT constraint_name, table_name
  FROM information_schema.table_constraints
  WHERE table_schema = 'public'
  ORDER BY table_name;
"
```

**⚠️ Warning**: After rolling back critical constraints:
- Data integrity is NOT enforced at database level
- Application-level validation becomes critical
- Re-apply migration as soon as issue is resolved

---

### Rollback Compliance Audit Fields

**Risk**: LOW
**Data Loss**: YES - All compliance violation tracking data

```bash
# Backup (critical - contains violation history)
pg_dump -U gardener -t users gardening_db > backup_users_compliance_$(date +%Y%m%d_%H%M%S).sql

# Apply rollback
psql -U gardener -d gardening_db -f migrations/rollback_add_compliance_audit_fields.sql

# Update version
psql -U gardener -d gardening_db -c "DELETE FROM schema_migrations WHERE version = 'add_compliance_audit_fields';"

# Verify columns removed
psql -U gardener -d gardening_db -c "
  SELECT column_name
  FROM information_schema.columns
  WHERE table_name = 'users'
    AND column_name LIKE 'restricted_crop%';
"
# Should return 0 rows
```

**Impact**: Compliance service will fail to start. Requires code rollback to version before compliance feature.

---

### Rollback Admin Column

**Risk**: HIGH - Removes all admin role assignments
**Data Loss**: YES - Admin user designations

```bash
# Backup admin users first
pg_dump -U gardener -t users --data-only --column-inserts gardening_db > backup_admin_users_$(date +%Y%m%d_%H%M%S).sql

# Extract admin user IDs for restoration
psql -U gardener -d gardening_db -c "
  COPY (SELECT id, email FROM users WHERE is_admin = TRUE)
  TO '/tmp/admin_users_backup.csv'
  WITH CSV HEADER;
"

# Apply rollback
psql -U gardener -d gardening_db -f migrations/rollback_add_is_admin_column.sql

# Update version
psql -U gardener -d gardening_db -c "DELETE FROM schema_migrations WHERE version = 'add_is_admin_column';"
```

**⚠️ Critical**: After rollback, admin endpoints will be inaccessible. Requires code rollback to version before admin feature.

**To restore admin users after re-applying migration**:
```bash
# Re-apply migration
psql -U gardener -d gardening_db -f migrations/add_is_admin_column.sql

# Restore admin designations from backup CSV
psql -U gardener -d gardening_db -c "
  UPDATE users SET is_admin = TRUE
  WHERE id IN (SELECT id FROM temp_admin_backup);
"
```

---

### Rollback Nutrient Profiles

**Risk**: LOW
**Data Loss**: YES - Nutrient profile configurations

```bash
# Backup nutrient data
pg_dump -U gardener -t plant_varieties gardening_db > backup_nutrient_profiles_$(date +%Y%m%d_%H%M%S).sql

# Apply rollback
psql -U gardener -d gardening_db -f migrations/rollback_add_nutrient_profiles.sql

# Update version
psql -U gardener -d gardening_db -c "DELETE FROM schema_migrations WHERE version = 'add_nutrient_profiles';"
```

**Impact**: Nutrient optimization feature will fail. Requires code rollback or feature flag disable.

---

## Failure Recovery

### Scenario: Migration Fails Halfway

**Symptoms**: Migration started but didn't complete, database in inconsistent state

**Recovery**:

1. **Check transaction status**:
   ```bash
   psql -U gardener -d gardening_db -c "
     SELECT * FROM pg_stat_activity
     WHERE state = 'idle in transaction';
   "
   ```

2. **Kill stuck transactions if needed**:
   ```bash
   psql -U gardener -d gardening_db -c "
     SELECT pg_terminate_backend(pid)
     FROM pg_stat_activity
     WHERE datname = 'gardening_db'
       AND state = 'idle in transaction';
   "
   ```

3. **Check migration version table**:
   ```bash
   psql -U gardener -d gardening_db -c "
     SELECT * FROM schema_migrations
     ORDER BY applied_at DESC
     LIMIT 5;
   "
   ```

4. **Determine state**:
   - If migration is NOT in `schema_migrations`: Re-run migration
   - If migration IS in `schema_migrations`: Apply rollback, then re-run

5. **Verify schema state**:
   ```bash
   # Check if expected columns/tables exist
   psql -U gardener -d gardening_db -c "\d+ <table_name>"
   ```

6. **Apply fix**:
   ```bash
   # If migration partially applied:
   psql -U gardener -d gardening_db -f migrations/rollback_<migration>.sql
   psql -U gardener -d gardening_db -f migrations/<migration>.sql

   # If migration not applied:
   psql -U gardener -d gardening_db -f migrations/<migration>.sql
   ```

---

### Scenario: Application Won't Start After Migration

**Symptoms**: `RuntimeError: Database schema is outdated`

**Diagnosis**:

```bash
# Check migration status
psql -U gardener -d gardening_db -c "
  SELECT version, description, applied_at
  FROM schema_migrations
  ORDER BY applied_at;
"

# Compare with expected migrations in code
# See: app/utils/migration_check.py -> EXPECTED_MIGRATIONS
```

**Resolution**:

Option 1: **Apply missing migrations**
```bash
# Identify missing migration
# Apply it
psql -U gardener -d gardening_db -f migrations/<missing_migration>.sql

# Record in version table
psql -U gardener -d gardening_db -c "
  INSERT INTO schema_migrations (version, description, applied_by)
  VALUES ('<version>', '<description>', 'manual_recovery');
"
```

Option 2: **Rollback code to match database**
```bash
# Deploy older version of code that matches current database schema
git checkout <previous_tag>
./deploy.sh
```

---

### Scenario: Version Table Corrupted

**Symptoms**: `schema_migrations` table missing or corrupted

**Recovery**:

```bash
# Recreate migration table
psql -U gardener -d gardening_db -f migrations/000_create_migration_version_table.sql

# Manually reconstruct migration history
# Check each migration to see if it's been applied
psql -U gardener -d gardening_db -c "
  SELECT column_name
  FROM information_schema.columns
  WHERE table_name = 'users' AND column_name = 'is_admin';
"
# If returns rows, migration was applied

# Record applied migrations
psql -U gardener -d gardening_db -c "
  INSERT INTO schema_migrations (version, description, applied_by)
  VALUES
    ('001', 'Add critical constraints', 'recovery'),
    ('add_is_admin_column', 'Add is_admin column', 'recovery');
  -- Add others as needed
"
```

---

## Testing Rollbacks

### Dry Run in Staging

**Before production rollback, test in staging**:

```bash
# 1. Clone production to staging
pg_dump -h prod-db -U gardener gardening_db | psql -h staging-db -U gardener gardening_db

# 2. Apply rollback in staging
psql -h staging-db -U gardener -d gardening_db -f migrations/rollback_<migration>.sql

# 3. Verify application works
curl https://staging-api.example.com/health

# 4. Run test suite
pytest tests/

# 5. If successful, proceed to production
```

### Rollback Testing Checklist

- [ ] Database backup created
- [ ] Rollback script tested in staging
- [ ] Application tested with rolled-back schema
- [ ] Data loss documented and accepted
- [ ] Rollback procedure documented
- [ ] Team notified of maintenance window
- [ ] Monitoring/alerts configured

---

## Emergency Rollback Decision Tree

```
Migration Failure Detected
    |
    ├─> Application still running?
    |   ├─> YES: Evaluate impact
    |   |   ├─> Minor issue: Fix forward (patch migration)
    |   |   └─> Critical issue: Plan rollback window
    |   └─> NO: Emergency rollback
    |       └─> Execute rollback immediately
    |
    └─> Data integrity compromised?
        ├─> YES: STOP - Do not rollback without backup
        |   └─> Restore from backup instead
        └─> NO: Proceed with rollback
```

---

## Rollback Safety Checklist

Before executing any rollback:

- [ ] **Backup created** - Full database dump
- [ ] **Application stopped** - No active transactions
- [ ] **Team notified** - All stakeholders aware
- [ ] **Rollback script tested** - Verified in staging
- [ ] **Data loss acceptable** - Stakeholders approved
- [ ] **Recovery plan ready** - How to re-apply if needed
- [ ] **Monitoring ready** - Alerts configured for issues
- [ ] **Rollback window scheduled** - Maintenance window reserved

---

## Post-Rollback Actions

After successful rollback:

1. **Verify Application**:
   ```bash
   systemctl start gardening-api
   curl https://api.example.com/health
   ```

2. **Check Logs**:
   ```bash
   journalctl -u gardening-api -n 100 --no-pager
   ```

3. **Monitor Errors**:
   ```bash
   # Check error rate
   curl https://api.example.com/metrics | grep http_errors_total
   ```

4. **Update Documentation**:
   - Document why rollback was needed
   - Record lessons learned
   - Update rollback procedures if needed

5. **Plan Forward Fix**:
   - Identify root cause of migration failure
   - Create fix
   - Test in staging
   - Re-apply migration

---

## Prevention

### Pre-Migration Checklist

Prevent rollbacks by careful pre-migration validation:

- [ ] Migration tested in local environment
- [ ] Migration tested in staging environment
- [ ] Rollback script created and tested
- [ ] Migration is idempotent (can be re-run)
- [ ] Migration uses transactions where possible
- [ ] Large data migrations are batched
- [ ] Migration includes timing estimates
- [ ] Team reviewed migration SQL

### Migration Best Practices

1. **Use Transactions**:
   ```sql
   BEGIN;
     -- Migration steps
     ALTER TABLE ...;
   COMMIT;  -- Only commit if all steps succeed
   ```

2. **Check Before Modify**:
   ```sql
   -- Good: Check before adding
   ALTER TABLE users
     ADD COLUMN IF NOT EXISTS is_admin BOOLEAN;
   ```

3. **Make Rollback Easy**:
   ```sql
   -- Avoid mixing DDL and DML in one migration
   -- Separate schema changes from data changes
   ```

4. **Test Rollback**:
   ```bash
   # Always test rollback works
   psql -f migration.sql
   psql -f rollback_migration.sql
   ```

---

## Support

### Getting Help

If rollback fails or you're unsure:

1. **Check logs**: `journalctl -u gardening-api -n 500`
2. **Check database logs**: `tail -f /var/log/postgresql/postgresql-14-main.log`
3. **Review this document**: Follow procedures exactly
4. **Contact team**: Don't guess - ask for help

### Common Issues

**Issue**: Rollback fails with "column does not exist"
**Solution**: Column already removed, rollback already applied. Check migration version table.

**Issue**: Application still fails after rollback
**Solution**: Code still expects new schema. Deploy older code version or fix forward.

**Issue**: Data lost after rollback
**Solution**: Restore from backup created before rollback.

---

## Appendix: Quick Command Reference

```bash
# Create backup
pg_dump -U gardener gardening_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Apply rollback
psql -U gardener -d gardening_db -f migrations/rollback_<name>.sql

# Update version table
psql -U gardener -d gardening_db -c "DELETE FROM schema_migrations WHERE version = '<version>';"

# Check migration status
psql -U gardener -d gardening_db -c "SELECT * FROM schema_migrations ORDER BY applied_at;"

# Restart application
systemctl restart gardening-api

# Check status
systemctl status gardening-api
curl https://api.example.com/health
```

---

**Last Updated**: 2026-02-01
**Maintained By**: Engineering Team
**Next Review**: 2026-03-01
