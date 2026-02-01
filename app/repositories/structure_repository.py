"""Structure repository"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.structure import Structure


class StructureRepository:
    """Repository for Structure database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, land_id: int, **kwargs) -> Structure:
        """Create a new structure with any valid Structure model fields"""
        structure = Structure(
            user_id=user_id,
            land_id=land_id,
            **kwargs
        )
        self.db.add(structure)
        self.db.commit()
        self.db.refresh(structure)
        return structure

    def get_by_id(self, structure_id: int) -> Optional[Structure]:
        """Get structure by ID"""
        return self.db.query(Structure).filter(Structure.id == structure_id).first()

    def get_by_land(self, land_id: int) -> List[Structure]:
        """Get all structures for a specific land"""
        return self.db.query(Structure).filter(Structure.land_id == land_id).all()

    def get_user_structures(self, user_id: int) -> List[Structure]:
        """Get all structures for a user"""
        return self.db.query(Structure).filter(Structure.user_id == user_id).all()

    def update(self, structure: Structure, **kwargs) -> Structure:
        """Update structure"""
        for key, value in kwargs.items():
            if hasattr(structure, key) and value is not None:
                setattr(structure, key, value)
        self.db.commit()
        self.db.refresh(structure)
        return structure

    def delete(self, structure: Structure) -> None:
        """Delete structure"""
        self.db.delete(structure)
        self.db.commit()
