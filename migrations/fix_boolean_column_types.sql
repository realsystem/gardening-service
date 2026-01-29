-- Migration: Fix boolean column type mismatch
-- Date: 2026-01-29
-- Issue: is_hydroponic column was created as integer instead of boolean
--
-- Problem:
--   Database:  is_hydroponic integer NOT NULL DEFAULT 0
--   Python:    is_hydroponic = Column(Boolean, nullable=False, default=False)
--
-- Error:
--   column "is_hydroponic" is of type integer but expression is of type boolean
--
-- Solution:
--   Convert integer column to boolean (0 -> false, non-zero -> true)

-- Fix is_hydroponic column in gardens table
ALTER TABLE gardens ALTER COLUMN is_hydroponic DROP DEFAULT;
ALTER TABLE gardens ALTER COLUMN is_hydroponic TYPE boolean USING (is_hydroponic::integer != 0);
ALTER TABLE gardens ALTER COLUMN is_hydroponic SET DEFAULT false;

-- Verification
\echo 'Verifying is_hydroponic column is now boolean...'
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'gardens' AND column_name = 'is_hydroponic';

-- Check all boolean columns are correct
\echo 'All boolean columns in database:'
SELECT table_name, column_name, data_type, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND (column_name LIKE 'is_%' OR column_name LIKE '%_bool%' OR column_name = 'is_recurring')
ORDER BY table_name, column_name;
