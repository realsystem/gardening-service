-- Create migration version tracking table
-- This table tracks which migrations have been applied to the database
-- Applied: 2026-02-01

CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) NOT NULL PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    description TEXT,
    checksum VARCHAR(64),  -- SHA256 hash of migration file
    execution_time_ms INTEGER,
    applied_by VARCHAR(100)  -- User/system that applied the migration
);

CREATE INDEX IF NOT EXISTS idx_schema_migrations_applied_at ON schema_migrations(applied_at);

COMMENT ON TABLE schema_migrations IS 'Tracks applied database migrations for version control';
COMMENT ON COLUMN schema_migrations.version IS 'Migration version identifier (e.g., 001, 002, etc.)';
COMMENT ON COLUMN schema_migrations.applied_at IS 'Timestamp when migration was applied';
COMMENT ON COLUMN schema_migrations.description IS 'Human-readable description of migration';
COMMENT ON COLUMN schema_migrations.checksum IS 'SHA256 hash of migration file for integrity verification';
COMMENT ON COLUMN schema_migrations.execution_time_ms IS 'Time taken to execute migration in milliseconds';
COMMENT ON COLUMN schema_migrations.applied_by IS 'User or system that applied the migration';
