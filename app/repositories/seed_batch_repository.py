"""SeedBatch repository"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.seed_batch import SeedBatch


class SeedBatchRepository:
    """Repository for SeedBatch database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, plant_variety_id: int, **kwargs) -> SeedBatch:
        """Create a new seed batch"""
        batch = SeedBatch(
            user_id=user_id,
            plant_variety_id=plant_variety_id,
            **kwargs
        )
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def get_by_id(self, batch_id: int) -> Optional[SeedBatch]:
        """Get seed batch by ID"""
        return self.db.query(SeedBatch).filter(SeedBatch.id == batch_id).first()

    def get_user_batches(self, user_id: int) -> List[SeedBatch]:
        """Get all seed batches for a user with plant_variety loaded"""
        return (
            self.db.query(SeedBatch)
            .options(joinedload(SeedBatch.plant_variety))
            .filter(SeedBatch.user_id == user_id)
            .all()
        )

    def update(self, batch: SeedBatch, **kwargs) -> SeedBatch:
        """Update seed batch"""
        for key, value in kwargs.items():
            if hasattr(batch, key) and value is not None:
                setattr(batch, key, value)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def delete(self, batch: SeedBatch) -> None:
        """Delete seed batch"""
        self.db.delete(batch)
        self.db.commit()
