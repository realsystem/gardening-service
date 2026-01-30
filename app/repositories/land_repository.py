"""Land repository"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.land import Land


class LandRepository:
    """Repository for Land database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, **kwargs) -> Land:
        """Create a new land with any valid Land model fields"""
        land = Land(
            user_id=user_id,
            **kwargs
        )
        self.db.add(land)
        self.db.commit()
        self.db.refresh(land)
        return land

    def get_by_id(self, land_id: int) -> Optional[Land]:
        """Get land by ID"""
        return self.db.query(Land).filter(Land.id == land_id).first()

    def get_user_lands(self, user_id: int) -> List[Land]:
        """Get all lands for a user"""
        return self.db.query(Land).filter(Land.user_id == user_id).all()

    def get_land_with_gardens(self, land_id: int) -> Optional[Land]:
        """
        Get land with all gardens eager-loaded.
        Useful for overlap checking when placing/moving gardens.
        """
        return self.db.query(Land).options(
            joinedload(Land.gardens)
        ).filter(Land.id == land_id).first()

    def update(self, land: Land, **kwargs) -> Land:
        """Update land"""
        for key, value in kwargs.items():
            if hasattr(land, key) and value is not None:
                setattr(land, key, value)
        self.db.commit()
        self.db.refresh(land)
        return land

    def delete(self, land: Land) -> None:
        """Delete land (sets land_id=NULL on gardens due to CASCADE SET NULL)"""
        self.db.delete(land)
        self.db.commit()
