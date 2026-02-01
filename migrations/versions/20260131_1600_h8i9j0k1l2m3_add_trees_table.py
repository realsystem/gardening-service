"""Add trees table for shading impact modeling

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-01-31 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h8i9j0k1l2m3'
down_revision: Union[str, None] = 'g7h8i9j0k1l2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create trees table
    op.create_table('trees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('land_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('species_id', sa.Integer(), nullable=True),
        sa.Column('x', sa.Float(), nullable=False),
        sa.Column('y', sa.Float(), nullable=False),
        sa.Column('canopy_radius', sa.Float(), nullable=False),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['land_id'], ['lands.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['species_id'], ['plant_varieties.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trees_id'), 'trees', ['id'], unique=False)
    op.create_index(op.f('ix_trees_user_id'), 'trees', ['user_id'], unique=False)
    op.create_index(op.f('ix_trees_land_id'), 'trees', ['land_id'], unique=False)
    op.create_index(op.f('ix_trees_species_id'), 'trees', ['species_id'], unique=False)


def downgrade():
    # Drop trees table and indexes
    op.drop_index(op.f('ix_trees_species_id'), table_name='trees')
    op.drop_index(op.f('ix_trees_land_id'), table_name='trees')
    op.drop_index(op.f('ix_trees_user_id'), table_name='trees')
    op.drop_index(op.f('ix_trees_id'), table_name='trees')
    op.drop_table('trees')
