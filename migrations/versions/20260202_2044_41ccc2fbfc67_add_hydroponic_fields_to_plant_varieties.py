"""add_hydroponic_fields_to_plant_varieties

Revision ID: 41ccc2fbfc67
Revises: 7d7bbb6bd5a4
Create Date: 2026-02-02 20:44:28.367129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41ccc2fbfc67'
down_revision = '7d7bbb6bd5a4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add hydroponic EC (Electrical Conductivity) fields for different growth stages
    op.add_column('plant_varieties', sa.Column('seedling_ec_min', sa.Float(), nullable=True))
    op.add_column('plant_varieties', sa.Column('seedling_ec_max', sa.Float(), nullable=True))
    op.add_column('plant_varieties', sa.Column('vegetative_ec_min', sa.Float(), nullable=True))
    op.add_column('plant_varieties', sa.Column('vegetative_ec_max', sa.Float(), nullable=True))
    op.add_column('plant_varieties', sa.Column('flowering_ec_min', sa.Float(), nullable=True))
    op.add_column('plant_varieties', sa.Column('flowering_ec_max', sa.Float(), nullable=True))
    op.add_column('plant_varieties', sa.Column('fruiting_ec_min', sa.Float(), nullable=True))
    op.add_column('plant_varieties', sa.Column('fruiting_ec_max', sa.Float(), nullable=True))

    # Add pH range fields
    op.add_column('plant_varieties', sa.Column('optimal_ph_min', sa.Float(), nullable=True))
    op.add_column('plant_varieties', sa.Column('optimal_ph_max', sa.Float(), nullable=True))

    # Add solution change interval fields
    op.add_column('plant_varieties', sa.Column('solution_change_days_min', sa.Integer(), nullable=True))
    op.add_column('plant_varieties', sa.Column('solution_change_days_max', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove hydroponic fields from plant_varieties table
    op.drop_column('plant_varieties', 'solution_change_days_max')
    op.drop_column('plant_varieties', 'solution_change_days_min')
    op.drop_column('plant_varieties', 'optimal_ph_max')
    op.drop_column('plant_varieties', 'optimal_ph_min')
    op.drop_column('plant_varieties', 'fruiting_ec_max')
    op.drop_column('plant_varieties', 'fruiting_ec_min')
    op.drop_column('plant_varieties', 'flowering_ec_max')
    op.drop_column('plant_varieties', 'flowering_ec_min')
    op.drop_column('plant_varieties', 'vegetative_ec_max')
    op.drop_column('plant_varieties', 'vegetative_ec_min')
    op.drop_column('plant_varieties', 'seedling_ec_max')
    op.drop_column('plant_varieties', 'seedling_ec_min')
