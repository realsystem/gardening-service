-- Migration 001: Add Critical Database Constraints (Phase 1)
--
-- This migration adds critical foreign key, unique, and check constraints
-- identified in the database schema audit (2026-02-01).
--
-- CRITICAL ISSUES ADDRESSED:
-- 1. CompanionRelationship missing FK constraints (CRITICAL)
-- 2. Missing ON DELETE CASCADE on user_id columns (CRITICAL)
-- 3. SensorReading missing unique constraint on (garden_id, reading_date)
--
-- IMPORTANT: This migration assumes data is already valid.
-- If there are orphaned records, they must be cleaned up first.
--
-- Author: Database Schema Audit
-- Date: 2026-02-01

-- =============================================================================
-- PART 1: Add Foreign Key Constraints to CompanionRelationship
-- =============================================================================

-- Add FK for plant_a_id
ALTER TABLE companion_relationships
  ADD CONSTRAINT fk_companion_relationship_plant_a
  FOREIGN KEY (plant_a_id)
  REFERENCES plant_varieties(id)
  ON DELETE CASCADE;

-- Add FK for plant_b_id
ALTER TABLE companion_relationships
  ADD CONSTRAINT fk_companion_relationship_plant_b
  FOREIGN KEY (plant_b_id)
  REFERENCES plant_varieties(id)
  ON DELETE CASCADE;

-- Add check constraint: plant_a_id < plant_b_id (normalization)
ALTER TABLE companion_relationships
  ADD CONSTRAINT check_normalized_pair
  CHECK (plant_a_id < plant_b_id);

-- Add check constraint: plant_a_id != plant_b_id (no self-companionship)
ALTER TABLE companion_relationships
  ADD CONSTRAINT check_not_self_companion
  CHECK (plant_a_id != plant_b_id);

-- Add check constraint: effective_distance_m > 0
ALTER TABLE companion_relationships
  ADD CONSTRAINT check_effective_distance_positive
  CHECK (effective_distance_m > 0);

-- Add check constraint: optimal_distance_m <= effective_distance_m (if not null)
ALTER TABLE companion_relationships
  ADD CONSTRAINT check_optimal_within_effective
  CHECK (optimal_distance_m IS NULL OR optimal_distance_m <= effective_distance_m);

COMMENT ON CONSTRAINT fk_companion_relationship_plant_a ON companion_relationships
  IS 'Ensures plant_a_id references a valid plant variety. Cascades deletion to prevent orphaned relationships.';

COMMENT ON CONSTRAINT fk_companion_relationship_plant_b ON companion_relationships
  IS 'Ensures plant_b_id references a valid plant variety. Cascades deletion to prevent orphaned relationships.';

-- =============================================================================
-- PART 2: Add ON DELETE CASCADE to user_id Foreign Keys
-- =============================================================================

-- Note: PostgreSQL requires dropping and recreating FK constraints to modify ON DELETE behavior
-- We'll use ALTER TABLE ... ALTER CONSTRAINT where supported (PG 12+), otherwise drop and recreate

-- 2.1 Gardens table
ALTER TABLE gardens
  DROP CONSTRAINT IF EXISTS gardens_user_id_fkey;

ALTER TABLE gardens
  ADD CONSTRAINT gardens_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;

-- 2.2 Seed Batches table
ALTER TABLE seed_batches
  DROP CONSTRAINT IF EXISTS seed_batches_user_id_fkey;

ALTER TABLE seed_batches
  ADD CONSTRAINT seed_batches_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;

-- 2.3 Planting Events table
ALTER TABLE planting_events
  DROP CONSTRAINT IF EXISTS planting_events_user_id_fkey;

ALTER TABLE planting_events
  ADD CONSTRAINT planting_events_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;

-- 2.4 Care Tasks table
ALTER TABLE care_tasks
  DROP CONSTRAINT IF EXISTS care_tasks_user_id_fkey;

ALTER TABLE care_tasks
  ADD CONSTRAINT care_tasks_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;

-- 2.5 Sensor Readings table
ALTER TABLE sensor_readings
  DROP CONSTRAINT IF EXISTS sensor_readings_user_id_fkey;

ALTER TABLE sensor_readings
  ADD CONSTRAINT sensor_readings_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;

-- 2.6 Soil Samples table
ALTER TABLE soil_samples
  DROP CONSTRAINT IF EXISTS soil_samples_user_id_fkey;

ALTER TABLE soil_samples
  ADD CONSTRAINT soil_samples_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;

-- 2.7 Irrigation Events table
ALTER TABLE irrigation_events
  DROP CONSTRAINT IF EXISTS irrigation_events_user_id_fkey;

ALTER TABLE irrigation_events
  ADD CONSTRAINT irrigation_events_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;

-- 2.8 Irrigation Zones table
ALTER TABLE irrigation_zones
  DROP CONSTRAINT IF EXISTS irrigation_zones_user_id_fkey;

ALTER TABLE irrigation_zones
  ADD CONSTRAINT irrigation_zones_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;

-- 2.9 Irrigation Sources table
ALTER TABLE irrigation_sources
  DROP CONSTRAINT IF EXISTS irrigation_sources_user_id_fkey;

ALTER TABLE irrigation_sources
  ADD CONSTRAINT irrigation_sources_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;

-- 2.10 Lands table
ALTER TABLE lands
  DROP CONSTRAINT IF EXISTS lands_user_id_fkey;

ALTER TABLE lands
  ADD CONSTRAINT lands_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;

-- 2.11 Trees table
ALTER TABLE trees
  DROP CONSTRAINT IF EXISTS trees_user_id_fkey;

ALTER TABLE trees
  ADD CONSTRAINT trees_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;

-- 2.12 Structures table
ALTER TABLE structures
  DROP CONSTRAINT IF EXISTS structures_user_id_fkey;

ALTER TABLE structures
  ADD CONSTRAINT structures_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;

-- 2.13 Germination Events table
ALTER TABLE germination_events
  DROP CONSTRAINT IF EXISTS germination_events_user_id_fkey;

ALTER TABLE germination_events
  ADD CONSTRAINT germination_events_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;

-- 2.14 Watering Events table
ALTER TABLE watering_events
  DROP CONSTRAINT IF EXISTS watering_events_user_id_fkey;

ALTER TABLE watering_events
  ADD CONSTRAINT watering_events_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;

-- =============================================================================
-- PART 3: Add Unique Constraint to SensorReading
-- =============================================================================

-- Prevent duplicate sensor readings for the same garden on the same day
CREATE UNIQUE INDEX IF NOT EXISTS unique_sensor_reading_per_day
  ON sensor_readings(garden_id, reading_date);

COMMENT ON INDEX unique_sensor_reading_per_day
  IS 'Ensures only one sensor reading per garden per day to prevent duplicate daily data.';

-- =============================================================================
-- PART 4: Add Rule Engine Enum Constraints
-- =============================================================================

-- Verify that rule categories and severities are properly constrained
-- These should already exist as CHECK constraints from the enum definitions
-- We're adding explicit named constraints for clarity and rollback support

-- Note: If using PostgreSQL ENUMs, these are already constrained at the type level
-- If using VARCHAR with application-level enums, add CHECK constraints:

DO $$
BEGIN
  -- Check if we're using VARCHAR for enum columns (not native ENUM types)
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'rule_results'
    AND column_name = 'category'
    AND data_type = 'character varying'
  ) THEN
    -- Add CHECK constraint for category if not exists
    IF NOT EXISTS (
      SELECT 1 FROM information_schema.check_constraints
      WHERE constraint_name = 'check_rule_category_enum'
    ) THEN
      ALTER TABLE rule_results
        ADD CONSTRAINT check_rule_category_enum
        CHECK (category IN (
          'COMPANION_PLANTING',
          'SOIL_NUTRIENTS',
          'IRRIGATION_TIMING',
          'HARVEST_TIMING',
          'FERTILIZER_APPLICATION',
          'PEST_PREVENTION',
          'DISEASE_PREVENTION',
          'CROP_ROTATION',
          'MICROCLIMATE',
          'NUTRIENT_TIMING'
        ));
    END IF;

    -- Add CHECK constraint for severity if not exists
    IF NOT EXISTS (
      SELECT 1 FROM information_schema.check_constraints
      WHERE constraint_name = 'check_rule_severity_enum'
    ) THEN
      ALTER TABLE rule_results
        ADD CONSTRAINT check_rule_severity_enum
        CHECK (severity IN ('INFO', 'WARNING', 'CRITICAL'));
    END IF;
  END IF;
END $$;

-- =============================================================================
-- VERIFICATION QUERIES (for manual testing)
-- =============================================================================

-- Uncomment these to verify constraints after migration:

-- Check CompanionRelationship foreign keys
-- SELECT conname, contype FROM pg_constraint WHERE conrelid = 'companion_relationships'::regclass;

-- Check user_id cascades
-- SELECT tc.table_name, tc.constraint_name, rc.update_rule, rc.delete_rule
-- FROM information_schema.table_constraints tc
-- JOIN information_schema.referential_constraints rc ON tc.constraint_name = rc.constraint_name
-- WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
-- AND rc.delete_rule = 'CASCADE'
-- ORDER BY tc.table_name;

-- Check SensorReading unique constraint
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'sensor_readings';

-- =============================================================================
-- END OF MIGRATION
-- =============================================================================
