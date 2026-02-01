"""fix_unit_system_enum_case

Revision ID: 5011a230ee82
Revises: 4761d9bfe6d4
Create Date: 2026-01-31 22:34:24.531275

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5011a230ee82'
down_revision = '4761d9bfe6d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Drop the default value first
    op.execute("ALTER TABLE users ALTER COLUMN unit_system DROP DEFAULT")

    # Step 2: Convert column to VARCHAR temporarily
    op.execute("ALTER TABLE users ALTER COLUMN unit_system TYPE VARCHAR(20)")

    # Step 3: Update lowercase values to uppercase
    op.execute("UPDATE users SET unit_system = 'METRIC' WHERE unit_system = 'metric'")
    op.execute("UPDATE users SET unit_system = 'IMPERIAL' WHERE unit_system = 'imperial'")

    # Step 4: Drop old enum type
    op.execute("DROP TYPE IF EXISTS unitsystem")

    # Step 5: Create new enum type with uppercase values
    op.execute("CREATE TYPE unitsystem AS ENUM ('METRIC', 'IMPERIAL')")

    # Step 6: Convert column back to enum type
    op.execute("ALTER TABLE users ALTER COLUMN unit_system TYPE unitsystem USING unit_system::unitsystem")

    # Step 7: Set new default value
    op.execute("ALTER TABLE users ALTER COLUMN unit_system SET DEFAULT 'METRIC'")


def downgrade() -> None:
    # Convert column to VARCHAR
    op.execute("ALTER TABLE users ALTER COLUMN unit_system TYPE VARCHAR(20)")

    # Update uppercase values to lowercase
    op.execute("UPDATE users SET unit_system = 'metric' WHERE unit_system = 'METRIC'")
    op.execute("UPDATE users SET unit_system = 'imperial' WHERE unit_system = 'IMPERIAL'")

    # Drop uppercase enum type
    op.execute("DROP TYPE IF EXISTS unitsystem")

    # Recreate lowercase enum type
    op.execute("CREATE TYPE unitsystem AS ENUM ('metric', 'imperial')")

    # Convert column back to enum type
    op.execute("ALTER TABLE users ALTER COLUMN unit_system TYPE unitsystem USING unit_system::unitsystem")

    # Set default value
    op.execute("ALTER TABLE users ALTER COLUMN unit_system SET DEFAULT 'metric'")
