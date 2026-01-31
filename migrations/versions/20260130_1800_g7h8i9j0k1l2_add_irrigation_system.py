"""Add irrigation system tables and garden irrigation fields

Revision ID: g7h8i9j0k1l2
Revises: f6g7h8i9j0k1
Create Date: 2026-01-30 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'g7h8i9j0k1l2'
down_revision: Union[str, None] = 'f6g7h8i9j0k1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create irrigation_sources table
    op.create_table(
        'irrigation_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('source_type', sa.String(), nullable=False),
        sa.Column('flow_capacity_lpm', sa.Float(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_irrigation_sources_id'), 'irrigation_sources', ['id'], unique=False)

    # Create irrigation_zones table
    op.create_table(
        'irrigation_zones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('irrigation_source_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('delivery_type', sa.String(), nullable=False),
        sa.Column('schedule', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['irrigation_source_id'], ['irrigation_sources.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_irrigation_zones_id'), 'irrigation_zones', ['id'], unique=False)

    # Create watering_events table
    op.create_table(
        'watering_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('irrigation_zone_id', sa.Integer(), nullable=False),
        sa.Column('watered_at', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Float(), nullable=False),
        sa.Column('estimated_volume_liters', sa.Float(), nullable=True),
        sa.Column('is_manual', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['irrigation_zone_id'], ['irrigation_zones.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_watering_events_id'), 'watering_events', ['id'], unique=False)
    op.create_index(op.f('ix_watering_events_watered_at'), 'watering_events', ['watered_at'], unique=False)

    # Add irrigation fields to gardens table
    op.add_column('gardens', sa.Column('irrigation_zone_id', sa.Integer(), nullable=True))
    op.add_column('gardens', sa.Column('mulch_depth_inches', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('is_raised_bed', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('gardens', sa.Column('soil_texture_override', sa.String(length=50), nullable=True))

    # Create foreign key and index for irrigation_zone_id
    op.create_foreign_key(
        'fk_gardens_irrigation_zone_id',
        'gardens',
        'irrigation_zones',
        ['irrigation_zone_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_index(op.f('ix_gardens_irrigation_zone_id'), 'gardens', ['irrigation_zone_id'], unique=False)


def downgrade() -> None:
    # Remove irrigation fields from gardens
    op.drop_index(op.f('ix_gardens_irrigation_zone_id'), table_name='gardens')
    op.drop_constraint('fk_gardens_irrigation_zone_id', 'gardens', type_='foreignkey')
    op.drop_column('gardens', 'soil_texture_override')
    op.drop_column('gardens', 'is_raised_bed')
    op.drop_column('gardens', 'mulch_depth_inches')
    op.drop_column('gardens', 'irrigation_zone_id')

    # Drop watering_events table
    op.drop_index(op.f('ix_watering_events_watered_at'), table_name='watering_events')
    op.drop_index(op.f('ix_watering_events_id'), table_name='watering_events')
    op.drop_table('watering_events')

    # Drop irrigation_zones table
    op.drop_index(op.f('ix_irrigation_zones_id'), table_name='irrigation_zones')
    op.drop_table('irrigation_zones')

    # Drop irrigation_sources table
    op.drop_index(op.f('ix_irrigation_sources_id'), table_name='irrigation_sources')
    op.drop_table('irrigation_sources')
