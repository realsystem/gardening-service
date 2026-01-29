"""Add soil and irrigation tracking tables

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-01-28 23:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd4e5f6g7h8i9'
down_revision = 'c3d4e5f6g7h8'
branch_labels = None
depends_on = None


def upgrade():
    # Create soil_samples table
    op.create_table(
        'soil_samples',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('garden_id', sa.Integer(), nullable=True),
        sa.Column('planting_event_id', sa.Integer(), nullable=True),
        sa.Column('ph', sa.Float(), nullable=False),
        sa.Column('nitrogen_ppm', sa.Float(), nullable=True),
        sa.Column('phosphorus_ppm', sa.Float(), nullable=True),
        sa.Column('potassium_ppm', sa.Float(), nullable=True),
        sa.Column('organic_matter_percent', sa.Float(), nullable=True),
        sa.Column('moisture_percent', sa.Float(), nullable=True),
        sa.Column('date_collected', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['garden_id'], ['gardens.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['planting_event_id'], ['planting_events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_soil_samples_id'), 'soil_samples', ['id'], unique=False)

    # Create irrigation_events table
    op.create_table(
        'irrigation_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('garden_id', sa.Integer(), nullable=True),
        sa.Column('planting_event_id', sa.Integer(), nullable=True),
        sa.Column('irrigation_date', sa.DateTime(), nullable=False),
        sa.Column('water_volume_liters', sa.Float(), nullable=True),
        sa.Column(
            'irrigation_method',
            sa.Enum('drip', 'sprinkler', 'hand_watering', 'soaker_hose', 'flood', 'misting', name='irrigationmethod'),
            nullable=False
        ),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['garden_id'], ['gardens.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['planting_event_id'], ['planting_events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_irrigation_events_id'), 'irrigation_events', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_irrigation_events_id'), table_name='irrigation_events')
    op.drop_table('irrigation_events')
    op.execute('DROP TYPE irrigationmethod')

    op.drop_index(op.f('ix_soil_samples_id'), table_name='soil_samples')
    op.drop_table('soil_samples')
