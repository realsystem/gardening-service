"""Add companion_relationships table for science-based companion planting

Revision ID: n5o6p7q8r9s0
Revises: 5011a230ee82
Create Date: 2026-02-01 23:00:00.000000

This migration adds support for tracking plant-to-plant companion relationships
based on documented agronomic science. Relationships are:
- Bidirectional and normalized (plant_a_id < plant_b_id)
- Science-based with documented sources
- Distance-aware (effective and optimal ranges)
- Classified by confidence level
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'n5o6p7q8r9s0'
down_revision: Union[str, None] = '5011a230ee82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create companion_relationships table
    # SQLAlchemy will automatically create the enum types
    op.create_table(
        'companion_relationships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plant_a_id', sa.Integer(), nullable=False),
        sa.Column('plant_b_id', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.Enum('beneficial', 'neutral', 'antagonistic', name='relationshiptype'), nullable=False),
        sa.Column('mechanism', sa.Text(), nullable=False),
        sa.Column('confidence_level', sa.Enum('high', 'medium', 'low', name='confidencelevel'), nullable=False),
        sa.Column('effective_distance_m', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('optimal_distance_m', sa.Float(), nullable=True),
        sa.Column('source_reference', sa.Text(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        # Enforce normalized plant pairs (no duplicate combinations)
        sa.UniqueConstraint('plant_a_id', 'plant_b_id', name='unique_plant_pair')
    )

    # Create indexes for efficient lookups
    op.create_index('idx_companion_plants', 'companion_relationships', ['plant_a_id', 'plant_b_id'])
    op.create_index('idx_relationship_type', 'companion_relationships', ['relationship_type'])
    op.create_index(op.f('ix_companion_relationships_id'), 'companion_relationships', ['id'], unique=False)
    op.create_index(op.f('ix_companion_relationships_plant_a_id'), 'companion_relationships', ['plant_a_id'], unique=False)
    op.create_index(op.f('ix_companion_relationships_plant_b_id'), 'companion_relationships', ['plant_b_id'], unique=False)


def downgrade():
    # Drop table and indexes
    op.drop_index(op.f('ix_companion_relationships_plant_b_id'), table_name='companion_relationships')
    op.drop_index(op.f('ix_companion_relationships_plant_a_id'), table_name='companion_relationships')
    op.drop_index(op.f('ix_companion_relationships_id'), table_name='companion_relationships')
    op.drop_index('idx_relationship_type', table_name='companion_relationships')
    op.drop_index('idx_companion_plants', table_name='companion_relationships')
    op.drop_table('companion_relationships')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS confidencelevel')
    op.execute('DROP TYPE IF EXISTS relationshiptype')
