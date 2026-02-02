-- Rollback Migration 002: Remove High Priority Database Constraints (Phase 2)
--
-- This script reverts the changes made in 002_add_high_priority_constraints.sql
--
-- WARNING: Rolling back these constraints will remove type safety and data
-- integrity protections. Use with caution.
--
-- Author: Database Schema Audit
-- Date: 2026-02-01

-- =============================================================================
-- PART 1: Revert Foreign Key CASCADE Policies
-- =============================================================================

-- 1.1 WateringEvent.planting_event_id
ALTER TABLE watering_events
  DROP CONSTRAINT IF EXISTS watering_events_planting_event_id_fkey;

ALTER TABLE watering_events
  ADD CONSTRAINT watering_events_planting_event_id_fkey
  FOREIGN KEY (planting_event_id)
  REFERENCES planting_events(id);

-- 1.2 GerminationEvent.plant_variety_id
ALTER TABLE germination_events
  DROP CONSTRAINT IF EXISTS germination_events_plant_variety_id_fkey;

ALTER TABLE germination_events
  ADD CONSTRAINT germination_events_plant_variety_id_fkey
  FOREIGN KEY (plant_variety_id)
  REFERENCES plant_varieties(id);

-- 1.3 GerminationEvent.seed_batch_id
ALTER TABLE germination_events
  DROP CONSTRAINT IF EXISTS germination_events_seed_batch_id_fkey;

ALTER TABLE germination_events
  ADD CONSTRAINT germination_events_seed_batch_id_fkey
  FOREIGN KEY (seed_batch_id)
  REFERENCES seed_batches(id);

-- 1.4 Structure.land_id
ALTER TABLE structures
  DROP CONSTRAINT IF EXISTS structures_land_id_fkey;

ALTER TABLE structures
  ADD CONSTRAINT structures_land_id_fkey
  FOREIGN KEY (land_id)
  REFERENCES lands(id);

-- 1.5 Tree.land_id
ALTER TABLE trees
  DROP CONSTRAINT IF EXISTS trees_land_id_fkey;

ALTER TABLE trees
  ADD CONSTRAINT trees_land_id_fkey
  FOREIGN KEY (land_id)
  REFERENCES lands(id);

-- 1.6 IrrigationZone.source_id
ALTER TABLE irrigation_zones
  DROP CONSTRAINT IF EXISTS irrigation_zones_source_id_fkey;

ALTER TABLE irrigation_zones
  ADD CONSTRAINT irrigation_zones_source_id_fkey
  FOREIGN KEY (source_id)
  REFERENCES irrigation_sources(id);

-- 1.7 IrrigationZone.land_id
ALTER TABLE irrigation_zones
  DROP CONSTRAINT IF EXISTS irrigation_zones_land_id_fkey;

ALTER TABLE irrigation_zones
  ADD CONSTRAINT irrigation_zones_land_id_fkey
  FOREIGN KEY (land_id)
  REFERENCES lands(id);

-- 1.8 IrrigationEvent.zone_id
ALTER TABLE irrigation_events
  DROP CONSTRAINT IF EXISTS irrigation_events_zone_id_fkey;

ALTER TABLE irrigation_events
  ADD CONSTRAINT irrigation_events_zone_id_fkey
  FOREIGN KEY (zone_id)
  REFERENCES irrigation_zones(id);

-- 1.9 SoilSample.garden_id
ALTER TABLE soil_samples
  DROP CONSTRAINT IF EXISTS soil_samples_garden_id_fkey;

ALTER TABLE soil_samples
  ADD CONSTRAINT soil_samples_garden_id_fkey
  FOREIGN KEY (garden_id)
  REFERENCES gardens(id);

-- 1.10 SensorReading.garden_id
ALTER TABLE sensor_readings
  DROP CONSTRAINT IF EXISTS sensor_readings_garden_id_fkey;

ALTER TABLE sensor_readings
  ADD CONSTRAINT sensor_readings_garden_id_fkey
  FOREIGN KEY (garden_id)
  REFERENCES gardens(id);

-- 1.11 CareTask.planting_event_id
ALTER TABLE care_tasks
  DROP CONSTRAINT IF EXISTS care_tasks_planting_event_id_fkey;

ALTER TABLE care_tasks
  ADD CONSTRAINT care_tasks_planting_event_id_fkey
  FOREIGN KEY (planting_event_id)
  REFERENCES planting_events(id);

-- 1.12 PlantingEvent.seed_batch_id
ALTER TABLE planting_events
  DROP CONSTRAINT IF EXISTS planting_events_seed_batch_id_fkey;

ALTER TABLE planting_events
  ADD CONSTRAINT planting_events_seed_batch_id_fkey
  FOREIGN KEY (seed_batch_id)
  REFERENCES seed_batches(id);

-- 1.13 PlantingEvent.garden_id
ALTER TABLE planting_events
  DROP CONSTRAINT IF EXISTS planting_events_garden_id_fkey;

ALTER TABLE planting_events
  ADD CONSTRAINT planting_events_garden_id_fkey
  FOREIGN KEY (garden_id)
  REFERENCES gardens(id);

-- 1.14 PlantingEvent.plant_variety_id
ALTER TABLE planting_events
  DROP CONSTRAINT IF EXISTS planting_events_plant_variety_id_fkey;

ALTER TABLE planting_events
  ADD CONSTRAINT planting_events_plant_variety_id_fkey
  FOREIGN KEY (plant_variety_id)
  REFERENCES plant_varieties(id);

-- 1.15 SeedBatch.plant_variety_id
ALTER TABLE seed_batches
  DROP CONSTRAINT IF EXISTS seed_batches_plant_variety_id_fkey;

ALTER TABLE seed_batches
  ADD CONSTRAINT seed_batches_plant_variety_id_fkey
  FOREIGN KEY (plant_variety_id)
  REFERENCES plant_varieties(id);

-- =============================================================================
-- PART 2: Remove Unique Constraints
-- =============================================================================

DROP INDEX IF EXISTS unique_source_name_per_user;
DROP INDEX IF EXISTS unique_zone_name_per_land;
DROP INDEX IF EXISTS unique_land_name_per_user;
DROP INDEX IF EXISTS unique_garden_name_per_user;

-- =============================================================================
-- PART 3: Revert NOT NULL Constraints on Timestamp Columns
-- =============================================================================

-- Note: Making columns nullable again is safe as they have default values
ALTER TABLE seed_batches
  ALTER COLUMN created_at DROP NOT NULL;

ALTER TABLE germination_events
  ALTER COLUMN created_at DROP NOT NULL;

ALTER TABLE planting_events
  ALTER COLUMN created_at DROP NOT NULL;

ALTER TABLE users
  ALTER COLUMN created_at DROP NOT NULL;

-- =============================================================================
-- PART 4: Revert NOT NULL Constraints on Data Columns
-- =============================================================================

ALTER TABLE germination_events
  ALTER COLUMN germinated DROP NOT NULL,
  ALTER COLUMN germinated DROP DEFAULT;

ALTER TABLE germination_events
  ALTER COLUMN seed_count DROP NOT NULL,
  ALTER COLUMN seed_count DROP DEFAULT;

ALTER TABLE planting_events
  ALTER COLUMN plant_count DROP NOT NULL,
  ALTER COLUMN plant_count DROP DEFAULT;

-- =============================================================================
-- PART 5: Revert ENUM Type Conversion (Back to VARCHAR)
-- =============================================================================

-- 5.1 Convert IrrigationSource.source_type back to VARCHAR
ALTER TABLE irrigation_sources
  ALTER COLUMN source_type DROP DEFAULT;

ALTER TABLE irrigation_sources
  ALTER COLUMN source_type DROP NOT NULL;

ALTER TABLE irrigation_sources
  ALTER COLUMN source_type TYPE VARCHAR(50)
  USING source_type::text;

-- 5.2 Convert IrrigationZone.delivery_type back to VARCHAR
ALTER TABLE irrigation_zones
  ALTER COLUMN delivery_type DROP DEFAULT;

ALTER TABLE irrigation_zones
  ALTER COLUMN delivery_type DROP NOT NULL;

ALTER TABLE irrigation_zones
  ALTER COLUMN delivery_type TYPE VARCHAR(50)
  USING delivery_type::text;

-- 5.3 Drop ENUM types (only if no other tables use them)
DROP TYPE IF EXISTS irrigation_source_type CASCADE;
DROP TYPE IF EXISTS irrigation_delivery_type CASCADE;

-- =============================================================================
-- VERIFICATION QUERIES (for manual testing)
-- =============================================================================

-- Uncomment to verify rollback:

-- Check that columns are nullable again:
-- SELECT table_name, column_name, is_nullable, data_type
-- FROM information_schema.columns
-- WHERE table_name IN ('irrigation_zones', 'irrigation_sources', 'planting_events', 'germination_events')
-- AND column_name IN ('delivery_type', 'source_type', 'plant_count', 'seed_count', 'germinated', 'created_at')
-- ORDER BY table_name, column_name;

-- Check that unique constraints are removed:
-- SELECT indexname
-- FROM pg_indexes
-- WHERE indexname LIKE 'unique_%';

-- Check that foreign keys have no CASCADE:
-- SELECT tc.table_name, kcu.column_name, rc.delete_rule
-- FROM information_schema.table_constraints tc
-- JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
-- JOIN information_schema.referential_constraints rc ON tc.constraint_name = rc.constraint_name
-- WHERE tc.constraint_type = 'FOREIGN KEY'
-- AND rc.delete_rule = 'CASCADE'
-- ORDER BY tc.table_name;

-- =============================================================================
-- END OF ROLLBACK
-- =============================================================================
