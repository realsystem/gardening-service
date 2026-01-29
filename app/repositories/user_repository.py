"""User repository"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    """Repository for User database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, hashed_password: str, **kwargs) -> User:
        """Create a new user"""
        user = User(
            email=email,
            hashed_password=hashed_password,
            **kwargs
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def update(self, user: User, **kwargs) -> User:
        """Update user"""
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        """Delete user"""
        self.db.delete(user)
        self.db.commit()
