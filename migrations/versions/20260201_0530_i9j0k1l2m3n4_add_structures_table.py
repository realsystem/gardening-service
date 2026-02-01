"""Add structures table for shadow casting buildings/obstacles

Revision ID: structures_v001
Revises: 781105a76383
Create Date: 2026-02-01 05:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'structures_v001'
down_revision: Union[str, None] = '781105a76383'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create structures table
    op.create_table('structures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('land_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('x', sa.Float(), nullable=False),
        sa.Column('y', sa.Float(), nullable=False),
        sa.Column('width', sa.Float(), nullable=False),
        sa.Column('depth', sa.Float(), nullable=False),
        sa.Column('height', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['land_id'], ['lands.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_structures_id'), 'structures', ['id'], unique=False)
    op.create_index(op.f('ix_structures_user_id'), 'structures', ['user_id'], unique=False)
    op.create_index(op.f('ix_structures_land_id'), 'structures', ['land_id'], unique=False)


def downgrade():
    # Drop structures table and indexes
    op.drop_index(op.f('ix_structures_land_id'), table_name='structures')
    op.drop_index(op.f('ix_structures_user_id'), table_name='structures')
    op.drop_index(op.f('ix_structures_id'), table_name='structures')
    op.drop_table('structures')
