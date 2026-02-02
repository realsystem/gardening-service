-- Rollback compliance audit fields from users table
-- Reverses: add_compliance_audit_fields.sql
-- WARNING: This will permanently delete all compliance audit data

-- Drop index
DROP INDEX IF EXISTS idx_users_restricted_crop_flag;

-- Remove columns
ALTER TABLE users
  DROP COLUMN IF EXISTS restricted_crop_flag,
  DROP COLUMN IF EXISTS restricted_crop_count,
  DROP COLUMN IF EXISTS restricted_crop_first_violation,
  DROP COLUMN IF EXISTS restricted_crop_last_violation,
  DROP COLUMN IF EXISTS restricted_crop_reason;
