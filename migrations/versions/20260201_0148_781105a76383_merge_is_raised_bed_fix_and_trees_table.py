"""Merge is_raised_bed fix and trees table

Revision ID: 781105a76383
Revises: 934ddc276e38, h8i9j0k1l2m3
Create Date: 2026-02-01 01:48:25.236544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '781105a76383'
down_revision = ('934ddc276e38', 'h8i9j0k1l2m3')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
