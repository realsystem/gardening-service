-- Migration: Fix enum case mismatch between database and application code
-- Date: 2026-01-29
-- Issue: Database enums were created with uppercase values but Python code uses lowercase
--
-- This migration fixes the following enums to match the Python code:
-- - taskstatus: PENDING -> pending, COMPLETED -> completed, SKIPPED -> skipped
-- - plantingmethod: DIRECT_SOW -> direct_sow, TRANSPLANT -> transplant
-- - sunrequirement: FULL_SUN -> full_sun, etc.
-- - tasksource: AUTO_GENERATED -> auto_generated, MANUAL -> manual
-- - waterrequirement: LOW -> low, MEDIUM -> medium, HIGH -> high
-- - tasktype: WATER -> water, etc.

-- Fix TaskStatus enum
ALTER TYPE taskstatus RENAME TO taskstatus_old;
CREATE TYPE taskstatus AS ENUM ('pending', 'completed', 'skipped');
ALTER TABLE care_tasks ALTER COLUMN status TYPE taskstatus USING status::text::taskstatus;
DROP TYPE taskstatus_old;

-- Fix PlantingMethod enum
ALTER TYPE plantingmethod RENAME TO plantingmethod_old;
CREATE TYPE plantingmethod AS ENUM ('direct_sow', 'transplant');
ALTER TABLE planting_events ALTER COLUMN planting_method TYPE plantingmethod USING lower(planting_method::text)::plantingmethod;
DROP TYPE plantingmethod_old;

-- Fix SunRequirement enum
ALTER TYPE sunrequirement RENAME TO sunrequirement_old;
CREATE TYPE sunrequirement AS ENUM ('full_sun', 'partial_sun', 'partial_shade', 'full_shade');
ALTER TABLE plant_varieties ALTER COLUMN sun_requirement TYPE sunrequirement USING lower(sun_requirement::text)::sunrequirement;
DROP TYPE sunrequirement_old;

-- Fix TaskSource enum
ALTER TYPE tasksource RENAME TO tasksource_old;
CREATE TYPE tasksource AS ENUM ('auto_generated', 'manual');
ALTER TABLE care_tasks ALTER COLUMN task_source TYPE tasksource USING lower(task_source::text)::tasksource;
DROP TYPE tasksource_old;

-- Fix WaterRequirement enum
ALTER TYPE waterrequirement RENAME TO waterrequirement_old;
CREATE TYPE waterrequirement AS ENUM ('low', 'medium', 'high');
ALTER TABLE plant_varieties ALTER COLUMN water_requirement TYPE waterrequirement USING lower(water_requirement::text)::waterrequirement;
DROP TYPE waterrequirement_old;

-- Fix TaskType enum (complex - has mixed case already in database)
ALTER TYPE tasktype RENAME TO tasktype_old;
CREATE TYPE tasktype AS ENUM (
    'water', 'fertilize', 'prune', 'mulch', 'weed', 'pest_control', 'harvest', 'other',
    'adjust_lighting', 'adjust_temperature', 'adjust_humidity', 'nutrient_solution', 'train_plant',
    'check_nutrient_solution', 'adjust_ph', 'replace_nutrient_solution', 'clean_reservoir', 'adjust_water_circulation'
);
ALTER TABLE care_tasks ALTER COLUMN task_type TYPE tasktype USING lower(task_type::text)::tasktype;
DROP TYPE tasktype_old;

-- Verification: Check all enums are now lowercase
\echo 'Verifying enum values are now lowercase...'
\dT+ taskstatus
\dT+ plantingmethod
\dT+ sunrequirement
\dT+ tasksource
\dT+ waterrequirement
\dT+ tasktype
