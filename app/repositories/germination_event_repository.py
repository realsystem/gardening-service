"""GerminationEvent repository"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.germination_event import GerminationEvent
from datetime import date


class GerminationEventRepository:
    """Repository for GerminationEvent database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, seed_batch_id: int, plant_variety_id: int,
               started_date: date, **kwargs) -> GerminationEvent:
        """Create a new germination event"""
        event = GerminationEvent(
            user_id=user_id,
            seed_batch_id=seed_batch_id,
            plant_variety_id=plant_variety_id,
            started_date=started_date,
            **kwargs
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_by_id(self, event_id: int) -> Optional[GerminationEvent]:
        """Get germination event by ID"""
        return self.db.query(GerminationEvent).filter(GerminationEvent.id == event_id).first()

    def get_user_events(self, user_id: int) -> List[GerminationEvent]:
        """Get all germination events for a user"""
        return self.db.query(GerminationEvent).filter(GerminationEvent.user_id == user_id).all()

    def update(self, event: GerminationEvent, **kwargs) -> GerminationEvent:
        """Update germination event"""
        for key, value in kwargs.items():
            if hasattr(event, key) and value is not None:
                setattr(event, key, value)
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete(self, event: GerminationEvent) -> None:
        """Delete germination event"""
        self.db.delete(event)
        self.db.commit()
