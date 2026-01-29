"""PlantingEvent repository"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.planting_event import PlantingEvent, PlantingMethod
from datetime import date


class PlantingEventRepository:
    """Repository for PlantingEvent database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, garden_id: int, plant_variety_id: int,
               planting_date: date, planting_method: PlantingMethod, **kwargs) -> PlantingEvent:
        """Create a new planting event"""
        event = PlantingEvent(
            user_id=user_id,
            garden_id=garden_id,
            plant_variety_id=plant_variety_id,
            planting_date=planting_date,
            planting_method=planting_method,
            **kwargs
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_by_id(self, event_id: int) -> Optional[PlantingEvent]:
        """Get planting event by ID"""
        return self.db.query(PlantingEvent).filter(PlantingEvent.id == event_id).first()

    def get_user_events(self, user_id: int) -> List[PlantingEvent]:
        """Get all planting events for a user"""
        return self.db.query(PlantingEvent).filter(PlantingEvent.user_id == user_id).all()

    def get_by_garden(self, garden_id: int) -> List[PlantingEvent]:
        """Get all planting events for a specific garden"""
        return self.db.query(PlantingEvent).filter(PlantingEvent.garden_id == garden_id).all()

    def get_by_date_range(self, user_id: int, start_date: date, end_date: date) -> List[PlantingEvent]:
        """Get planting events within a date range"""
        return self.db.query(PlantingEvent).filter(
            PlantingEvent.user_id == user_id,
            PlantingEvent.planting_date >= start_date,
            PlantingEvent.planting_date <= end_date
        ).all()

    def update(self, event: PlantingEvent, **kwargs) -> PlantingEvent:
        """Update planting event"""
        for key, value in kwargs.items():
            if hasattr(event, key) and value is not None:
                setattr(event, key, value)
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete(self, event: PlantingEvent) -> None:
        """Delete planting event"""
        self.db.delete(event)
        self.db.commit()
