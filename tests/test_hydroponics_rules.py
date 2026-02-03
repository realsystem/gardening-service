"""Tests for hydroponics-specific rules"""
import pytest
from datetime import date, timedelta
from unittest.mock import Mock

from app.rules.hydroponics_rules import (
    NutrientCheckRule,
    # PHMonitoringRule,  # Removed in Phase 6 - requires sensor readings
    # ECPPMMonitoringRule,  # Removed in Phase 6 - requires sensor readings
    # WaterTemperatureMonitoringRule,  # Removed in Phase 6 - requires sensor readings
    ReservoirMaintenanceRule,
    NutrientReplacementRule
)
from app.models.care_task import TaskType, TaskPriority


class TestNutrientCheckRule:
    """Test nutrient check rule"""

    def test_nutrient_check_for_hydroponic_planting(self, test_db, sample_user, hydroponic_planting_event):
        """Test that nutrient check tasks are generated for hydroponic gardens"""
        rule = NutrientCheckRule()
        context = {
            "planting_event": hydroponic_planting_event,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        # Should generate daily checks for first 14 days + 1 recurring task
        assert len(tasks) == 15  # 14 daily + 1 recurring

        # Check daily tasks
        daily_tasks = [t for t in tasks if not t["is_recurring"]]
        assert len(daily_tasks) == 14
        assert all(t["task_type"] == TaskType.CHECK_NUTRIENT_SOLUTION for t in daily_tasks)
        assert all(t["priority"] == TaskPriority.MEDIUM for t in daily_tasks)

        # Check recurring task
        recurring_tasks = [t for t in tasks if t["is_recurring"]]
        assert len(recurring_tasks) == 1
        assert recurring_tasks[0]["recurrence_frequency"] == "daily"

    def test_nutrient_check_not_for_outdoor_garden(self, test_db, sample_user, outdoor_planting_event):
        """Test that nutrient check tasks are NOT generated for outdoor gardens"""
        rule = NutrientCheckRule()
        context = {
            "planting_event": outdoor_planting_event,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        assert len(tasks) == 0

    def test_nutrient_check_not_for_indoor_non_hydro_garden(self, test_db, sample_user, indoor_planting_event):
        """Test that nutrient check tasks are NOT generated for indoor non-hydroponic gardens"""
        rule = NutrientCheckRule()
        context = {
            "planting_event": indoor_planting_event,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        assert len(tasks) == 0


# TestPHMonitoringRule removed - PHMonitoringRule requires SensorReading model (removed in Phase 6)


# TestECPPMMonitoringRule removed - ECPPMMonitoringRule requires SensorReading model (removed in Phase 6)


# TestWaterTemperatureMonitoringRule removed - WaterTemperatureMonitoringRule requires SensorReading model (removed in Phase 6)


class TestReservoirMaintenanceRule:
    """Test reservoir maintenance rule"""

    def test_reservoir_maintenance_scheduling(self, test_db, sample_user, hydroponic_planting_event):
        """Test that biweekly reservoir maintenance tasks are scheduled"""
        rule = ReservoirMaintenanceRule()
        context = {
            "planting_event": hydroponic_planting_event,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        assert len(tasks) == 1
        task = tasks[0]
        assert task["task_type"] == TaskType.CLEAN_RESERVOIR
        assert task["priority"] == TaskPriority.MEDIUM
        assert task["is_recurring"] is True
        assert task["recurrence_frequency"] == "biweekly"
        # First maintenance should be 14 days after planting
        expected_date = hydroponic_planting_event.planting_date + timedelta(days=14)
        assert task["due_date"] == expected_date

    def test_reservoir_maintenance_not_for_outdoor_garden(self, test_db, sample_user, outdoor_planting_event):
        """Test that reservoir maintenance is not scheduled for outdoor gardens"""
        rule = ReservoirMaintenanceRule()
        context = {
            "planting_event": outdoor_planting_event,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        assert len(tasks) == 0


class TestNutrientReplacementRule:
    """Test nutrient replacement rule"""

    def test_nutrient_replacement_scheduling(self, test_db, sample_user, hydroponic_planting_event):
        """Test that weekly nutrient replacement tasks are scheduled"""
        rule = NutrientReplacementRule()
        context = {
            "planting_event": hydroponic_planting_event,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        assert len(tasks) == 1
        task = tasks[0]
        assert task["task_type"] == TaskType.REPLACE_NUTRIENT_SOLUTION
        assert task["priority"] == TaskPriority.MEDIUM
        assert task["is_recurring"] is True
        assert task["recurrence_frequency"] == "weekly"
        # First replacement should be 7 days after planting
        expected_date = hydroponic_planting_event.planting_date + timedelta(days=7)
        assert task["due_date"] == expected_date

    def test_nutrient_replacement_includes_reservoir_info(self, test_db, sample_user, hydroponic_planting_event):
        """Test that nutrient replacement task includes reservoir size info"""
        rule = NutrientReplacementRule()
        context = {
            "planting_event": hydroponic_planting_event,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        task = tasks[0]
        # Should include reservoir size in description
        assert "100.0L" in task["description"] or "100L" in task["description"]

    def test_nutrient_replacement_not_for_outdoor_garden(self, test_db, sample_user, outdoor_planting_event):
        """Test that nutrient replacement is not scheduled for outdoor gardens"""
        rule = NutrientReplacementRule()
        context = {
            "planting_event": outdoor_planting_event,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        assert len(tasks) == 0


class TestHydroponicsIntegration:
    """Integration tests for hydroponics rules with task generator"""

    def test_complete_hydroponic_planting_workflow(self, test_db, sample_user, hydroponic_garden, lettuce_variety):
        """Test complete workflow: planting event creates all appropriate hydroponic tasks"""
        from app.models.planting_event import PlantingEvent, PlantingMethod, PlantHealth
        from app.rules.task_generator import TaskGenerator

        # Create a new planting event
        planting_event = PlantingEvent(
            user_id=sample_user.id,
            garden_id=hydroponic_garden.id,
            plant_variety_id=lettuce_variety.id,
            planting_date=date.today(),
            planting_method=PlantingMethod.TRANSPLANT,
            plant_count=30,
            location_in_garden="Channel 2",
            health_status=PlantHealth.HEALTHY
        )
        test_db.add(planting_event)
        test_db.commit()
        test_db.refresh(planting_event)

        # Generate tasks
        generator = TaskGenerator()
        tasks = generator.generate_tasks_for_planting(test_db, planting_event, user_id=sample_user.id)

        # Should create:
        # - Harvest task (1)
        # - Watering tasks (4)
        # - Nutrient check tasks (14 daily + 1 recurring = 15)
        # - Reservoir maintenance (1)
        # - Nutrient replacement (1)
        # Total: 1 + 4 + 15 + 1 + 1 = 22 tasks

        assert len(tasks) >= 20  # At least these tasks

        # Verify task types
        task_types = [task.task_type for task in tasks]
        assert TaskType.CHECK_NUTRIENT_SOLUTION in task_types
        assert TaskType.CLEAN_RESERVOIR in task_types
        assert TaskType.REPLACE_NUTRIENT_SOLUTION in task_types
