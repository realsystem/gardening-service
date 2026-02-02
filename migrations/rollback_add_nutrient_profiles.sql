-- Rollback nutrient profile fields from plant_varieties table
-- Reverses: add_nutrient_profiles.sql
-- WARNING: This will permanently delete all nutrient profile data

ALTER TABLE plant_varieties
  DROP COLUMN IF EXISTS seedling_ec_min,
  DROP COLUMN IF EXISTS seedling_ec_max,
  DROP COLUMN IF EXISTS vegetative_ec_min,
  DROP COLUMN IF EXISTS vegetative_ec_max,
  DROP COLUMN IF EXISTS flowering_ec_min,
  DROP COLUMN IF EXISTS flowering_ec_max,
  DROP COLUMN IF EXISTS fruiting_ec_min,
  DROP COLUMN IF EXISTS fruiting_ec_max,
  DROP COLUMN IF EXISTS optimal_ph_min,
  DROP COLUMN IF EXISTS optimal_ph_max,
  DROP COLUMN IF EXISTS solution_change_days_min,
  DROP COLUMN IF EXISTS solution_change_days_max;
