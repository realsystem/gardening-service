-- Rollback Migration 001: Remove Critical Database Constraints (Phase 1)
--
-- This script reverts the changes made in 001_add_critical_constraints.sql
--
-- WARNING: Rolling back these constraints will remove important data integrity
-- protections. Only use this rollback if absolutely necessary (e.g., migration
-- failure, data incompatibility discovered after deployment).
--
-- Author: Database Schema Audit
-- Date: 2026-02-01

-- =============================================================================
-- PART 1: Remove Rule Engine Enum Constraints
-- =============================================================================

ALTER TABLE rule_results
  DROP CONSTRAINT IF EXISTS check_rule_severity_enum;

ALTER TABLE rule_results
  DROP CONSTRAINT IF EXISTS check_rule_category_enum;

-- =============================================================================
-- PART 2: Remove Unique Constraint from SensorReading
-- =============================================================================

DROP INDEX IF EXISTS unique_sensor_reading_per_day;

-- =============================================================================
-- PART 3: Revert user_id Foreign Keys to Original State (No CASCADE)
-- =============================================================================

-- Note: The original constraints may have been named differently.
-- We'll drop the CASCADE versions and recreate without CASCADE.

-- 3.1 Gardens table
ALTER TABLE gardens
  DROP CONSTRAINT IF EXISTS gardens_user_id_fkey;

ALTER TABLE gardens
  ADD CONSTRAINT gardens_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id);

-- 3.2 Seed Batches table
ALTER TABLE seed_batches
  DROP CONSTRAINT IF EXISTS seed_batches_user_id_fkey;

ALTER TABLE seed_batches
  ADD CONSTRAINT seed_batches_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id);

-- 3.3 Planting Events table
ALTER TABLE planting_events
  DROP CONSTRAINT IF EXISTS planting_events_user_id_fkey;

ALTER TABLE planting_events
  ADD CONSTRAINT planting_events_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id);

-- 3.4 Care Tasks table
ALTER TABLE care_tasks
  DROP CONSTRAINT IF EXISTS care_tasks_user_id_fkey;

ALTER TABLE care_tasks
  ADD CONSTRAINT care_tasks_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id);

-- 3.5 Sensor Readings table
ALTER TABLE sensor_readings
  DROP CONSTRAINT IF EXISTS sensor_readings_user_id_fkey;

ALTER TABLE sensor_readings
  ADD CONSTRAINT sensor_readings_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id);

-- 3.6 Soil Samples table
ALTER TABLE soil_samples
  DROP CONSTRAINT IF EXISTS soil_samples_user_id_fkey;

ALTER TABLE soil_samples
  ADD CONSTRAINT soil_samples_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id);

-- 3.7 Irrigation Events table
ALTER TABLE irrigation_events
  DROP CONSTRAINT IF EXISTS irrigation_events_user_id_fkey;

ALTER TABLE irrigation_events
  ADD CONSTRAINT irrigation_events_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id);

-- 3.8 Irrigation Zones table
ALTER TABLE irrigation_zones
  DROP CONSTRAINT IF EXISTS irrigation_zones_user_id_fkey;

ALTER TABLE irrigation_zones
  ADD CONSTRAINT irrigation_zones_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id);

-- 3.9 Irrigation Sources table
ALTER TABLE irrigation_sources
  DROP CONSTRAINT IF EXISTS irrigation_sources_user_id_fkey;

ALTER TABLE irrigation_sources
  ADD CONSTRAINT irrigation_sources_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id);

-- 3.10 Lands table
ALTER TABLE lands
  DROP CONSTRAINT IF EXISTS lands_user_id_fkey;

ALTER TABLE lands
  ADD CONSTRAINT lands_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id);

-- 3.11 Trees table
ALTER TABLE trees
  DROP CONSTRAINT IF EXISTS trees_user_id_fkey;

ALTER TABLE trees
  ADD CONSTRAINT trees_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id);

-- 3.12 Structures table
ALTER TABLE structures
  DROP CONSTRAINT IF EXISTS structures_user_id_fkey;

ALTER TABLE structures
  ADD CONSTRAINT structures_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id);

-- 3.13 Germination Events table
ALTER TABLE germination_events
  DROP CONSTRAINT IF EXISTS germination_events_user_id_fkey;

ALTER TABLE germination_events
  ADD CONSTRAINT germination_events_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id);

-- 3.14 Watering Events table
ALTER TABLE watering_events
  DROP CONSTRAINT IF EXISTS watering_events_user_id_fkey;

ALTER TABLE watering_events
  ADD CONSTRAINT watering_events_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id);

-- =============================================================================
-- PART 4: Remove CompanionRelationship Constraints
-- =============================================================================

-- Remove check constraints
ALTER TABLE companion_relationships
  DROP CONSTRAINT IF EXISTS check_optimal_within_effective;

ALTER TABLE companion_relationships
  DROP CONSTRAINT IF EXISTS check_effective_distance_positive;

ALTER TABLE companion_relationships
  DROP CONSTRAINT IF EXISTS check_not_self_companion;

ALTER TABLE companion_relationships
  DROP CONSTRAINT IF EXISTS check_normalized_pair;

-- Remove foreign key constraints
ALTER TABLE companion_relationships
  DROP CONSTRAINT IF EXISTS fk_companion_relationship_plant_b;

ALTER TABLE companion_relationships
  DROP CONSTRAINT IF EXISTS fk_companion_relationship_plant_a;

-- =============================================================================
-- VERIFICATION QUERIES (for manual testing)
-- =============================================================================

-- Uncomment these to verify rollback:

-- Check that CompanionRelationship has NO foreign keys
-- SELECT conname, contype FROM pg_constraint WHERE conrelid = 'companion_relationships'::regclass;

-- Check that user_id foreign keys have NO CASCADE
-- SELECT tc.table_name, rc.delete_rule
-- FROM information_schema.table_constraints tc
-- JOIN information_schema.referential_constraints rc ON tc.constraint_name = rc.constraint_name
-- WHERE tc.constraint_type = 'FOREIGN KEY'
-- AND tc.table_schema = 'public'
-- AND tc.constraint_name LIKE '%user_id%'
-- ORDER BY tc.table_name;

-- =============================================================================
-- END OF ROLLBACK
-- =============================================================================
