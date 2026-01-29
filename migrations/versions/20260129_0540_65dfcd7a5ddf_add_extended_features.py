"""add_extended_features

Revision ID: 65dfcd7a5ddf
Revises: c001108a6d8e
Create Date: 2026-01-29 05:40:23.148058

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '65dfcd7a5ddf'
down_revision = 'c001108a6d8e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types for new fields
    op.execute("CREATE TYPE taskpriority AS ENUM ('low', 'medium', 'high')")
    op.execute("CREATE TYPE planthealth AS ENUM ('healthy', 'stressed', 'diseased')")
    op.execute("CREATE TYPE recurrencefrequency AS ENUM ('daily', 'weekly', 'biweekly', 'monthly')")

    # Add new columns to care_tasks
    op.add_column('care_tasks', sa.Column('priority', sa.Enum('low', 'medium', 'high', name='taskpriority'), nullable=False, server_default='medium'))
    op.add_column('care_tasks', sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('care_tasks', sa.Column('recurrence_frequency', sa.Enum('daily', 'weekly', 'biweekly', 'monthly', name='recurrencefrequency'), nullable=True))
    op.add_column('care_tasks', sa.Column('parent_task_id', sa.Integer(), nullable=True))

    # Add foreign key for recurring task parent
    op.create_foreign_key('fk_care_tasks_parent_task', 'care_tasks', 'care_tasks', ['parent_task_id'], ['id'], ondelete='SET NULL')

    # Add new columns to planting_events
    op.add_column('planting_events', sa.Column('health_status', sa.Enum('healthy', 'stressed', 'diseased', name='planthealth'), nullable=True))
    op.add_column('planting_events', sa.Column('plant_notes', sa.Text(), nullable=True))

    # Add new column to germination_events
    op.add_column('germination_events', sa.Column('germination_success_rate', sa.Float(), nullable=True))


def downgrade() -> None:
    # Remove columns from germination_events
    op.drop_column('germination_events', 'germination_success_rate')

    # Remove columns from planting_events
    op.drop_column('planting_events', 'plant_notes')
    op.drop_column('planting_events', 'health_status')

    # Remove foreign key and columns from care_tasks
    op.drop_constraint('fk_care_tasks_parent_task', 'care_tasks', type_='foreignkey')
    op.drop_column('care_tasks', 'parent_task_id')
    op.drop_column('care_tasks', 'recurrence_frequency')
    op.drop_column('care_tasks', 'is_recurring')
    op.drop_column('care_tasks', 'priority')

    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS recurrencefrequency')
    op.execute('DROP TYPE IF EXISTS planthealth')
    op.execute('DROP TYPE IF EXISTS taskpriority')
