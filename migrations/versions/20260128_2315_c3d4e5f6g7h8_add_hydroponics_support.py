"""add_hydroponics_support

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-01-28 23:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c3d4e5f6g7h8'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade():
    # Create HydroSystemType ENUM
    hydro_system_type_enum = postgresql.ENUM(
        'nft', 'dwc', 'ebb_flow', 'aeroponics', 'drip', 'wick',
        name='hydrosystemtype',
        create_type=True
    )
    hydro_system_type_enum.create(op.get_bind(), checkfirst=True)

    # Extend TaskType ENUM with hydroponics task types
    op.execute("""
        ALTER TYPE tasktype ADD VALUE IF NOT EXISTS 'check_nutrient_solution';
        ALTER TYPE tasktype ADD VALUE IF NOT EXISTS 'adjust_ph';
        ALTER TYPE tasktype ADD VALUE IF NOT EXISTS 'replace_nutrient_solution';
        ALTER TYPE tasktype ADD VALUE IF NOT EXISTS 'clean_reservoir';
        ALTER TYPE tasktype ADD VALUE IF NOT EXISTS 'adjust_water_circulation';
    """)

    # Add hydroponics fields to gardens table
    op.add_column('gardens', sa.Column('is_hydroponic', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('gardens', sa.Column('hydro_system_type', hydro_system_type_enum, nullable=True))
    op.add_column('gardens', sa.Column('reservoir_size_liters', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('nutrient_schedule', sa.Text(), nullable=True))
    op.add_column('gardens', sa.Column('ph_min', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('ph_max', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('ec_min', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('ec_max', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('ppm_min', sa.Integer(), nullable=True))
    op.add_column('gardens', sa.Column('ppm_max', sa.Integer(), nullable=True))
    op.add_column('gardens', sa.Column('water_temp_min_f', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('water_temp_max_f', sa.Float(), nullable=True))

    # Add hydroponics sensor reading fields to sensor_readings table
    op.add_column('sensor_readings', sa.Column('ph_level', sa.Float(), nullable=True))
    op.add_column('sensor_readings', sa.Column('ec_ms_cm', sa.Float(), nullable=True))
    op.add_column('sensor_readings', sa.Column('ppm', sa.Integer(), nullable=True))
    op.add_column('sensor_readings', sa.Column('water_temp_f', sa.Float(), nullable=True))


def downgrade():
    # Remove hydroponics fields from sensor_readings
    op.drop_column('sensor_readings', 'water_temp_f')
    op.drop_column('sensor_readings', 'ppm')
    op.drop_column('sensor_readings', 'ec_ms_cm')
    op.drop_column('sensor_readings', 'ph_level')

    # Remove hydroponics fields from gardens
    op.drop_column('gardens', 'water_temp_max_f')
    op.drop_column('gardens', 'water_temp_min_f')
    op.drop_column('gardens', 'ppm_max')
    op.drop_column('gardens', 'ppm_min')
    op.drop_column('gardens', 'ec_max')
    op.drop_column('gardens', 'ec_min')
    op.drop_column('gardens', 'ph_max')
    op.drop_column('gardens', 'ph_min')
    op.drop_column('gardens', 'nutrient_schedule')
    op.drop_column('gardens', 'reservoir_size_liters')
    op.drop_column('gardens', 'hydro_system_type')
    op.drop_column('gardens', 'is_hydroponic')

    # Note: Cannot easily remove ENUM values in PostgreSQL
    # Would need to recreate the entire ENUM type
    # For now, leave the task type values in place

    # Drop HydroSystemType ENUM
    hydro_system_type_enum = postgresql.ENUM(name='hydrosystemtype')
    hydro_system_type_enum.drop(op.get_bind(), checkfirst=True)
