"""Add is_admin column to users table

Revision ID: a1b2c3d4e5f6
Revises: 781105a76383
Create Date: 2026-02-01 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '781105a76383'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_admin column to users table with default False
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    # Remove is_admin column
    op.drop_column('users', 'is_admin')
