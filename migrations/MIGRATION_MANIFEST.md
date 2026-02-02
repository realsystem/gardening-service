# Migration Manifest

## Overview

This document lists all database migrations, their purposes, rollback scripts, and dependencies.

## Migration List

### Core Migrations (Applied in Order)

#### 000 - Migration Version Table
- **File**: `000_create_migration_version_table.sql`
- **Rollback**: `rollback_000_create_migration_version_table.sql`
- **Purpose**: Create version tracking table for migration management
- **Dependencies**: None
- **Reversible**: Yes
- **Data Loss on Rollback**: Migration history only
- **Applied**: 2026-02-01
- **Status**: Required

#### 001 - Critical Constraints
- **File**: `001_add_critical_constraints.sql`
- **Rollback**: `001_rollback_critical_constraints.sql`
- **Purpose**: Add foreign keys and NOT NULL constraints for data integrity
- **Dependencies**: Base schema (users, gardens, plantings, etc.)
- **Reversible**: Yes
- **Data Loss on Rollback**: None (constraints only)
- **Applied**: 2026-01-28
- **Status**: Required

#### 002 - High Priority Constraints
- **File**: `002_add_high_priority_constraints.sql`
- **Rollback**: `002_rollback_high_priority_constraints.sql`
- **Purpose**: Add additional foreign key constraints
- **Dependencies**: Migration 001
- **Reversible**: Yes
- **Data Loss on Rollback**: None (constraints only)
- **Applied**: 2026-01-28
- **Status**: Required

#### 003 - Check Constraints
- **File**: `003_add_check_constraints.sql`
- **Rollback**: `003_rollback_check_constraints.sql`
- **Purpose**: Add value validation constraints
- **Dependencies**: Migration 002
- **Reversible**: Yes
- **Data Loss on Rollback**: None (constraints only)
- **Applied**: 2026-01-28
- **Status**: Required

### Feature Migrations

#### Compliance Audit Fields
- **File**: `add_compliance_audit_fields.sql`
- **Rollback**: `rollback_add_compliance_audit_fields.sql`
- **Purpose**: Track users who attempt to create restricted plants
- **Dependencies**: users table
- **Reversible**: Yes
- **Data Loss on Rollback**: All compliance violation tracking data
- **Applied**: 2026-01-30
- **Status**: Required for compliance feature
- **Risk Level**: LOW
- **Notes**: Backs up users table before rollback recommended

#### Admin Column
- **File**: `add_is_admin_column.sql`
- **Rollback**: `rollback_add_is_admin_column.sql`
- **Purpose**: Support role-based access control for admin users
- **Dependencies**: users table
- **Reversible**: Yes
- **Data Loss on Rollback**: All admin role assignments
- **Applied**: 2026-01-31
- **Status**: Required for admin features
- **Risk Level**: HIGH
- **Notes**: Backup admin user list before rollback

#### Nutrient Profiles
- **File**: `add_nutrient_profiles.sql`
- **Rollback**: `rollback_add_nutrient_profiles.sql`
- **Purpose**: Add EC/pH optimization fields for hydroponic systems
- **Dependencies**: plant_varieties table
- **Reversible**: Yes
- **Data Loss on Rollback**: All nutrient profile configurations
- **Applied**: 2026-02-01
- **Status**: Required for nutrient optimization feature
- **Risk Level**: LOW
- **Notes**: Seed data in separate migration

#### Nutrient Profile Seed Data
- **File**: `seed_nutrient_profiles.sql`
- **Rollback**: N/A (can be manually deleted)
- **Purpose**: Populate nutrient profiles for common crops
- **Dependencies**: add_nutrient_profiles migration
- **Reversible**: Partial (can delete and re-seed)
- **Data Loss on Rollback**: Seed data only (can be re-applied)
- **Applied**: 2026-02-01
- **Status**: Optional (data only)
- **Risk Level**: LOW

### Data Migrations

#### Seed Plant Varieties
- **File**: `seed_plant_varieties.sql`
- **Rollback**: N/A (data only, can be manually deleted)
- **Purpose**: Initial plant variety data
- **Dependencies**: plant_varieties table
- **Reversible**: Partial
- **Applied**: Initial setup
- **Status**: Optional (data only)

#### Seed Plant Varieties Expanded
- **File**: `seed_plant_varieties_expanded.sql`
- **Rollback**: N/A (data only, can be manually deleted)
- **Purpose**: Extended plant variety catalog
- **Dependencies**: seed_plant_varieties migration
- **Reversible**: Partial
- **Applied**: Initial setup
- **Status**: Optional (data only)

### Fix Migrations

#### Fix Enum Case Mismatch
- **File**: `fix_enum_case_mismatch.sql`
- **Rollback**: N/A (correction only)
- **Purpose**: Fix case sensitivity in enum values
- **Dependencies**: Base schema
- **Reversible**: Partial (can revert values)
- **Applied**: Initial setup
- **Status**: Applied as needed

#### Fix Boolean Column Types
- **File**: `fix_boolean_column_types.sql`
- **Rollback**: N/A (type correction)
- **Purpose**: Ensure consistent boolean column types
- **Dependencies**: Base schema
- **Reversible**: Partial (can revert types)
- **Applied**: Initial setup
- **Status**: Applied as needed

## Migration Dependencies Graph

```
000_create_migration_version_table
  |
  ├─> 001_add_critical_constraints
  |    |
  |    └─> 002_add_high_priority_constraints
  |         |
  |         └─> 003_add_check_constraints
  |
  ├─> add_compliance_audit_fields
  |
  ├─> add_is_admin_column
  |
  └─> add_nutrient_profiles
       |
       └─> seed_nutrient_profiles
```

## Applying Migrations

### Production Deployment

```bash
# 1. Backup database
pg_dump -U gardener gardening_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Apply migrations in order
psql -U gardener -d gardening_db -f migrations/000_create_migration_version_table.sql
psql -U gardener -d gardening_db -f migrations/001_add_critical_constraints.sql
psql -U gardener -d gardening_db -f migrations/002_add_high_priority_constraints.sql
psql -U gardener -d gardening_db -f migrations/003_add_check_constraints.sql
psql -U gardener -d gardening_db -f migrations/add_compliance_audit_fields.sql
psql -U gardener -d gardening_db -f migrations/add_is_admin_column.sql
psql -U gardener -d gardening_db -f migrations/add_nutrient_profiles.sql
psql -U gardener -d gardening_db -f migrations/seed_nutrient_profiles.sql

# 3. Record migrations in version table
psql -U gardener -d gardening_db -c "
  INSERT INTO schema_migrations (version, description, applied_by) VALUES
    ('000', 'Create migration version table', 'deployment_script'),
    ('001', 'Add critical constraints', 'deployment_script'),
    ('002', 'Add high priority constraints', 'deployment_script'),
    ('003', 'Add check constraints', 'deployment_script'),
    ('add_compliance_audit_fields', 'Add compliance audit fields', 'deployment_script'),
    ('add_is_admin_column', 'Add is_admin column', 'deployment_script'),
    ('add_nutrient_profiles', 'Add nutrient profiles', 'deployment_script')
  ON CONFLICT (version) DO NOTHING;
"

# 4. Verify
psql -U gardener -d gardening_db -c "SELECT * FROM schema_migrations ORDER BY applied_at;"
```

## Rollback Order

Rollbacks must be applied in REVERSE order of application:

```bash
# Reverse order rollback
psql -U gardener -d gardening_db -f migrations/rollback_add_nutrient_profiles.sql
psql -U gardener -d gardening_db -f migrations/rollback_add_is_admin_column.sql
psql -U gardener -d gardening_db -f migrations/rollback_add_compliance_audit_fields.sql
psql -U gardener -d gardening_db -f migrations/003_rollback_check_constraints.sql
psql -U gardener -d gardening_db -f migrations/002_rollback_high_priority_constraints.sql
psql -U gardener -d gardening_db -f migrations/001_rollback_critical_constraints.sql
psql -U gardener -d gardening_db -f migrations/rollback_000_create_migration_version_table.sql
```

## Migration Status Checking

### Via Application

Application checks migration version on startup (production/staging only).

```bash
# Start application
systemctl start gardening-api

# Check logs for migration status
journalctl -u gardening-api | grep -i migration
```

### Via Database

```bash
# Check applied migrations
psql -U gardener -d gardening_db -c "
  SELECT version, description, applied_at
  FROM schema_migrations
  ORDER BY applied_at;
"

# Check for missing migrations
psql -U gardener -d gardening_db -c "
  SELECT COUNT(*) as applied_count
  FROM schema_migrations;
"
# Should match EXPECTED_MIGRATIONS count in app/utils/migration_check.py
```

### Via Admin API

```bash
# Get migration status (admin only)
curl https://api.example.com/admin/migration-status \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## Troubleshooting

### Application Won't Start

**Error**: `RuntimeError: Database schema is outdated`

**Solution**: Check and apply missing migrations

```bash
# Check which migrations are missing
psql -U gardener -d gardening_db -c "SELECT * FROM schema_migrations;"

# Apply missing migrations
psql -U gardener -d gardening_db -f migrations/<missing_migration>.sql
```

### Migration Already Applied

**Error**: `column "is_admin" already exists`

**Solution**: Migration is idempotent or already applied

```bash
# Check if migration is recorded
psql -U gardener -d gardening_db -c "
  SELECT * FROM schema_migrations
  WHERE version = 'add_is_admin_column';
"

# If not recorded, just record it (don't re-apply)
psql -U gardener -d gardening_db -c "
  INSERT INTO schema_migrations (version, description, applied_by)
  VALUES ('add_is_admin_column', 'Add is_admin column', 'manual_fix');
"
```

### Rollback Failed

**Error**: `column "is_admin" does not exist`

**Solution**: Rollback already applied or column never existed

```bash
# Check column existence
psql -U gardener -d gardening_db -c "
  SELECT column_name
  FROM information_schema.columns
  WHERE table_name = 'users' AND column_name = 'is_admin';
"

# If column doesn't exist, just update version table
psql -U gardener -d gardening_db -c "
  DELETE FROM schema_migrations
  WHERE version = 'add_is_admin_column';
"
```

## Best Practices

1. **Always Backup**: Before applying or rolling back migrations
2. **Test First**: Apply in staging before production
3. **Apply in Order**: Follow dependency graph
4. **Record Versions**: Always update `schema_migrations` table
5. **Use Transactions**: Wrap migrations in BEGIN/COMMIT where possible
6. **Check Idempotency**: Use `IF EXISTS` / `IF NOT EXISTS` clauses
7. **Document Changes**: Update this manifest for new migrations

## Adding New Migrations

### Checklist for New Migration

- [ ] Migration file created (`.sql`)
- [ ] Rollback file created (`rollback_*.sql`)
- [ ] Tested in local environment
- [ ] Tested in staging environment
- [ ] Added to `EXPECTED_MIGRATIONS` in `app/utils/migration_check.py`
- [ ] Added to this manifest
- [ ] Rollback procedure documented in `MIGRATION_ROLLBACK.md`
- [ ] Dependencies identified
- [ ] Risk level assessed
- [ ] Data loss potential documented

---

**Maintained By**: Engineering Team
**Last Updated**: 2026-02-01
**Next Review**: When adding new migrations
