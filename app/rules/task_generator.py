"""Main task generator orchestrator"""
import time
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.rules.base_rule import BaseRule
from app.rules.rules import HarvestRule, WateringRule, SeedViabilityRule
from app.utils.metrics import MetricsCollector
from app.utils.feature_flags import is_rule_engine_enabled

logger = logging.getLogger(__name__)
from app.rules.indoor_rules import (
    LightScheduleRule,
    TemperatureMonitoringRule,
    HumidityMonitoringRule,
    NutrientScheduleRule
)
from app.rules.hydroponics_rules import (
    NutrientCheckRule,
    PHMonitoringRule,
    ECPPMMonitoringRule,
    WaterTemperatureMonitoringRule,
    ReservoirMaintenanceRule,
    NutrientReplacementRule
)
from app.repositories.care_task_repository import CareTaskRepository
from app.models.care_task import CareTask
from app.models.garden import GardenType


class TaskGenerator:
    """
    Orchestrates rule-based task generation.
    Applies all registered rules and creates tasks in the database.
    """

    def __init__(self):
        # Register all rules
        self.rules: List[BaseRule] = [
            HarvestRule(),
            WateringRule(),
            SeedViabilityRule(),
        ]

    def generate_tasks_for_planting(self, db: Session, planting_event, user_id: int) -> List[CareTask]:
        """
        Generate all applicable tasks for a new planting event.

        Args:
            db: Database session
            planting_event: PlantingEvent instance
            user_id: User ID

        Returns:
            List of created CareTask instances
        """
        context = {
            "planting_event": planting_event,
            "user_id": user_id,
        }

        # Determine which rules to apply based on garden type
        rules = [HarvestRule(), WateringRule()]

        # Add indoor-specific rules if this is an indoor garden
        if planting_event.garden and planting_event.garden.garden_type == GardenType.INDOOR:
            rules.extend([
                LightScheduleRule(),
                NutrientScheduleRule()
            ])

            # Add hydroponics-specific rules if this is a hydroponic garden
            if planting_event.garden.is_hydroponic:
                rules.extend([
                    NutrientCheckRule(),
                    ReservoirMaintenanceRule(),
                    NutrientReplacementRule()
                ])

        return self._apply_rules_and_create_tasks(db, context, rules)

    def generate_tasks_for_seed_batch(self, db: Session, seed_batch, user_id: int) -> List[CareTask]:
        """
        Generate viability warning tasks for a seed batch.

        Args:
            db: Database session
            seed_batch: SeedBatch instance
            user_id: User ID

        Returns:
            List of created CareTask instances
        """
        context = {
            "seed_batch": seed_batch,
            "user_id": user_id,
        }

        return self._apply_rules_and_create_tasks(db, context, [SeedViabilityRule()])

    def generate_tasks_for_sensor_reading(self, db: Session, sensor_reading, user_id: int) -> List[CareTask]:
        """
        Generate warning tasks based on sensor readings.

        Args:
            db: Database session
            sensor_reading: SensorReading instance
            user_id: User ID

        Returns:
            List of created CareTask instances
        """
        context = {
            "sensor_reading": sensor_reading,
            "user_id": user_id,
        }

        # Apply indoor monitoring rules
        rules = [TemperatureMonitoringRule(), HumidityMonitoringRule()]

        # Add hydroponics monitoring rules if this is a hydroponic garden
        if sensor_reading.garden and sensor_reading.garden.is_hydroponic:
            rules.extend([
                PHMonitoringRule(),
                ECPPMMonitoringRule(),
                WaterTemperatureMonitoringRule()
            ])

        return self._apply_rules_and_create_tasks(db, context, rules)

    def _apply_rules_and_create_tasks(
        self,
        db: Session,
        context: Dict[str, Any],
        rules: List[BaseRule]
    ) -> List[CareTask]:
        """
        Apply rules and create tasks in database.

        Args:
            db: Database session
            context: Context dictionary
            rules: List of rules to apply

        Returns:
            List of created CareTask instances

        Note:
            If rule engine is disabled via feature flag, returns empty list
            without error. This allows graceful degradation during incidents.
        """
        # Check feature flag - fail safe by returning empty list
        if not is_rule_engine_enabled():
            logger.info(
                "Rule engine disabled via feature flag - skipping task generation",
                extra={'context': context}
            )
            return []

        # Track batch execution time
        batch_start_time = time.time()

        task_repo = CareTaskRepository(db)
        created_tasks = []

        for rule in rules:
            # Track individual rule execution time
            rule_start_time = time.time()
            task_dicts = rule.generate_tasks(db, context)
            rule_duration = time.time() - rule_start_time

            # Determine if rule triggered (generated tasks)
            triggered = len(task_dicts) > 0

            # Track metrics for this rule
            MetricsCollector.track_rule_evaluation(
                rule_id=rule.name,
                triggered=triggered,
                duration=rule_duration,
                severity='info' if triggered else None
            )

            for task_dict in task_dicts:
                # Create task in database
                task = task_repo.create(**task_dict)
                created_tasks.append(task)

        # Track batch execution time
        batch_duration = time.time() - batch_start_time
        MetricsCollector.track_rule_engine_batch(batch_duration)

        return created_tasks
