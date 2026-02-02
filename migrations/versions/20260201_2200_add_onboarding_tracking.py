"""Add onboarding tracking to users

Revision ID: t1u2v3w4x5y6
Revises: n5o6p7q8r9s0
Create Date: 2026-02-01 22:00:00.000000

Phase 3: Onboarding Simplification - Track whether users have completed
the simplified 3-screen onboarding wizard.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 't1u2v3w4x5y6'
down_revision = 'n5o6p7q8r9s0'
branch_labels = None
depends_on = None


def upgrade():
    """Add has_completed_onboarding field to users table"""
    op.add_column('users',
        sa.Column('has_completed_onboarding',
                  sa.Boolean(),
                  server_default='false',
                  nullable=False))

    # Existing users are considered to have "completed" onboarding
    # (they've already created gardens/plants through the old flow)
    op.execute("""
        UPDATE users
        SET has_completed_onboarding = true
        WHERE id IN (
            SELECT DISTINCT user_id FROM gardens
        )
    """)


def downgrade():
    """Remove has_completed_onboarding field"""
    op.drop_column('users', 'has_completed_onboarding')
