-- Migration 003: Add CHECK Constraints for Data Quality (Phase 3)
--
-- This migration adds CHECK constraints to enforce business rules and data
-- validation at the database level, identified in the schema audit (2026-02-01).
--
-- DATA QUALITY RULES ENFORCED:
-- 1. Range constraints (min/max values)
-- 2. Positive value constraints
-- 3. Percentage constraints (0-100)
-- 4. Conditional constraints (business rules)
-- 5. Date/time logical constraints
--
-- PREREQUISITES:
-- - Migrations 001 and 002 must be applied first
-- - All existing data must be valid (no values violating constraints)
--
-- Author: Database Schema Audit
-- Date: 2026-02-01

-- =============================================================================
-- PART 1: Garden Model Constraints
-- =============================================================================

ALTER TABLE gardens
  ADD CONSTRAINT check_garden_size_positive
  CHECK (size_sq_ft > 0);

ALTER TABLE gardens
  ADD CONSTRAINT check_garden_light_hours_range
  CHECK (light_hours_per_day IS NULL OR (light_hours_per_day >= 0 AND light_hours_per_day <= 24));

ALTER TABLE gardens
  ADD CONSTRAINT check_garden_temp_range
  CHECK (
    (temp_min_f IS NULL AND temp_max_f IS NULL) OR
    (temp_min_f IS NOT NULL AND temp_max_f IS NOT NULL AND temp_min_f <= temp_max_f)
  );

ALTER TABLE gardens
  ADD CONSTRAINT check_garden_humidity_range
  CHECK (
    (humidity_min_percent IS NULL AND humidity_max_percent IS NULL) OR
    (humidity_min_percent IS NOT NULL AND humidity_max_percent IS NOT NULL AND
     humidity_min_percent >= 0 AND humidity_max_percent <= 100 AND
     humidity_min_percent <= humidity_max_percent)
  );

ALTER TABLE gardens
  ADD CONSTRAINT check_garden_ec_range
  CHECK (
    (ec_min IS NULL AND ec_max IS NULL) OR
    (ec_min IS NOT NULL AND ec_max IS NOT NULL AND
     ec_min >= 0 AND ec_max <= 10 AND ec_min <= ec_max)
  );

ALTER TABLE gardens
  ADD CONSTRAINT check_garden_ph_range
  CHECK (
    (ph_min IS NULL AND ph_max IS NULL) OR
    (ph_min IS NOT NULL AND ph_max IS NOT NULL AND
     ph_min >= 0 AND ph_max <= 14 AND ph_min <= ph_max)
  );

ALTER TABLE gardens
  ADD CONSTRAINT check_garden_reservoir_size_positive
  CHECK (reservoir_size_liters IS NULL OR reservoir_size_liters > 0);

-- Conditional: if is_hydroponic=true, then hydro_system_type must be set
ALTER TABLE gardens
  ADD CONSTRAINT check_hydro_system_type_required
  CHECK (NOT is_hydroponic OR hydro_system_type IS NOT NULL);

-- =============================================================================
-- PART 2: PlantVariety Model Constraints
-- =============================================================================

ALTER TABLE plant_varieties
  ADD CONSTRAINT check_plant_variety_days_to_germination_positive
  CHECK (
    (days_to_germination_min IS NULL AND days_to_germination_max IS NULL) OR
    (days_to_germination_min > 0 AND days_to_germination_max > 0 AND
     days_to_germination_min <= days_to_germination_max)
  );

ALTER TABLE plant_varieties
  ADD CONSTRAINT check_plant_variety_days_to_harvest_positive
  CHECK (days_to_harvest IS NULL OR days_to_harvest > 0);

ALTER TABLE plant_varieties
  ADD CONSTRAINT check_plant_variety_spacing_positive
  CHECK (spacing_inches IS NULL OR spacing_inches > 0);

ALTER TABLE plant_varieties
  ADD CONSTRAINT check_plant_variety_row_spacing_positive
  CHECK (row_spacing_inches IS NULL OR row_spacing_inches > 0);

ALTER TABLE plant_varieties
  ADD CONSTRAINT check_plant_variety_ec_ranges
  CHECK (
    (seedling_ec_min IS NULL OR seedling_ec_min >= 0) AND
    (seedling_ec_max IS NULL OR (seedling_ec_max >= 0 AND seedling_ec_max <= 10)) AND
    (vegetative_ec_min IS NULL OR vegetative_ec_min >= 0) AND
    (vegetative_ec_max IS NULL OR (vegetative_ec_max >= 0 AND vegetative_ec_max <= 10)) AND
    (flowering_ec_min IS NULL OR flowering_ec_min >= 0) AND
    (flowering_ec_max IS NULL OR (flowering_ec_max >= 0 AND flowering_ec_max <= 10)) AND
    (fruiting_ec_min IS NULL OR fruiting_ec_min >= 0) AND
    (fruiting_ec_max IS NULL OR (fruiting_ec_max >= 0 AND fruiting_ec_max <= 10))
  );

ALTER TABLE plant_varieties
  ADD CONSTRAINT check_plant_variety_ph_ranges
  CHECK (
    (optimal_ph_min IS NULL OR (optimal_ph_min >= 0 AND optimal_ph_min <= 14)) AND
    (optimal_ph_max IS NULL OR (optimal_ph_max >= 0 AND optimal_ph_max <= 14)) AND
    (optimal_ph_min IS NULL OR optimal_ph_max IS NULL OR optimal_ph_min <= optimal_ph_max)
  );

ALTER TABLE plant_varieties
  ADD CONSTRAINT check_plant_variety_solution_change_days_positive
  CHECK (
    (solution_change_days_min IS NULL OR solution_change_days_min > 0) AND
    (solution_change_days_max IS NULL OR solution_change_days_max > 0) AND
    (solution_change_days_min IS NULL OR solution_change_days_max IS NULL OR
     solution_change_days_min <= solution_change_days_max)
  );

-- =============================================================================
-- PART 3: PlantingEvent Model Constraints
-- =============================================================================

ALTER TABLE planting_events
  ADD CONSTRAINT check_planting_event_plant_count_positive
  CHECK (plant_count > 0);

ALTER TABLE planting_events
  ADD CONSTRAINT check_planting_event_expected_harvest_after_planted
  CHECK (expected_harvest_date IS NULL OR expected_harvest_date >= planted_date);

-- Conditional: if visual_x and visual_y are set, width and height must also be set
ALTER TABLE planting_events
  ADD CONSTRAINT check_planting_event_visual_placement_complete
  CHECK (
    (visual_x IS NULL AND visual_y IS NULL AND visual_width IS NULL AND visual_height IS NULL) OR
    (visual_x IS NOT NULL AND visual_y IS NOT NULL AND visual_width IS NOT NULL AND visual_height IS NOT NULL)
  );

ALTER TABLE planting_events
  ADD CONSTRAINT check_planting_event_visual_dimensions_positive
  CHECK (
    (visual_width IS NULL OR visual_width > 0) AND
    (visual_height IS NULL OR visual_height > 0)
  );

-- =============================================================================
-- PART 4: SeedBatch Model Constraints
-- =============================================================================

ALTER TABLE seed_batches
  ADD CONSTRAINT check_seed_batch_quantity_non_negative
  CHECK (quantity IS NULL OR quantity >= 0);

ALTER TABLE seed_batches
  ADD CONSTRAINT check_seed_batch_harvest_year_reasonable
  CHECK (harvest_year IS NULL OR (harvest_year >= 1900 AND harvest_year <= 2100));

-- =============================================================================
-- PART 5: SensorReading Model Constraints
-- =============================================================================

ALTER TABLE sensor_readings
  ADD CONSTRAINT check_sensor_reading_temperature_reasonable
  CHECK (temperature_f IS NULL OR (temperature_f >= -50 AND temperature_f <= 150));

ALTER TABLE sensor_readings
  ADD CONSTRAINT check_sensor_reading_humidity_percentage
  CHECK (humidity_percent IS NULL OR (humidity_percent >= 0 AND humidity_percent <= 100));

ALTER TABLE sensor_readings
  ADD CONSTRAINT check_sensor_reading_light_hours_range
  CHECK (light_hours IS NULL OR (light_hours >= 0 AND light_hours <= 24));

-- =============================================================================
-- PART 6: SoilSample Model Constraints
-- =============================================================================

ALTER TABLE soil_samples
  ADD CONSTRAINT check_soil_sample_ph_range
  CHECK (ph_level IS NULL OR (ph_level >= 0 AND ph_level <= 14));

ALTER TABLE soil_samples
  ADD CONSTRAINT check_soil_sample_nitrogen_non_negative
  CHECK (nitrogen_ppm IS NULL OR nitrogen_ppm >= 0);

ALTER TABLE soil_samples
  ADD CONSTRAINT check_soil_sample_phosphorus_non_negative
  CHECK (phosphorus_ppm IS NULL OR phosphorus_ppm >= 0);

ALTER TABLE soil_samples
  ADD CONSTRAINT check_soil_sample_potassium_non_negative
  CHECK (potassium_ppm IS NULL OR potassium_ppm >= 0);

ALTER TABLE soil_samples
  ADD CONSTRAINT check_soil_sample_organic_matter_percentage
  CHECK (organic_matter_percent IS NULL OR (organic_matter_percent >= 0 AND organic_matter_percent <= 100));

-- =============================================================================
-- PART 7: IrrigationEvent Model Constraints
-- =============================================================================

ALTER TABLE irrigation_events
  ADD CONSTRAINT check_irrigation_event_duration_positive
  CHECK (duration_minutes IS NULL OR duration_minutes > 0);

ALTER TABLE irrigation_events
  ADD CONSTRAINT check_irrigation_event_water_amount_non_negative
  CHECK (water_amount_liters IS NULL OR water_amount_liters >= 0);

-- =============================================================================
-- PART 8: IrrigationZone Model Constraints
-- =============================================================================

ALTER TABLE irrigation_zones
  ADD CONSTRAINT check_irrigation_zone_area_positive
  CHECK (area_sq_m IS NULL OR area_sq_m > 0);

ALTER TABLE irrigation_zones
  ADD CONSTRAINT check_irrigation_zone_flow_rate_positive
  CHECK (flow_rate_lpm IS NULL OR flow_rate_lpm > 0);

ALTER TABLE irrigation_zones
  ADD CONSTRAINT check_irrigation_zone_pressure_positive
  CHECK (pressure_psi IS NULL OR pressure_psi > 0);

-- =============================================================================
-- PART 9: IrrigationSource Model Constraints
-- =============================================================================

ALTER TABLE irrigation_sources
  ADD CONSTRAINT check_irrigation_source_capacity_positive
  CHECK (capacity_liters IS NULL OR capacity_liters > 0);

ALTER TABLE irrigation_sources
  ADD CONSTRAINT check_irrigation_source_flow_rate_positive
  CHECK (flow_rate_lpm IS NULL OR flow_rate_lpm > 0);

-- =============================================================================
-- PART 10: Land Model Constraints
-- =============================================================================

ALTER TABLE lands
  ADD CONSTRAINT check_land_dimensions_positive
  CHECK (width > 0 AND height > 0);

ALTER TABLE lands
  ADD CONSTRAINT check_land_position_non_negative
  CHECK (
    (position_x IS NULL OR position_x >= 0) AND
    (position_y IS NULL OR position_y >= 0)
  );

-- =============================================================================
-- PART 11: Tree Model Constraints
-- =============================================================================

ALTER TABLE trees
  ADD CONSTRAINT check_tree_canopy_radius_non_negative
  CHECK (canopy_radius_m >= 0);

ALTER TABLE trees
  ADD CONSTRAINT check_tree_height_non_negative
  CHECK (height_m IS NULL OR height_m >= 0);

ALTER TABLE trees
  ADD CONSTRAINT check_tree_position_non_negative
  CHECK (position_x >= 0 AND position_y >= 0);

-- =============================================================================
-- PART 12: Structure Model Constraints
-- =============================================================================

ALTER TABLE structures
  ADD CONSTRAINT check_structure_dimensions_positive
  CHECK (width > 0 AND height > 0);

ALTER TABLE structures
  ADD CONSTRAINT check_structure_position_non_negative
  CHECK (position_x >= 0 AND position_y >= 0);

ALTER TABLE structures
  ADD CONSTRAINT check_structure_shed_height_positive
  CHECK (shed_height_m IS NULL OR shed_height_m > 0);

-- =============================================================================
-- PART 13: GerminationEvent Model Constraints
-- =============================================================================

ALTER TABLE germination_events
  ADD CONSTRAINT check_germination_event_seed_count_non_negative
  CHECK (seed_count >= 0);

ALTER TABLE germination_events
  ADD CONSTRAINT check_germination_event_germination_count_non_negative
  CHECK (germination_count IS NULL OR germination_count >= 0);

ALTER TABLE germination_events
  ADD CONSTRAINT check_germination_event_success_rate_percentage
  CHECK (germination_success_rate IS NULL OR
         (germination_success_rate >= 0 AND germination_success_rate <= 100));

ALTER TABLE germination_events
  ADD CONSTRAINT check_germination_event_date_after_started
  CHECK (germination_date IS NULL OR germination_date >= started_date);

-- Conditional: if germinated=true, germination_date must be set
ALTER TABLE germination_events
  ADD CONSTRAINT check_germination_event_date_required_if_germinated
  CHECK (NOT germinated OR germination_date IS NOT NULL);

-- =============================================================================
-- PART 14: WateringEvent Model Constraints
-- =============================================================================

ALTER TABLE watering_events
  ADD CONSTRAINT check_watering_event_water_amount_non_negative
  CHECK (water_amount_liters IS NULL OR water_amount_liters >= 0);

-- =============================================================================
-- PART 15: CareTask Model Constraints
-- =============================================================================

ALTER TABLE care_tasks
  ADD CONSTRAINT check_care_task_due_date_after_created
  CHECK (due_date >= created_at::date);

-- =============================================================================
-- PART 16: User Model Constraints
-- =============================================================================

ALTER TABLE users
  ADD CONSTRAINT check_user_email_format
  CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE users
  ADD CONSTRAINT check_user_restricted_crop_count_non_negative
  CHECK (restricted_crop_count >= 0);

ALTER TABLE users
  ADD CONSTRAINT check_user_latitude_range
  CHECK (latitude IS NULL OR (latitude >= -90 AND latitude <= 90));

ALTER TABLE users
  ADD CONSTRAINT check_user_longitude_range
  CHECK (longitude IS NULL OR (longitude >= -180 AND longitude <= 180));

-- Conditional: if restricted_crop_flag=true, first_violation must be set
ALTER TABLE users
  ADD CONSTRAINT check_user_first_violation_required_if_flagged
  CHECK (NOT restricted_crop_flag OR restricted_crop_first_violation IS NOT NULL);

-- =============================================================================
-- COMMENTS ON CONSTRAINTS
-- =============================================================================

COMMENT ON CONSTRAINT check_garden_ec_range ON gardens
  IS 'Ensures EC (electrical conductivity) values are within valid hydroponic range (0-10 mS/cm)';

COMMENT ON CONSTRAINT check_garden_ph_range ON gardens
  IS 'Ensures pH values are within valid range (0-14)';

COMMENT ON CONSTRAINT check_hydro_system_type_required ON gardens
  IS 'Business rule: Hydroponic gardens must specify a system type';

COMMENT ON CONSTRAINT check_user_email_format ON users
  IS 'Validates email address format using regex pattern';

COMMENT ON CONSTRAINT check_germination_event_date_required_if_germinated ON germination_events
  IS 'Business rule: If seeds have germinated, the germination date must be recorded';

COMMENT ON CONSTRAINT check_planting_event_visual_placement_complete ON planting_events
  IS 'Business rule: Visual placement coordinates must all be set together or all be null';

-- =============================================================================
-- VERIFICATION QUERIES (for manual testing)
-- =============================================================================

-- Uncomment to list all CHECK constraints:
-- SELECT conname, conrelid::regclass AS table_name, pg_get_constraintdef(oid) AS definition
-- FROM pg_constraint
-- WHERE contype = 'c'
-- AND connamespace = 'public'::regnamespace
-- ORDER BY conrelid::regclass::text, conname;

-- Uncomment to count constraints by table:
-- SELECT conrelid::regclass AS table_name, COUNT(*) AS constraint_count
-- FROM pg_constraint
-- WHERE contype = 'c'
-- AND connamespace = 'public'::regnamespace
-- GROUP BY conrelid
-- ORDER BY constraint_count DESC;

-- =============================================================================
-- END OF MIGRATION
-- =============================================================================
