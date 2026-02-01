"""Add x and y position columns to planting_events

Revision ID: p0q1r2s3t4u5
Revises: n5o6p7q8r9s0
Create Date: 2026-02-01 00:03:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'p0q1r2s3t4u5'
down_revision: Union[str, None] = 'n5o6p7q8r9s0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add x and y position columns for spatial companion planting analysis
    op.add_column('planting_events', sa.Column('x', sa.Float(), nullable=True))
    op.add_column('planting_events', sa.Column('y', sa.Float(), nullable=True))


def downgrade() -> None:
    # Remove position columns
    op.drop_column('planting_events', 'y')
    op.drop_column('planting_events', 'x')
