"""Fix is_raised_bed column type to boolean

Revision ID: 934ddc276e38
Revises: g7h8i9j0k1l2
Create Date: 2026-01-31 06:59:46.438988

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '934ddc276e38'
down_revision = 'g7h8i9j0k1l2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Convert is_raised_bed from Integer to Boolean
    # PostgreSQL requires explicit casting and default change
    op.execute("""
        ALTER TABLE gardens
        ALTER COLUMN is_raised_bed DROP DEFAULT,
        ALTER COLUMN is_raised_bed TYPE BOOLEAN
        USING CASE WHEN is_raised_bed = 0 THEN FALSE ELSE TRUE END,
        ALTER COLUMN is_raised_bed SET DEFAULT FALSE
    """)


def downgrade() -> None:
    # Convert back from Boolean to Integer
    op.execute("""
        ALTER TABLE gardens
        ALTER COLUMN is_raised_bed TYPE INTEGER
        USING CASE WHEN is_raised_bed = FALSE THEN 0 ELSE 1 END
    """)
