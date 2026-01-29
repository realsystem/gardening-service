"""Garden repository"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.garden import Garden


class GardenRepository:
    """Repository for Garden database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, name: str, description: Optional[str] = None) -> Garden:
        """Create a new garden"""
        garden = Garden(
            user_id=user_id,
            name=name,
            description=description
        )
        self.db.add(garden)
        self.db.commit()
        self.db.refresh(garden)
        return garden

    def get_by_id(self, garden_id: int) -> Optional[Garden]:
        """Get garden by ID"""
        return self.db.query(Garden).filter(Garden.id == garden_id).first()

    def get_user_gardens(self, user_id: int) -> List[Garden]:
        """Get all gardens for a user"""
        return self.db.query(Garden).filter(Garden.user_id == user_id).all()

    def update(self, garden: Garden, **kwargs) -> Garden:
        """Update garden"""
        for key, value in kwargs.items():
            if hasattr(garden, key) and value is not None:
                setattr(garden, key, value)
        self.db.commit()
        self.db.refresh(garden)
        return garden

    def delete(self, garden: Garden) -> None:
        """Delete garden"""
        self.db.delete(garden)
        self.db.commit()
