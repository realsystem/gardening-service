"""add_indoor_gardening_support

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-01-28 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create new ENUM types for indoor features
    op.execute("CREATE TYPE gardentype AS ENUM ('outdoor', 'indoor')")
    op.execute("CREATE TYPE lightsourcetype AS ENUM ('led', 'fluorescent', 'natural_supplement', 'hps', 'mh')")

    # Extend TaskType ENUM with indoor task types
    op.execute("ALTER TYPE tasktype ADD VALUE IF NOT EXISTS 'adjust_lighting'")
    op.execute("ALTER TYPE tasktype ADD VALUE IF NOT EXISTS 'adjust_temperature'")
    op.execute("ALTER TYPE tasktype ADD VALUE IF NOT EXISTS 'adjust_humidity'")
    op.execute("ALTER TYPE tasktype ADD VALUE IF NOT EXISTS 'nutrient_solution'")
    op.execute("ALTER TYPE tasktype ADD VALUE IF NOT EXISTS 'train_plant'")

    # Add indoor garden fields to gardens table
    op.add_column('gardens', sa.Column('garden_type', sa.Enum('outdoor', 'indoor', name='gardentype'), nullable=False, server_default='outdoor'))
    op.add_column('gardens', sa.Column('location', sa.String(length=100), nullable=True))
    op.add_column('gardens', sa.Column('light_source_type', sa.Enum('led', 'fluorescent', 'natural_supplement', 'hps', 'mh', name='lightsourcetype'), nullable=True))
    op.add_column('gardens', sa.Column('light_hours_per_day', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('temp_min_f', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('temp_max_f', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('humidity_min_percent', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('humidity_max_percent', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('container_type', sa.String(length=100), nullable=True))
    op.add_column('gardens', sa.Column('grow_medium', sa.String(length=100), nullable=True))

    # Create sensor_readings table
    op.create_table(
        'sensor_readings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('garden_id', sa.Integer(), nullable=False),
        sa.Column('reading_date', sa.Date(), nullable=False),
        sa.Column('temperature_f', sa.Float(), nullable=True),
        sa.Column('humidity_percent', sa.Float(), nullable=True),
        sa.Column('light_hours', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['garden_id'], ['gardens.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sensor_readings_id'), 'sensor_readings', ['id'], unique=False)
    op.create_index(op.f('ix_sensor_readings_reading_date'), 'sensor_readings', ['reading_date'], unique=False)


def downgrade() -> None:
    # Drop sensor_readings table
    op.drop_index(op.f('ix_sensor_readings_reading_date'), table_name='sensor_readings')
    op.drop_index(op.f('ix_sensor_readings_id'), table_name='sensor_readings')
    op.drop_table('sensor_readings')

    # Remove columns from gardens table
    op.drop_column('gardens', 'grow_medium')
    op.drop_column('gardens', 'container_type')
    op.drop_column('gardens', 'humidity_max_percent')
    op.drop_column('gardens', 'humidity_min_percent')
    op.drop_column('gardens', 'temp_max_f')
    op.drop_column('gardens', 'temp_min_f')
    op.drop_column('gardens', 'light_hours_per_day')
    op.drop_column('gardens', 'light_source_type')
    op.drop_column('gardens', 'location')
    op.drop_column('gardens', 'garden_type')

    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS lightsourcetype')
    op.execute('DROP TYPE IF EXISTS gardentype')
    # Note: Cannot easily remove values from TaskType ENUM in PostgreSQL
