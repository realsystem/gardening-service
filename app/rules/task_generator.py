"""Main task generator orchestrator"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.rules.base_rule import BaseRule
from app.rules.rules import HarvestRule, WateringRule, SeedViabilityRule
from app.repositories.care_task_repository import CareTaskRepository
from app.models.care_task import CareTask


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

        return self._apply_rules_and_create_tasks(db, context, [HarvestRule(), WateringRule()])

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
        """
        task_repo = CareTaskRepository(db)
        created_tasks = []

        for rule in rules:
            task_dicts = rule.generate_tasks(db, context)

            for task_dict in task_dicts:
                # Create task in database
                task = task_repo.create(**task_dict)
                created_tasks.append(task)

        return created_tasks
