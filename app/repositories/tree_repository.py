"""Tree repository"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.tree import Tree


class TreeRepository:
    """Repository for Tree database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, **kwargs) -> Tree:
        """Create a new tree with any valid Tree model fields"""
        tree = Tree(
            user_id=user_id,
            **kwargs
        )
        self.db.add(tree)
        self.db.commit()
        self.db.refresh(tree)
        return tree

    def get_by_id(self, tree_id: int) -> Optional[Tree]:
        """Get tree by ID"""
        return self.db.query(Tree).filter(Tree.id == tree_id).first()

    def get_user_trees(self, user_id: int) -> List[Tree]:
        """Get all trees for a user"""
        return self.db.query(Tree).filter(Tree.user_id == user_id).all()

    def get_land_trees(self, land_id: int) -> List[Tree]:
        """Get all trees on a specific land plot"""
        return self.db.query(Tree).filter(Tree.land_id == land_id).all()

    def get_tree_with_species(self, tree_id: int) -> Optional[Tree]:
        """Get tree with species (plant variety) details eager-loaded"""
        return self.db.query(Tree).options(
            joinedload(Tree.species)
        ).filter(Tree.id == tree_id).first()

    def get_land_trees_with_species(self, land_id: int) -> List[Tree]:
        """Get all trees on a land plot with species details"""
        return self.db.query(Tree).options(
            joinedload(Tree.species)
        ).filter(Tree.land_id == land_id).all()

    def update(self, tree: Tree, **kwargs) -> Tree:
        """Update tree"""
        for key, value in kwargs.items():
            if hasattr(tree, key) and value is not None:
                setattr(tree, key, value)
        self.db.commit()
        self.db.refresh(tree)
        return tree

    def delete(self, tree: Tree) -> None:
        """Delete tree"""
        self.db.delete(tree)
        self.db.commit()
