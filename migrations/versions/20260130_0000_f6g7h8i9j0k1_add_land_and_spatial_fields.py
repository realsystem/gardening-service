"""add_land_and_spatial_fields

Revision ID: f6g7h8i9j0k1
Revises: e5f6g7h8i9j0
Create Date: 2026-01-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6g7h8i9j0k1'
down_revision = 'e5f6g7h8i9j0'
branch_labels = None
depends_on = None


def upgrade():
    # Create lands table
    op.create_table('lands',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('width', sa.Float(), nullable=False),
        sa.Column('height', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lands_id'), 'lands', ['id'], unique=False)
    op.create_index(op.f('ix_lands_user_id'), 'lands', ['user_id'], unique=False)

    # Add spatial columns to gardens table
    op.add_column('gardens', sa.Column('land_id', sa.Integer(), nullable=True))
    op.add_column('gardens', sa.Column('x', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('y', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('width', sa.Float(), nullable=True))
    op.add_column('gardens', sa.Column('height', sa.Float(), nullable=True))

    # Add foreign key constraint and index
    op.create_foreign_key('fk_gardens_land_id', 'gardens', 'lands', ['land_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_gardens_land_id'), 'gardens', ['land_id'], unique=False)


def downgrade():
    # Remove spatial columns and constraints from gardens
    op.drop_index(op.f('ix_gardens_land_id'), table_name='gardens')
    op.drop_constraint('fk_gardens_land_id', 'gardens', type_='foreignkey')
    op.drop_column('gardens', 'height')
    op.drop_column('gardens', 'width')
    op.drop_column('gardens', 'y')
    op.drop_column('gardens', 'x')
    op.drop_column('gardens', 'land_id')

    # Drop lands table
    op.drop_index(op.f('ix_lands_user_id'), table_name='lands')
    op.drop_index(op.f('ix_lands_id'), table_name='lands')
    op.drop_table('lands')
