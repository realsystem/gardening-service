-- Add is_admin column to users table
-- This column supports role-based access control for admin users
-- Applied: 2026-01-31

-- Add is_admin column with default value false
ALTER TABLE users
ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT false;

-- Create index for faster admin user queries (optional, uncomment if needed)
-- CREATE INDEX IF NOT EXISTS ix_users_is_admin ON users(is_admin) WHERE is_admin = true;
