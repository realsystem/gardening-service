-- Add Nutrient Optimization Profile Fields to Plant Varieties
-- Date: 2026-02-01
-- Purpose: Support EC/pH optimization for hydroponic and fertigation systems

-- Add nutrient profile fields to plant_varieties table
ALTER TABLE plant_varieties
  ADD COLUMN seedling_ec_min FLOAT,
  ADD COLUMN seedling_ec_max FLOAT,
  ADD COLUMN vegetative_ec_min FLOAT,
  ADD COLUMN vegetative_ec_max FLOAT,
  ADD COLUMN flowering_ec_min FLOAT,
  ADD COLUMN flowering_ec_max FLOAT,
  ADD COLUMN fruiting_ec_min FLOAT,
  ADD COLUMN fruiting_ec_max FLOAT,
  ADD COLUMN optimal_ph_min FLOAT,
  ADD COLUMN optimal_ph_max FLOAT,
  ADD COLUMN solution_change_days_min INTEGER,
  ADD COLUMN solution_change_days_max INTEGER;

-- Add comments for documentation
COMMENT ON COLUMN plant_varieties.seedling_ec_min IS 'Minimum EC (mS/cm) for seedling stage';
COMMENT ON COLUMN plant_varieties.seedling_ec_max IS 'Maximum EC (mS/cm) for seedling stage';
COMMENT ON COLUMN plant_varieties.vegetative_ec_min IS 'Minimum EC (mS/cm) for vegetative stage';
COMMENT ON COLUMN plant_varieties.vegetative_ec_max IS 'Maximum EC (mS/cm) for vegetative stage';
COMMENT ON COLUMN plant_varieties.flowering_ec_min IS 'Minimum EC (mS/cm) for flowering stage';
COMMENT ON COLUMN plant_varieties.flowering_ec_max IS 'Maximum EC (mS/cm) for flowering stage';
COMMENT ON COLUMN plant_varieties.fruiting_ec_min IS 'Minimum EC (mS/cm) for fruiting stage';
COMMENT ON COLUMN plant_varieties.fruiting_ec_max IS 'Maximum EC (mS/cm) for fruiting stage';
COMMENT ON COLUMN plant_varieties.optimal_ph_min IS 'Minimum optimal pH';
COMMENT ON COLUMN plant_varieties.optimal_ph_max IS 'Maximum optimal pH';
COMMENT ON COLUMN plant_varieties.solution_change_days_min IS 'Minimum days between full solution changes';
COMMENT ON COLUMN plant_varieties.solution_change_days_max IS 'Maximum days between full solution changes';