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
    # Convert is_raised_bed from Integer to Boolean (if needed)
    # Check if column is already boolean before attempting conversion
    from sqlalchemy import inspect
    from sqlalchemy.engine import reflection

    conn = op.get_bind()
    inspector = inspect(conn)
    columns = inspector.get_columns('gardens')
    is_raised_bed_col = next((col for col in columns if col['name'] == 'is_raised_bed'), None)

    # Only convert if column exists and is not already boolean
    if is_raised_bed_col and str(is_raised_bed_col['type']).upper() not in ('BOOLEAN', 'BOOL'):
        op.execute("""
            ALTER TABLE gardens
            ALTER COLUMN is_raised_bed DROP DEFAULT,
            ALTER COLUMN is_raised_bed TYPE BOOLEAN
            USING CASE WHEN is_raised_bed::INTEGER = 0 THEN FALSE ELSE TRUE END,
            ALTER COLUMN is_raised_bed SET DEFAULT FALSE
        """)


def downgrade() -> None:
    # Convert back from Boolean to Integer
    op.execute("""
        ALTER TABLE gardens
        ALTER COLUMN is_raised_bed TYPE INTEGER
        USING CASE WHEN is_raised_bed = FALSE THEN 0 ELSE 1 END
    """)
