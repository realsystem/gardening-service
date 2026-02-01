"""add_user_profiles_and_variety_enhancements

Revision ID: user_profiles_v001
Revises: 65dfcd7a5ddf
Create Date: 2026-01-28 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'user_profiles_v001'
down_revision = '65dfcd7a5ddf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add profile fields to users table
    op.add_column('users', sa.Column('display_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('city', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('gardening_preferences', sa.Text(), nullable=True))

    # Add enhanced fields to plant_varieties table
    op.add_column('plant_varieties', sa.Column('photo_url', sa.String(length=500), nullable=True))
    op.add_column('plant_varieties', sa.Column('tags', sa.Text(), nullable=True))

    # Add preferred germination method to seed_batches table
    op.add_column('seed_batches', sa.Column('preferred_germination_method', sa.String(length=100), nullable=True))


def downgrade() -> None:
    # Remove fields from seed_batches
    op.drop_column('seed_batches', 'preferred_germination_method')

    # Remove fields from plant_varieties
    op.drop_column('plant_varieties', 'tags')
    op.drop_column('plant_varieties', 'photo_url')

    # Remove fields from users
    op.drop_column('users', 'gardening_preferences')
    op.drop_column('users', 'city')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'display_name')
