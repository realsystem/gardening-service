-- Rollback Migration 003: Remove CHECK Constraints (Phase 3)
--
-- This script reverts the changes made in 003_add_check_constraints.sql
--
-- WARNING: Rolling back CHECK constraints will remove data validation at the
-- database level. Application-level validation will still apply, but invalid
-- data could be inserted directly via SQL.
--
-- Author: Database Schema Audit
-- Date: 2026-02-01

-- =============================================================================
-- PART 1: Remove User Model Constraints
-- =============================================================================

ALTER TABLE users DROP CONSTRAINT IF EXISTS check_user_first_violation_required_if_flagged;
ALTER TABLE users DROP CONSTRAINT IF EXISTS check_user_longitude_range;
ALTER TABLE users DROP CONSTRAINT IF EXISTS check_user_latitude_range;
ALTER TABLE users DROP CONSTRAINT IF EXISTS check_user_restricted_crop_count_non_negative;
ALTER TABLE users DROP CONSTRAINT IF EXISTS check_user_email_format;

-- =============================================================================
-- PART 2: Remove CareTask Model Constraints
-- =============================================================================

ALTER TABLE care_tasks DROP CONSTRAINT IF EXISTS check_care_task_due_date_after_created;

-- =============================================================================
-- PART 3: Remove WateringEvent Model Constraints
-- =============================================================================

ALTER TABLE watering_events DROP CONSTRAINT IF EXISTS check_watering_event_water_amount_non_negative;

-- =============================================================================
-- PART 4: Remove GerminationEvent Model Constraints
-- =============================================================================

ALTER TABLE germination_events DROP CONSTRAINT IF EXISTS check_germination_event_date_required_if_germinated;
ALTER TABLE germination_events DROP CONSTRAINT IF EXISTS check_germination_event_date_after_started;
ALTER TABLE germination_events DROP CONSTRAINT IF EXISTS check_germination_event_success_rate_percentage;
ALTER TABLE germination_events DROP CONSTRAINT IF EXISTS check_germination_event_germination_count_non_negative;
ALTER TABLE germination_events DROP CONSTRAINT IF EXISTS check_germination_event_seed_count_non_negative;

-- =============================================================================
-- PART 5: Remove Structure Model Constraints
-- =============================================================================

ALTER TABLE structures DROP CONSTRAINT IF EXISTS check_structure_shed_height_positive;
ALTER TABLE structures DROP CONSTRAINT IF EXISTS check_structure_position_non_negative;
ALTER TABLE structures DROP CONSTRAINT IF EXISTS check_structure_dimensions_positive;

-- =============================================================================
-- PART 6: Remove Tree Model Constraints
-- =============================================================================

ALTER TABLE trees DROP CONSTRAINT IF EXISTS check_tree_position_non_negative;
ALTER TABLE trees DROP CONSTRAINT IF EXISTS check_tree_height_non_negative;
ALTER TABLE trees DROP CONSTRAINT IF EXISTS check_tree_canopy_radius_non_negative;

-- =============================================================================
-- PART 7: Remove Land Model Constraints
-- =============================================================================

ALTER TABLE lands DROP CONSTRAINT IF EXISTS check_land_position_non_negative;
ALTER TABLE lands DROP CONSTRAINT IF EXISTS check_land_dimensions_positive;

-- =============================================================================
-- PART 8: Remove IrrigationSource Model Constraints
-- =============================================================================

ALTER TABLE irrigation_sources DROP CONSTRAINT IF EXISTS check_irrigation_source_flow_rate_positive;
ALTER TABLE irrigation_sources DROP CONSTRAINT IF EXISTS check_irrigation_source_capacity_positive;

-- =============================================================================
-- PART 9: Remove IrrigationZone Model Constraints
-- =============================================================================

ALTER TABLE irrigation_zones DROP CONSTRAINT IF EXISTS check_irrigation_zone_pressure_positive;
ALTER TABLE irrigation_zones DROP CONSTRAINT IF EXISTS check_irrigation_zone_flow_rate_positive;
ALTER TABLE irrigation_zones DROP CONSTRAINT IF EXISTS check_irrigation_zone_area_positive;

-- =============================================================================
-- PART 10: Remove IrrigationEvent Model Constraints
-- =============================================================================

ALTER TABLE irrigation_events DROP CONSTRAINT IF EXISTS check_irrigation_event_water_amount_non_negative;
ALTER TABLE irrigation_events DROP CONSTRAINT IF EXISTS check_irrigation_event_duration_positive;

-- =============================================================================
-- PART 11: Remove SoilSample Model Constraints
-- =============================================================================

ALTER TABLE soil_samples DROP CONSTRAINT IF EXISTS check_soil_sample_organic_matter_percentage;
ALTER TABLE soil_samples DROP CONSTRAINT IF EXISTS check_soil_sample_potassium_non_negative;
ALTER TABLE soil_samples DROP CONSTRAINT IF EXISTS check_soil_sample_phosphorus_non_negative;
ALTER TABLE soil_samples DROP CONSTRAINT IF EXISTS check_soil_sample_nitrogen_non_negative;
ALTER TABLE soil_samples DROP CONSTRAINT IF EXISTS check_soil_sample_ph_range;

-- =============================================================================
-- PART 12: Remove SensorReading Model Constraints
-- =============================================================================

ALTER TABLE sensor_readings DROP CONSTRAINT IF EXISTS check_sensor_reading_light_hours_range;
ALTER TABLE sensor_readings DROP CONSTRAINT IF EXISTS check_sensor_reading_humidity_percentage;
ALTER TABLE sensor_readings DROP CONSTRAINT IF EXISTS check_sensor_reading_temperature_reasonable;

-- =============================================================================
-- PART 13: Remove SeedBatch Model Constraints
-- =============================================================================

ALTER TABLE seed_batches DROP CONSTRAINT IF EXISTS check_seed_batch_harvest_year_reasonable;
ALTER TABLE seed_batches DROP CONSTRAINT IF EXISTS check_seed_batch_quantity_non_negative;

-- =============================================================================
-- PART 14: Remove PlantingEvent Model Constraints
-- =============================================================================

ALTER TABLE planting_events DROP CONSTRAINT IF EXISTS check_planting_event_visual_dimensions_positive;
ALTER TABLE planting_events DROP CONSTRAINT IF EXISTS check_planting_event_visual_placement_complete;
ALTER TABLE planting_events DROP CONSTRAINT IF EXISTS check_planting_event_expected_harvest_after_planted;
ALTER TABLE planting_events DROP CONSTRAINT IF EXISTS check_planting_event_plant_count_positive;

-- =============================================================================
-- PART 15: Remove PlantVariety Model Constraints
-- =============================================================================

ALTER TABLE plant_varieties DROP CONSTRAINT IF EXISTS check_plant_variety_solution_change_days_positive;
ALTER TABLE plant_varieties DROP CONSTRAINT IF EXISTS check_plant_variety_ph_ranges;
ALTER TABLE plant_varieties DROP CONSTRAINT IF EXISTS check_plant_variety_ec_ranges;
ALTER TABLE plant_varieties DROP CONSTRAINT IF EXISTS check_plant_variety_row_spacing_positive;
ALTER TABLE plant_varieties DROP CONSTRAINT IF EXISTS check_plant_variety_spacing_positive;
ALTER TABLE plant_varieties DROP CONSTRAINT IF EXISTS check_plant_variety_days_to_harvest_positive;
ALTER TABLE plant_varieties DROP CONSTRAINT IF EXISTS check_plant_variety_days_to_germination_positive;

-- =============================================================================
-- PART 16: Remove Garden Model Constraints
-- =============================================================================

ALTER TABLE gardens DROP CONSTRAINT IF EXISTS check_hydro_system_type_required;
ALTER TABLE gardens DROP CONSTRAINT IF EXISTS check_garden_reservoir_size_positive;
ALTER TABLE gardens DROP CONSTRAINT IF EXISTS check_garden_ph_range;
ALTER TABLE gardens DROP CONSTRAINT IF EXISTS check_garden_ec_range;
ALTER TABLE gardens DROP CONSTRAINT IF EXISTS check_garden_humidity_range;
ALTER TABLE gardens DROP CONSTRAINT IF EXISTS check_garden_temp_range;
ALTER TABLE gardens DROP CONSTRAINT IF EXISTS check_garden_light_hours_range;
ALTER TABLE gardens DROP CONSTRAINT IF EXISTS check_garden_size_positive;

-- =============================================================================
-- VERIFICATION QUERIES (for manual testing)
-- =============================================================================

-- Uncomment to verify all CHECK constraints are removed:
-- SELECT conname, conrelid::regclass AS table_name
-- FROM pg_constraint
-- WHERE contype = 'c'
-- AND connamespace = 'public'::regnamespace
-- AND conname LIKE 'check_%'
-- ORDER BY conrelid::regclass::text, conname;

-- If the above query returns any rows, there are still CHECK constraints remaining

-- =============================================================================
-- END OF ROLLBACK
-- =============================================================================
