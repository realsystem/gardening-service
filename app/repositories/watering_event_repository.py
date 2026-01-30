"""Repository for watering event data access"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.watering_event import WateringEvent
from app.schemas.watering_event import WateringEventCreate, WateringEventUpdate


class WateringEventRepository:
    """Repository for managing watering events"""

    @staticmethod
    def create(db: Session, user_id: int, event_data: WateringEventCreate) -> WateringEvent:
        """Create a new watering event"""
        db_event = WateringEvent(
            user_id=user_id,
            **event_data.model_dump()
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event

    @staticmethod
    def get_by_id(db: Session, event_id: int, user_id: int) -> Optional[WateringEvent]:
        """Get watering event by ID (with user ownership check)"""
        return db.query(WateringEvent).filter(
            WateringEvent.id == event_id,
            WateringEvent.user_id == user_id
        ).first()

    @staticmethod
    def get_all(db: Session, user_id: int, limit: int = 100) -> List[WateringEvent]:
        """Get recent watering events for a user"""
        return db.query(WateringEvent).filter(
            WateringEvent.user_id == user_id
        ).order_by(desc(WateringEvent.watered_at)).limit(limit).all()

    @staticmethod
    def get_by_zone(db: Session, zone_id: int, user_id: int, days: int = 30) -> List[WateringEvent]:
        """Get watering events for a specific zone within date range"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return db.query(WateringEvent).filter(
            WateringEvent.irrigation_zone_id == zone_id,
            WateringEvent.user_id == user_id,
            WateringEvent.watered_at >= cutoff_date
        ).order_by(desc(WateringEvent.watered_at)).all()

    @staticmethod
    def get_latest_by_zone(db: Session, zone_id: int, user_id: int) -> Optional[WateringEvent]:
        """Get the most recent watering event for a zone"""
        return db.query(WateringEvent).filter(
            WateringEvent.irrigation_zone_id == zone_id,
            WateringEvent.user_id == user_id
        ).order_by(desc(WateringEvent.watered_at)).first()

    @staticmethod
    def get_by_date_range(
        db: Session,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        zone_id: Optional[int] = None
    ) -> List[WateringEvent]:
        """Get watering events within a date range, optionally filtered by zone"""
        query = db.query(WateringEvent).filter(
            WateringEvent.user_id == user_id,
            WateringEvent.watered_at >= start_date,
            WateringEvent.watered_at <= end_date
        )

        if zone_id is not None:
            query = query.filter(WateringEvent.irrigation_zone_id == zone_id)

        return query.order_by(desc(WateringEvent.watered_at)).all()

    @staticmethod
    def update(db: Session, event_id: int, user_id: int, event_data: WateringEventUpdate) -> Optional[WateringEvent]:
        """Update a watering event"""
        db_event = WateringEventRepository.get_by_id(db, event_id, user_id)
        if not db_event:
            return None

        update_data = event_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_event, field, value)

        db.commit()
        db.refresh(db_event)
        return db_event

    @staticmethod
    def delete(db: Session, event_id: int, user_id: int) -> bool:
        """Delete a watering event"""
        db_event = WateringEventRepository.get_by_id(db, event_id, user_id)
        if not db_event:
            return False

        db.delete(db_event)
        db.commit()
        return True
