"""add_restricted_crop_fields_to_users

Revision ID: 7d7bbb6bd5a4
Revises: u7v8w9x0y1z2
Create Date: 2026-02-02 20:39:46.796884

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d7bbb6bd5a4'
down_revision = 'u7v8w9x0y1z2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add restricted crop tracking fields to users table
    op.add_column('users', sa.Column('restricted_crop_flag', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('restricted_crop_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('restricted_crop_first_violation', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('restricted_crop_last_violation', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('restricted_crop_reason', sa.String(length=100), nullable=True))


def downgrade() -> None:
    # Remove restricted crop tracking fields from users table
    op.drop_column('users', 'restricted_crop_reason')
    op.drop_column('users', 'restricted_crop_last_violation')
    op.drop_column('users', 'restricted_crop_first_violation')
    op.drop_column('users', 'restricted_crop_count')
    op.drop_column('users', 'restricted_crop_flag')
