"""merge is_admin and structures

Revision ID: 100cd15dbb70
Revises: a1b2c3d4e5f6, structures_v001
Create Date: 2026-02-01 05:41:44.423820

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '100cd15dbb70'
down_revision = ('a1b2c3d4e5f6', 'structures_v001')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
