"""add_unit_system_to_users

Revision ID: 4761d9bfe6d4
Revises: 100cd15dbb70
Create Date: 2026-02-01 06:17:54.164257

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4761d9bfe6d4'
down_revision = '100cd15dbb70'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create unit_system enum type
    op.execute("CREATE TYPE unitsystem AS ENUM ('metric', 'imperial')")

    # Add unit_system column to users table with default value 'metric'
    op.add_column('users', sa.Column('unit_system', sa.Enum('metric', 'imperial', name='unitsystem'),
                                      nullable=False, server_default='metric'))


def downgrade() -> None:
    # Remove unit_system column
    op.drop_column('users', 'unit_system')

    # Drop the enum type
    op.execute('DROP TYPE IF EXISTS unitsystem')
