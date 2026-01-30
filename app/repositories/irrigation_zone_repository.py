"""Repository for irrigation zone data access"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.irrigation_zone import IrrigationZone
from app.models.garden import Garden
from app.schemas.irrigation_zone import IrrigationZoneCreate, IrrigationZoneUpdate


class IrrigationZoneRepository:
    """Repository for managing irrigation zones"""

    @staticmethod
    def create(db: Session, user_id: int, zone_data: IrrigationZoneCreate) -> IrrigationZone:
        """Create a new irrigation zone"""
        db_zone = IrrigationZone(
            user_id=user_id,
            **zone_data.model_dump()
        )
        db.add(db_zone)
        db.commit()
        db.refresh(db_zone)
        return db_zone

    @staticmethod
    def get_by_id(db: Session, zone_id: int, user_id: int) -> Optional[IrrigationZone]:
        """Get irrigation zone by ID (with user ownership check)"""
        return db.query(IrrigationZone).filter(
            IrrigationZone.id == zone_id,
            IrrigationZone.user_id == user_id
        ).first()

    @staticmethod
    def get_all(db: Session, user_id: int) -> List[IrrigationZone]:
        """Get all irrigation zones for a user"""
        return db.query(IrrigationZone).filter(
            IrrigationZone.user_id == user_id
        ).order_by(IrrigationZone.name).all()

    @staticmethod
    def get_with_garden_count(db: Session, user_id: int) -> List[tuple]:
        """Get all zones with count of gardens assigned to each"""
        return db.query(
            IrrigationZone,
            func.count(Garden.id).label('garden_count')
        ).outerjoin(
            Garden, Garden.irrigation_zone_id == IrrigationZone.id
        ).filter(
            IrrigationZone.user_id == user_id
        ).group_by(IrrigationZone.id).order_by(IrrigationZone.name).all()

    @staticmethod
    def update(db: Session, zone_id: int, user_id: int, zone_data: IrrigationZoneUpdate) -> Optional[IrrigationZone]:
        """Update an irrigation zone"""
        db_zone = IrrigationZoneRepository.get_by_id(db, zone_id, user_id)
        if not db_zone:
            return None

        update_data = zone_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_zone, field, value)

        db.commit()
        db.refresh(db_zone)
        return db_zone

    @staticmethod
    def delete(db: Session, zone_id: int, user_id: int) -> bool:
        """Delete an irrigation zone (gardens will have zone_id set to NULL)"""
        db_zone = IrrigationZoneRepository.get_by_id(db, zone_id, user_id)
        if not db_zone:
            return False

        db.delete(db_zone)
        db.commit()
        return True

    @staticmethod
    def get_gardens_in_zone(db: Session, zone_id: int, user_id: int) -> List[Garden]:
        """Get all gardens assigned to a specific zone"""
        return db.query(Garden).filter(
            Garden.irrigation_zone_id == zone_id,
            Garden.user_id == user_id
        ).all()
