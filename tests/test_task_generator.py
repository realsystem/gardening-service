"""Unit tests for TaskGenerator orchestrator"""
import pytest
from datetime import date
from unittest.mock import Mock, patch

from app.rules.task_generator import TaskGenerator
from app.models.care_task import TaskType


class TestTaskGenerator:
    """Test TaskGenerator orchestration of rules"""

    def test_generate_tasks_for_planting(self, test_db, sample_plant_variety):
        """Test that TaskGenerator applies planting rules and creates tasks"""
        # Create mock planting event
        planting_event = Mock()
        planting_event.id = 1
        planting_event.plant_variety_id = sample_plant_variety.id
        planting_event.planting_date = date(2024, 5, 15)
        planting_event.location_in_garden = "Bed 1"

        # Generate tasks
        generator = TaskGenerator()
        tasks = generator.generate_tasks_for_planting(test_db, planting_event, user_id=1)

        # Should create both harvest and watering tasks
        # - 1 harvest task
        # - 4 watering tasks (HIGH water requirement, TASKS_AHEAD=4)
        assert len(tasks) == 5

        # Verify task types
        task_types = [task.task_type for task in tasks]
        assert TaskType.HARVEST in task_types
        assert task_types.count(TaskType.WATER) == 4

        # Verify all tasks are persisted
        for task in tasks:
            assert task.id is not None
            assert task.user_id == 1
            assert task.planting_event_id == 1

    def test_generate_tasks_for_seed_batch(self, test_db, sample_plant_variety):
        """Test that TaskGenerator applies seed batch rules"""
        current_year = date.today().year
        old_harvest_year = current_year - 4  # 4 years old

        # Create mock seed batch
        seed_batch = Mock()
        seed_batch.id = 1
        seed_batch.plant_variety_id = sample_plant_variety.id
        seed_batch.harvest_year = old_harvest_year

        # Generate tasks
        generator = TaskGenerator()
        tasks = generator.generate_tasks_for_seed_batch(test_db, seed_batch, user_id=1)

        # Should create viability warning task
        assert len(tasks) == 1
        task = tasks[0]
        assert task.task_type == TaskType.OTHER
        assert "viability" in task.title.lower()
        assert task.user_id == 1

    def test_generate_tasks_for_fresh_seed_batch(self, test_db, sample_plant_variety):
        """Test that no tasks are generated for fresh seeds"""
        current_year = date.today().year
        fresh_harvest_year = current_year - 1  # 1 year old

        seed_batch = Mock()
        seed_batch.id = 1
        seed_batch.plant_variety_id = sample_plant_variety.id
        seed_batch.harvest_year = fresh_harvest_year

        generator = TaskGenerator()
        tasks = generator.generate_tasks_for_seed_batch(test_db, seed_batch, user_id=1)

        # No tasks should be generated for fresh seeds
        assert len(tasks) == 0

    def test_planting_without_water_requirement(self, test_db, sample_plant_variety):
        """Test task generation when plant has no water requirement"""
        # Remove water requirement
        sample_plant_variety.water_requirement = None
        test_db.commit()

        planting_event = Mock()
        planting_event.id = 1
        planting_event.plant_variety_id = sample_plant_variety.id
        planting_event.planting_date = date(2024, 5, 15)
        planting_event.location_in_garden = "Bed 1"

        generator = TaskGenerator()
        tasks = generator.generate_tasks_for_planting(test_db, planting_event, user_id=1)

        # Should only create harvest task, no watering tasks
        assert len(tasks) == 1
        assert tasks[0].task_type == TaskType.HARVEST

    def test_planting_without_days_to_harvest(self, test_db, sample_plant_variety):
        """Test task generation when plant has no days_to_harvest"""
        # Remove days_to_harvest
        sample_plant_variety.days_to_harvest = None
        test_db.commit()

        planting_event = Mock()
        planting_event.id = 1
        planting_event.plant_variety_id = sample_plant_variety.id
        planting_event.planting_date = date(2024, 5, 15)
        planting_event.location_in_garden = "Bed 1"

        generator = TaskGenerator()
        tasks = generator.generate_tasks_for_planting(test_db, planting_event, user_id=1)

        # Should only create watering tasks, no harvest task
        assert len(tasks) == 4
        assert all(task.task_type == TaskType.WATER for task in tasks)
