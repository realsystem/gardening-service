-- Migration 002: Add High Priority Database Constraints (Phase 2)
--
-- This migration adds high-priority constraints identified in the database
-- schema audit (2026-02-01).
--
-- HIGH PRIORITY ISSUES ADDRESSED:
-- 1. Convert delivery_type and source_type to ENUMs for type safety
-- 2. Make plant_count, seed_count, germinated columns NOT NULL
-- 3. Add unique constraints for user-scoped names
-- 4. Add ON DELETE/UPDATE policies to remaining foreign keys
--
-- PREREQUISITES:
-- - Migration 001 must be applied first
-- - All existing data must be valid (no NULL values in columns being made NOT NULL)
--
-- Author: Database Schema Audit
-- Date: 2026-02-01

-- =============================================================================
-- PART 1: Convert String Columns to ENUMs
-- =============================================================================

-- 1.1 Create ENUM types
CREATE TYPE irrigation_delivery_type AS ENUM (
  'drip',
  'sprinkler',
  'soaker_hose',
  'manual',
  'misting',
  'subsurface'
);

CREATE TYPE irrigation_source_type AS ENUM (
  'municipal',
  'well',
  'rainwater',
  'reclaimed',
  'surface_water',
  'other'
);

-- 1.2 Alter IrrigationZone.delivery_type column
-- Set default for existing NULL values before making it NOT NULL
UPDATE irrigation_zones
SET delivery_type = 'manual'
WHERE delivery_type IS NULL OR delivery_type = '';

-- Convert to ENUM (requires intermediate step due to type incompatibility)
ALTER TABLE irrigation_zones
  ALTER COLUMN delivery_type TYPE irrigation_delivery_type
  USING delivery_type::irrigation_delivery_type;

ALTER TABLE irrigation_zones
  ALTER COLUMN delivery_type SET NOT NULL;

ALTER TABLE irrigation_zones
  ALTER COLUMN delivery_type SET DEFAULT 'drip';

-- 1.3 Alter IrrigationSource.source_type column
UPDATE irrigation_sources
SET source_type = 'municipal'
WHERE source_type IS NULL OR source_type = '';

ALTER TABLE irrigation_sources
  ALTER COLUMN source_type TYPE irrigation_source_type
  USING source_type::irrigation_source_type;

ALTER TABLE irrigation_sources
  ALTER COLUMN source_type SET NOT NULL;

ALTER TABLE irrigation_sources
  ALTER COLUMN source_type SET DEFAULT 'municipal';

COMMENT ON COLUMN irrigation_zones.delivery_type
  IS 'Type of irrigation delivery method (ENUM enforced at database level)';

COMMENT ON COLUMN irrigation_sources.source_type
  IS 'Type of water source for irrigation (ENUM enforced at database level)';

-- =============================================================================
-- PART 2: Make Critical Columns NOT NULL
-- =============================================================================

-- 2.1 PlantingEvent.plant_count
-- Set default value for NULL entries before making NOT NULL
UPDATE planting_events
SET plant_count = 1
WHERE plant_count IS NULL;

ALTER TABLE planting_events
  ALTER COLUMN plant_count SET NOT NULL;

ALTER TABLE planting_events
  ALTER COLUMN plant_count SET DEFAULT 1;

-- 2.2 GerminationEvent.seed_count
UPDATE germination_events
SET seed_count = 0
WHERE seed_count IS NULL;

ALTER TABLE germination_events
  ALTER COLUMN seed_count SET NOT NULL;

ALTER TABLE germination_events
  ALTER COLUMN seed_count SET DEFAULT 0;

-- 2.3 GerminationEvent.germinated
UPDATE germination_events
SET germinated = FALSE
WHERE germinated IS NULL;

ALTER TABLE germination_events
  ALTER COLUMN germinated SET NOT NULL;

ALTER TABLE germination_events
  ALTER COLUMN germinated SET DEFAULT FALSE;

-- 2.4 User.created_at (should always have server default)
ALTER TABLE users
  ALTER COLUMN created_at SET NOT NULL;

-- 2.5 PlantingEvent.created_at
ALTER TABLE planting_events
  ALTER COLUMN created_at SET NOT NULL;

-- 2.6 GerminationEvent.created_at
ALTER TABLE germination_events
  ALTER COLUMN created_at SET NOT NULL;

-- 2.7 SeedBatch.created_at
ALTER TABLE seed_batches
  ALTER COLUMN created_at SET NOT NULL;

-- =============================================================================
-- PART 3: Add Unique Constraints for User-Scoped Names
-- =============================================================================

-- 3.1 Garden names should be unique per user
CREATE UNIQUE INDEX IF NOT EXISTS unique_garden_name_per_user
  ON gardens(user_id, LOWER(name));

COMMENT ON INDEX unique_garden_name_per_user
  IS 'Ensures garden names are unique per user (case-insensitive)';

-- 3.2 Land names should be unique per user
CREATE UNIQUE INDEX IF NOT EXISTS unique_land_name_per_user
  ON lands(user_id, LOWER(name));

COMMENT ON INDEX unique_land_name_per_user
  IS 'Ensures land names are unique per user (case-insensitive)';

-- 3.3 Irrigation zone names should be unique per land
CREATE UNIQUE INDEX IF NOT EXISTS unique_zone_name_per_land
  ON irrigation_zones(land_id, LOWER(name));

COMMENT ON INDEX unique_zone_name_per_land
  IS 'Ensures irrigation zone names are unique per land (case-insensitive)';

-- 3.4 Irrigation source names should be unique per user
CREATE UNIQUE INDEX IF NOT EXISTS unique_source_name_per_user
  ON irrigation_sources(user_id, LOWER(name));

COMMENT ON INDEX unique_source_name_per_user
  IS 'Ensures irrigation source names are unique per user (case-insensitive)';

-- =============================================================================
-- PART 4: Add Missing ON DELETE/UPDATE Policies
-- =============================================================================

-- 4.1 SeedBatch.plant_variety_id should RESTRICT (don't delete varieties in use)
ALTER TABLE seed_batches
  DROP CONSTRAINT IF EXISTS seed_batches_plant_variety_id_fkey;

ALTER TABLE seed_batches
  ADD CONSTRAINT seed_batches_plant_variety_id_fkey
  FOREIGN KEY (plant_variety_id)
  REFERENCES plant_varieties(id)
  ON DELETE RESTRICT
  ON UPDATE CASCADE;

-- 4.2 PlantingEvent.plant_variety_id should RESTRICT
ALTER TABLE planting_events
  DROP CONSTRAINT IF EXISTS planting_events_plant_variety_id_fkey;

ALTER TABLE planting_events
  ADD CONSTRAINT planting_events_plant_variety_id_fkey
  FOREIGN KEY (plant_variety_id)
  REFERENCES plant_varieties(id)
  ON DELETE RESTRICT
  ON UPDATE CASCADE;

-- 4.3 PlantingEvent.garden_id should CASCADE
ALTER TABLE planting_events
  DROP CONSTRAINT IF EXISTS planting_events_garden_id_fkey;

ALTER TABLE planting_events
  ADD CONSTRAINT planting_events_garden_id_fkey
  FOREIGN KEY (garden_id)
  REFERENCES gardens(id)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

-- 4.4 PlantingEvent.seed_batch_id should SET NULL (preserve planting if batch deleted)
ALTER TABLE planting_events
  DROP CONSTRAINT IF EXISTS planting_events_seed_batch_id_fkey;

ALTER TABLE planting_events
  ADD CONSTRAINT planting_events_seed_batch_id_fkey
  FOREIGN KEY (seed_batch_id)
  REFERENCES seed_batches(id)
  ON DELETE SET NULL
  ON UPDATE CASCADE;

-- 4.5 CareTask.planting_event_id should CASCADE
ALTER TABLE care_tasks
  DROP CONSTRAINT IF EXISTS care_tasks_planting_event_id_fkey;

ALTER TABLE care_tasks
  ADD CONSTRAINT care_tasks_planting_event_id_fkey
  FOREIGN KEY (planting_event_id)
  REFERENCES planting_events(id)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

-- 4.6 SensorReading.garden_id should CASCADE
ALTER TABLE sensor_readings
  DROP CONSTRAINT IF EXISTS sensor_readings_garden_id_fkey;

ALTER TABLE sensor_readings
  ADD CONSTRAINT sensor_readings_garden_id_fkey
  FOREIGN KEY (garden_id)
  REFERENCES gardens(id)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

-- 4.7 SoilSample.garden_id should CASCADE
ALTER TABLE soil_samples
  DROP CONSTRAINT IF EXISTS soil_samples_garden_id_fkey;

ALTER TABLE soil_samples
  ADD CONSTRAINT soil_samples_garden_id_fkey
  FOREIGN KEY (garden_id)
  REFERENCES gardens(id)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

-- 4.8 IrrigationEvent.zone_id should CASCADE
ALTER TABLE irrigation_events
  DROP CONSTRAINT IF EXISTS irrigation_events_zone_id_fkey;

ALTER TABLE irrigation_events
  ADD CONSTRAINT irrigation_events_zone_id_fkey
  FOREIGN KEY (zone_id)
  REFERENCES irrigation_zones(id)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

-- 4.9 IrrigationZone.land_id should CASCADE
ALTER TABLE irrigation_zones
  DROP CONSTRAINT IF EXISTS irrigation_zones_land_id_fkey;

ALTER TABLE irrigation_zones
  ADD CONSTRAINT irrigation_zones_land_id_fkey
  FOREIGN KEY (land_id)
  REFERENCES lands(id)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

-- 4.10 IrrigationZone.source_id should SET NULL (zone can exist without source)
ALTER TABLE irrigation_zones
  DROP CONSTRAINT IF EXISTS irrigation_zones_source_id_fkey;

ALTER TABLE irrigation_zones
  ADD CONSTRAINT irrigation_zones_source_id_fkey
  FOREIGN KEY (source_id)
  REFERENCES irrigation_sources(id)
  ON DELETE SET NULL
  ON UPDATE CASCADE;

-- 4.11 Tree.land_id should CASCADE
ALTER TABLE trees
  DROP CONSTRAINT IF EXISTS trees_land_id_fkey;

ALTER TABLE trees
  ADD CONSTRAINT trees_land_id_fkey
  FOREIGN KEY (land_id)
  REFERENCES lands(id)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

-- 4.12 Structure.land_id should CASCADE
ALTER TABLE structures
  DROP CONSTRAINT IF EXISTS structures_land_id_fkey;

ALTER TABLE structures
  ADD CONSTRAINT structures_land_id_fkey
  FOREIGN KEY (land_id)
  REFERENCES lands(id)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

-- 4.13 GerminationEvent.seed_batch_id should SET NULL
ALTER TABLE germination_events
  DROP CONSTRAINT IF EXISTS germination_events_seed_batch_id_fkey;

ALTER TABLE germination_events
  ADD CONSTRAINT germination_events_seed_batch_id_fkey
  FOREIGN KEY (seed_batch_id)
  REFERENCES seed_batches(id)
  ON DELETE SET NULL
  ON UPDATE CASCADE;

-- 4.14 GerminationEvent.plant_variety_id should RESTRICT
ALTER TABLE germination_events
  DROP CONSTRAINT IF EXISTS germination_events_plant_variety_id_fkey;

ALTER TABLE germination_events
  ADD CONSTRAINT germination_events_plant_variety_id_fkey
  FOREIGN KEY (plant_variety_id)
  REFERENCES plant_varieties(id)
  ON DELETE RESTRICT
  ON UPDATE CASCADE;

-- 4.15 WateringEvent.planting_event_id should CASCADE
ALTER TABLE watering_events
  DROP CONSTRAINT IF EXISTS watering_events_planting_event_id_fkey;

ALTER TABLE watering_events
  ADD CONSTRAINT watering_events_planting_event_id_fkey
  FOREIGN KEY (planting_event_id)
  REFERENCES planting_events(id)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

-- =============================================================================
-- VERIFICATION QUERIES (for manual testing)
-- =============================================================================

-- Uncomment to verify ENUMs:
-- SELECT column_name, udt_name, is_nullable
-- FROM information_schema.columns
-- WHERE table_name IN ('irrigation_zones', 'irrigation_sources')
-- AND column_name IN ('delivery_type', 'source_type');

-- Uncomment to verify NOT NULL columns:
-- SELECT table_name, column_name, is_nullable
-- FROM information_schema.columns
-- WHERE table_name IN ('planting_events', 'germination_events', 'users', 'seed_batches')
-- AND column_name IN ('plant_count', 'seed_count', 'germinated', 'created_at')
-- ORDER BY table_name, column_name;

-- Uncomment to verify unique constraints:
-- SELECT indexname, indexdef
-- FROM pg_indexes
-- WHERE tablename IN ('gardens', 'lands', 'irrigation_zones', 'irrigation_sources')
-- AND indexname LIKE 'unique_%';

-- Uncomment to verify CASCADE policies:
-- SELECT tc.table_name, kcu.column_name, rc.delete_rule, rc.update_rule
-- FROM information_schema.table_constraints tc
-- JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
-- JOIN information_schema.referential_constraints rc ON tc.constraint_name = rc.constraint_name
-- WHERE tc.constraint_type = 'FOREIGN KEY'
-- AND tc.table_schema = 'public'
-- ORDER BY tc.table_name, kcu.column_name;

-- =============================================================================
-- END OF MIGRATION
-- =============================================================================
