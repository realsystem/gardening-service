-- Rollback migration version tracking table
-- Reverses: 000_create_migration_version_table.sql
-- WARNING: This will permanently delete migration version history

DROP INDEX IF EXISTS idx_schema_migrations_applied_at;
DROP TABLE IF EXISTS schema_migrations;
