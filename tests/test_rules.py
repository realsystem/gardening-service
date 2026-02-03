"""Unit tests for task generation rules"""
import pytest
from datetime import date, timedelta
from unittest.mock import Mock

from app.rules.rules import HarvestRule, SeedViabilityRule
from app.models.care_task import TaskType, TaskSource
from app.models.plant_variety import WaterRequirement
from app.models.planting_event import PlantingEvent
from app.models.seed_batch import SeedBatch


class TestHarvestRule:
    """Test HarvestRule task generation logic"""

    def test_harvest_rule_generates_task(self, test_db, sample_plant_variety):
        """Test that HarvestRule generates a harvest task with correct date"""
        # Create a planting event
        planting_date = date(2024, 5, 15)
        planting_event = Mock()
        planting_event.id = 1
        planting_event.plant_variety_id = sample_plant_variety.id
        planting_event.planting_date = planting_date

        # Generate tasks
        rule = HarvestRule()
        context = {
            "planting_event": planting_event,
            "user_id": 1,
        }
        tasks = rule.generate_tasks(test_db, context)

        # Verify task was generated
        assert len(tasks) == 1
        task = tasks[0]

        # Verify task properties
        assert task["task_type"] == TaskType.HARVEST
        assert task["user_id"] == 1
        assert task["planting_event_id"] == 1
        assert task["task_source"] == TaskSource.AUTO_GENERATED
        assert "Harvest Tomato" in task["title"]

        # Verify harvest date calculation (planting_date + days_to_harvest)
        expected_harvest_date = planting_date + timedelta(days=80)
        assert task["due_date"] == expected_harvest_date

    def test_harvest_rule_no_task_without_days_to_harvest(self, test_db, sample_plant_variety):
        """Test that no task is generated if plant has no days_to_harvest"""
        # Modify variety to have no days_to_harvest
        sample_plant_variety.days_to_harvest = None
        test_db.commit()

        planting_event = Mock()
        planting_event.id = 1
        planting_event.plant_variety_id = sample_plant_variety.id
        planting_event.planting_date = date(2024, 5, 15)

        rule = HarvestRule()
        context = {
            "planting_event": planting_event,
            "user_id": 1,
        }
        tasks = rule.generate_tasks(test_db, context)

        # No task should be generated
        assert len(tasks) == 0


class TestSeedViabilityRule:
    """Test SeedViabilityRule task generation logic"""

    def test_seed_viability_warning_for_old_seeds(self, test_db, sample_plant_variety):
        """Test that warning is generated for seeds >= 3 years old"""
        current_year = date.today().year
        old_harvest_year = current_year - 3  # Exactly 3 years old

        seed_batch = Mock()
        seed_batch.id = 1
        seed_batch.plant_variety_id = sample_plant_variety.id
        seed_batch.harvest_year = old_harvest_year

        rule = SeedViabilityRule()
        context = {
            "seed_batch": seed_batch,
            "user_id": 1,
        }
        tasks = rule.generate_tasks(test_db, context)

        # Should generate warning task
        assert len(tasks) == 1
        task = tasks[0]
        assert task["task_type"] == TaskType.OTHER
        assert "viability" in task["title"].lower()
        assert str(old_harvest_year) in task["description"]
        assert task["due_date"] == date.today()

    def test_no_warning_for_fresh_seeds(self, test_db, sample_plant_variety):
        """Test that no warning is generated for seeds < 3 years old"""
        current_year = date.today().year
        fresh_harvest_year = current_year - 1  # 1 year old

        seed_batch = Mock()
        seed_batch.id = 1
        seed_batch.plant_variety_id = sample_plant_variety.id
        seed_batch.harvest_year = fresh_harvest_year

        rule = SeedViabilityRule()
        context = {
            "seed_batch": seed_batch,
            "user_id": 1,
        }
        tasks = rule.generate_tasks(test_db, context)

        # No task should be generated
        assert len(tasks) == 0

    def test_no_warning_without_harvest_year(self, test_db, sample_plant_variety):
        """Test that no warning is generated if harvest year is not set"""
        seed_batch = Mock()
        seed_batch.id = 1
        seed_batch.plant_variety_id = sample_plant_variety.id
        seed_batch.harvest_year = None

        rule = SeedViabilityRule()
        context = {
            "seed_batch": seed_batch,
            "user_id": 1,
        }
        tasks = rule.generate_tasks(test_db, context)

        # No task should be generated
        assert len(tasks) == 0
