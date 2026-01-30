"""Repository for irrigation source data access"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.irrigation_source import IrrigationSource
from app.schemas.irrigation_source import IrrigationSourceCreate, IrrigationSourceUpdate


class IrrigationSourceRepository:
    """Repository for managing irrigation sources"""

    @staticmethod
    def create(db: Session, user_id: int, source_data: IrrigationSourceCreate) -> IrrigationSource:
        """Create a new irrigation source"""
        db_source = IrrigationSource(
            user_id=user_id,
            **source_data.model_dump()
        )
        db.add(db_source)
        db.commit()
        db.refresh(db_source)
        return db_source

    @staticmethod
    def get_by_id(db: Session, source_id: int, user_id: int) -> Optional[IrrigationSource]:
        """Get irrigation source by ID (with user ownership check)"""
        return db.query(IrrigationSource).filter(
            IrrigationSource.id == source_id,
            IrrigationSource.user_id == user_id
        ).first()

    @staticmethod
    def get_all(db: Session, user_id: int) -> List[IrrigationSource]:
        """Get all irrigation sources for a user"""
        return db.query(IrrigationSource).filter(
            IrrigationSource.user_id == user_id
        ).order_by(IrrigationSource.name).all()

    @staticmethod
    def update(db: Session, source_id: int, user_id: int, source_data: IrrigationSourceUpdate) -> Optional[IrrigationSource]:
        """Update an irrigation source"""
        db_source = IrrigationSourceRepository.get_by_id(db, source_id, user_id)
        if not db_source:
            return None

        update_data = source_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_source, field, value)

        db.commit()
        db.refresh(db_source)
        return db_source

    @staticmethod
    def delete(db: Session, source_id: int, user_id: int) -> bool:
        """Delete an irrigation source"""
        db_source = IrrigationSourceRepository.get_by_id(db, source_id, user_id)
        if not db_source:
            return False

        db.delete(db_source)
        db.commit()
        return True
