"""Unit tests for TaskGenerator orchestrator"""
import pytest
from datetime import date
from unittest.mock import Mock, patch

from app.rules.task_generator import TaskGenerator
from app.models.care_task import TaskType


class TestTaskGenerator:
    """Test TaskGenerator orchestration of rules"""

    def test_generate_tasks_for_planting(self, test_db, sample_user, outdoor_planting_event):
        """Test that TaskGenerator applies planting rules and creates tasks"""
        # Use real planting event from fixture
        planting_event = outdoor_planting_event

        # Generate tasks
        generator = TaskGenerator()
        tasks = generator.generate_tasks_for_planting(test_db, planting_event, user_id=sample_user.id)

        # Should create only harvest task (watering removed)
        assert len(tasks) == 1

        # Verify task type
        assert tasks[0].task_type == TaskType.HARVEST

        # Verify all tasks are persisted
        for task in tasks:
            assert task.id is not None
            assert task.user_id == sample_user.id
            assert task.planting_event_id == planting_event.id

    def test_generate_tasks_for_seed_batch(self, test_db, sample_user, sample_plant_variety):
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
        tasks = generator.generate_tasks_for_seed_batch(test_db, seed_batch, user_id=sample_user.id)

        # Should create viability warning task
        assert len(tasks) == 1
        task = tasks[0]
        assert task.task_type == TaskType.OTHER
        assert "viability" in task.title.lower()
        assert task.user_id == sample_user.id

    def test_generate_tasks_for_fresh_seed_batch(self, test_db, sample_user, sample_plant_variety):
        """Test that no tasks are generated for fresh seeds"""
        current_year = date.today().year
        fresh_harvest_year = current_year - 1  # 1 year old

        seed_batch = Mock()
        seed_batch.id = 1
        seed_batch.plant_variety_id = sample_plant_variety.id
        seed_batch.harvest_year = fresh_harvest_year

        generator = TaskGenerator()
        tasks = generator.generate_tasks_for_seed_batch(test_db, seed_batch, user_id=sample_user.id)

        # No tasks should be generated for fresh seeds
        assert len(tasks) == 0

    def test_planting_without_water_requirement(self, test_db, sample_user, outdoor_planting_event):
        """Test task generation when plant has no water requirement - watering removed from system"""
        # Use real planting event from fixture
        planting_event = outdoor_planting_event

        # Remove water requirement from the variety
        planting_event.plant_variety.water_requirement = None
        test_db.commit()

        generator = TaskGenerator()
        tasks = generator.generate_tasks_for_planting(test_db, planting_event, user_id=sample_user.id)

        # Should only create harvest task (watering event tracking removed)
        assert len(tasks) == 1
        assert tasks[0].task_type == TaskType.HARVEST

    def test_planting_without_days_to_harvest(self, test_db, sample_user, outdoor_planting_event):
        """Test task generation when plant has no days_to_harvest"""
        # Use real planting event from fixture
        planting_event = outdoor_planting_event

        # Remove days_to_harvest from the variety
        planting_event.plant_variety.days_to_harvest = None
        test_db.commit()

        generator = TaskGenerator()
        tasks = generator.generate_tasks_for_planting(test_db, planting_event, user_id=sample_user.id)

        # Should create no tasks (no harvest, watering event tracking removed)
        assert len(tasks) == 0
