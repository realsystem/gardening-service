"""PlantVariety repository"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.plant_variety import PlantVariety


class PlantVarietyRepository:
    """Repository for PlantVariety database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, variety_id: int) -> Optional[PlantVariety]:
        """Get plant variety by ID"""
        return self.db.query(PlantVariety).filter(PlantVariety.id == variety_id).first()

    def get_all(self) -> List[PlantVariety]:
        """Get all plant varieties"""
        return self.db.query(PlantVariety).all()

    def search_by_name(self, name: str) -> List[PlantVariety]:
        """Search plant varieties by common name"""
        return self.db.query(PlantVariety).filter(
            PlantVariety.common_name.ilike(f"%{name}%")
        ).all()

    def create(self, **kwargs) -> PlantVariety:
        """Create a new plant variety (admin/seed data only)"""
        variety = PlantVariety(**kwargs)
        self.db.add(variety)
        self.db.commit()
        self.db.refresh(variety)
        return variety
