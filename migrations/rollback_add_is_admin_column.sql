-- Rollback is_admin column from users table
-- Reverses: add_is_admin_column.sql
-- WARNING: This will permanently delete all admin role assignments

-- Drop index if it was created
DROP INDEX IF EXISTS ix_users_is_admin;

-- Remove column
ALTER TABLE users
  DROP COLUMN IF EXISTS is_admin;
