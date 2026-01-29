"""Base rule interface"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from sqlalchemy.orm import Session


class BaseRule(ABC):
    """
    Base class for all task generation rules.
    Each rule encapsulates a specific piece of gardening logic.
    """

    @abstractmethod
    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate tasks based on the rule logic.

        Args:
            db: Database session
            context: Context dictionary with relevant data (user, planting_event, etc.)

        Returns:
            List of task dictionaries with keys:
                - user_id
                - planting_event_id (optional)
                - task_type
                - title
                - description
                - due_date
                - task_source
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the rule"""
        pass
