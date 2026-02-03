-- Clean up watering event tracking feature
-- This script removes all WATER and ADJUST_WATER_CIRCULATION tasks from the database
-- Run this after removing the watering event tracking code

-- Delete all WATER tasks
DELETE FROM care_tasks WHERE task_type = 'water';

-- Delete all ADJUST_WATER_CIRCULATION tasks
DELETE FROM care_tasks WHERE task_type = 'adjust_water_circulation';

-- Verify deletion
SELECT task_type, COUNT(*) as count
FROM care_tasks
GROUP BY task_type
ORDER BY task_type;
