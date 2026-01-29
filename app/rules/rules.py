"""
Concrete task generation rules.

Timezone assumption: Task due dates are stored as date (not datetime).
All date calculations are timezone-agnostic as they represent calendar dates.
Users interpret dates in their local timezone at presentation layer.
"""
from typing import List, Dict, Any
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.rules.base_rule import BaseRule
from app.models.care_task import TaskType, TaskSource, TaskPriority
from app.models.plant_variety import WaterRequirement
from app.models.planting_event import PlantHealth
from app.repositories.plant_variety_repository import PlantVarietyRepository


class HarvestRule(BaseRule):
    """
    Generates harvest task based on planting date + days to harvest.

    Formula: harvest_date = planting_date + typical_days_to_harvest
    """

    @property
    def name(self) -> str:
        return "Harvest Task Generator"

    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate harvest task for a planting event.

        Required context:
            - planting_event: PlantingEvent instance
            - user_id: int
        """
        planting_event = context.get("planting_event")
        user_id = context.get("user_id")

        if not planting_event or not user_id:
            return []

        # Get plant variety to check days_to_harvest
        variety_repo = PlantVarietyRepository(db)
        variety = variety_repo.get_by_id(planting_event.plant_variety_id)

        if not variety or not variety.days_to_harvest:
            return []

        # Calculate harvest date
        harvest_date = planting_event.planting_date + timedelta(days=variety.days_to_harvest)

        # Generate harvest task
        task = {
            "user_id": user_id,
            "planting_event_id": planting_event.id,
            "task_type": TaskType.HARVEST,
            "title": f"Harvest {variety.common_name}",
            "description": (
                f"Expected harvest date for {variety.common_name} "
                f"planted on {planting_event.planting_date}. "
                f"Based on typical {variety.days_to_harvest} days to harvest."
            ),
            "due_date": harvest_date,
            "priority": TaskPriority.HIGH,
            "task_source": TaskSource.AUTO_GENERATED,
        }

        return [task]


class WateringRule(BaseRule):
    """
    Generates watering tasks based on plant water requirements.

    Schedule:
        - HIGH: Every 2 days
        - MEDIUM: Every 4 days
        - LOW: Every 7 days
    """

    # Watering frequency in days
    WATERING_SCHEDULE = {
        WaterRequirement.HIGH: 2,
        WaterRequirement.MEDIUM: 4,
        WaterRequirement.LOW: 7,
    }

    # Number of watering tasks to generate ahead
    TASKS_AHEAD = 4

    @property
    def name(self) -> str:
        return "Watering Task Generator"

    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate watering tasks for a planting event.

        Required context:
            - planting_event: PlantingEvent instance
            - user_id: int
        """
        planting_event = context.get("planting_event")
        user_id = context.get("user_id")

        if not planting_event or not user_id:
            return []

        # Get plant variety to check water requirements
        variety_repo = PlantVarietyRepository(db)
        variety = variety_repo.get_by_id(planting_event.plant_variety_id)

        if not variety or not variety.water_requirement:
            return []

        # Get watering frequency
        frequency_days = self.WATERING_SCHEDULE.get(variety.water_requirement)
        if not frequency_days:
            return []

        # Determine priority based on plant health
        priority = TaskPriority.MEDIUM
        if planting_event.health_status in [PlantHealth.DISEASED, PlantHealth.STRESSED]:
            priority = TaskPriority.HIGH

        # Generate watering tasks
        tasks = []
        base_date = planting_event.planting_date

        for i in range(1, self.TASKS_AHEAD + 1):
            water_date = base_date + timedelta(days=frequency_days * i)

            task = {
                "user_id": user_id,
                "planting_event_id": planting_event.id,
                "task_type": TaskType.WATER,
                "title": f"Water {variety.common_name}",
                "description": (
                    f"Water {variety.common_name} in {planting_event.location_in_garden or 'garden'}. "
                    f"Water requirement: {variety.water_requirement.value}"
                ),
                "due_date": water_date,
                "priority": priority,
                "task_source": TaskSource.AUTO_GENERATED,
            }
            tasks.append(task)

        return tasks


class SeedViabilityRule(BaseRule):
    """
    Generates warning tasks for seeds past their viability period.

    Typical seed viability:
        - Most vegetables: 2-3 years
        - For MVP, we'll use 3 years as threshold
    """

    VIABILITY_YEARS = 3

    @property
    def name(self) -> str:
        return "Seed Viability Checker"

    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate warning task if seed batch is past viability.

        Required context:
            - seed_batch: SeedBatch instance
            - user_id: int
        """
        seed_batch = context.get("seed_batch")
        user_id = context.get("user_id")

        if not seed_batch or not user_id:
            return []

        # Check if harvest year is set
        if not seed_batch.harvest_year:
            return []

        # Get plant variety for name
        variety_repo = PlantVarietyRepository(db)
        variety = variety_repo.get_by_id(seed_batch.plant_variety_id)
        if not variety:
            return []

        # Calculate age of seeds
        current_year = date.today().year
        seed_age = current_year - seed_batch.harvest_year

        # Generate warning if seeds are old
        if seed_age >= self.VIABILITY_YEARS:
            task = {
                "user_id": user_id,
                "planting_event_id": None,
                "task_type": TaskType.OTHER,
                "title": f"Check viability: {variety.common_name} seeds",
                "description": (
                    f"Seed batch from {seed_batch.harvest_year} is {seed_age} years old. "
                    f"Seeds may have reduced germination rate. Consider germination test "
                    f"or purchasing fresh seeds."
                ),
                "due_date": date.today(),
                "priority": TaskPriority.LOW,
                "task_source": TaskSource.AUTO_GENERATED,
            }
            return [task]

        return []
