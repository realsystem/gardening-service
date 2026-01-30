"""Garden repository"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.garden import Garden


class GardenRepository:
    """Repository for Garden database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, **kwargs) -> Garden:
        """Create a new garden with any valid Garden model fields"""
        garden = Garden(
            user_id=user_id,
            **kwargs
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

    def get_gardens_on_land(self, land_id: int) -> List[Garden]:
        """
        Get all gardens placed on a specific land.
        Only returns gardens with spatial data (x, y, width, height all set).
        """
        return self.db.query(Garden).filter(
            Garden.land_id == land_id,
            Garden.x.isnot(None),
            Garden.y.isnot(None),
            Garden.width.isnot(None),
            Garden.height.isnot(None)
        ).all()

    def get_garden_with_land(self, garden_id: int) -> Optional[Garden]:
        """
        Get garden with land relationship eager-loaded.
        Useful for validation when updating layout.
        """
        return self.db.query(Garden).options(
            joinedload(Garden.land)
        ).filter(Garden.id == garden_id).first()
