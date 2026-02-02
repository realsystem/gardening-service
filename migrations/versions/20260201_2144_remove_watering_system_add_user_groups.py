"""Remove watering system and add user groups

Revision ID: q1r2s3t4u5v6
Revises: p0q1r2s3t4u5
Create Date: 2026-02-01 21:44:00

This migration implements the platform simplification refactoring:
- Removes watering/irrigation tracking system (user burden)
- Adds user groups for progressive feature disclosure
- Adds advisory watering fields (passive guidance only)
- Archives data for 30-day retention before deletion

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'q1r2s3t4u5v6'
down_revision = 'p0q1r2s3t4u5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Platform simplification upgrade:
    - Archive watering/irrigation data (30-day retention)
    - Drop watering/irrigation tables
    - Add user groups (amateur/farmer/researcher)
    - Add advisory watering guidance fields
    """

    # ============================================
    # STEP 1: Archive existing data (30-day retention)
    # ============================================

    # Archive watering events
    op.execute("""
        CREATE TABLE IF NOT EXISTS _archive_watering_events AS
        SELECT
            *,
            CURRENT_TIMESTAMP as archived_at,
            CURRENT_TIMESTAMP + INTERVAL '30 days' as delete_after
        FROM watering_events
    """)

    # Archive irrigation events
    op.execute("""
        CREATE TABLE IF NOT EXISTS _archive_irrigation_events AS
        SELECT
            *,
            CURRENT_TIMESTAMP as archived_at,
            CURRENT_TIMESTAMP + INTERVAL '30 days' as delete_after
        FROM irrigation_events
    """)

    # Archive irrigation zones
    op.execute("""
        CREATE TABLE IF NOT EXISTS _archive_irrigation_zones AS
        SELECT
            *,
            CURRENT_TIMESTAMP as archived_at,
            CURRENT_TIMESTAMP + INTERVAL '30 days' as delete_after
        FROM irrigation_zones
    """)

    # Archive irrigation sources
    op.execute("""
        CREATE TABLE IF NOT EXISTS _archive_irrigation_sources AS
        SELECT
            *,
            CURRENT_TIMESTAMP as archived_at,
            CURRENT_TIMESTAMP + INTERVAL '30 days' as delete_after
        FROM irrigation_sources
    """)

    print("✓ Archived watering/irrigation data (30-day retention)")

    # ============================================
    # STEP 2: Drop foreign key constraints
    # ============================================

    # Drop irrigation_zone_id from gardens (if exists)
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # Check if column exists before trying to drop constraint
    columns = [col['name'] for col in inspector.get_columns('gardens')]
    if 'irrigation_zone_id' in columns:
        # Check if constraint exists
        fkeys = inspector.get_foreign_keys('gardens')
        constraint_names = [fk['name'] for fk in fkeys if fk.get('constrained_columns') == ['irrigation_zone_id']]
        if constraint_names:
            op.drop_constraint(constraint_names[0], 'gardens', type_='foreignkey')
        op.drop_column('gardens', 'irrigation_zone_id')
        print("✓ Removed irrigation_zone_id from gardens")
    else:
        print("✓ irrigation_zone_id column not present (already removed)")

    # ============================================
    # STEP 3: Drop watering/irrigation tables
    # ============================================

    # Check and drop tables if they exist
    tables = inspector.get_table_names()

    if 'watering_events' in tables:
        op.drop_table('watering_events')
    if 'irrigation_events' in tables:
        op.drop_table('irrigation_events')
    if 'irrigation_zones' in tables:
        op.drop_table('irrigation_zones')
    if 'irrigation_sources' in tables:
        op.drop_table('irrigation_sources')

    print("✓ Dropped watering/irrigation tables (if existed)")

    # ============================================
    # STEP 4: Add user groups enum and columns
    # ============================================

    # Create user group enum
    op.execute("""
        CREATE TYPE usergroup AS ENUM (
            'amateur_gardener',
            'farmer',
            'scientific_researcher'
        )
    """)

    # Add user_group column (default: amateur_gardener)
    op.add_column('users',
        sa.Column('user_group',
                  postgresql.ENUM('amateur_gardener', 'farmer', 'scientific_researcher',
                                  name='usergroup', create_type=False),
                  server_default='amateur_gardener',
                  nullable=False))

    # Add tree visibility toggle (amateur users: hidden by default)
    op.add_column('users',
        sa.Column('show_trees',
                  sa.Boolean(),
                  server_default='false',
                  nullable=False))

    # Add alert toggle (all users: disabled by default)
    op.add_column('users',
        sa.Column('enable_alerts',
                  sa.Boolean(),
                  server_default='false',
                  nullable=False))

    print("✓ Added user groups and feature toggles")

    # ============================================
    # STEP 5: Add advisory watering fields to plant_varieties
    # ============================================

    # Water needs indicator (low/medium/high)
    op.add_column('plant_varieties',
        sa.Column('water_needs',
                  sa.String(length=20),
                  nullable=True))

    # Drought tolerance flag
    op.add_column('plant_varieties',
        sa.Column('drought_tolerant',
                  sa.Boolean(),
                  server_default='false',
                  nullable=False))

    # Typical watering frequency (advisory only, no tracking)
    op.add_column('plant_varieties',
        sa.Column('typical_watering_frequency_days',
                  sa.Integer(),
                  nullable=True))

    # Human-readable guidance text
    op.add_column('plant_varieties',
        sa.Column('watering_guidance',
                  sa.Text(),
                  nullable=True))

    print("✓ Added advisory watering fields to plant_varieties")

    # ============================================
    # STEP 6: Seed default watering guidance
    # ============================================

    # Set defaults for common plants
    op.execute("""
        UPDATE plant_varieties SET
            water_needs = 'medium',
            typical_watering_frequency_days = 3,
            watering_guidance = 'Water deeply every 2-4 days in summer. Reduce frequency in cooler weather.'
        WHERE common_name IN ('Tomato', 'Pepper', 'Cucumber', 'Squash', 'Zucchini')
    """)

    op.execute("""
        UPDATE plant_varieties SET
            water_needs = 'high',
            typical_watering_frequency_days = 2,
            watering_guidance = 'Keep soil consistently moist. Water daily in hot weather.'
        WHERE common_name IN ('Lettuce', 'Spinach', 'Celery', 'Cabbage')
    """)

    op.execute("""
        UPDATE plant_varieties SET
            water_needs = 'low',
            drought_tolerant = true,
            typical_watering_frequency_days = 5,
            watering_guidance = 'Water only when soil is dry. Tolerates drought well.'
        WHERE common_name IN ('Rosemary', 'Thyme', 'Lavender', 'Sage')
    """)

    print("✓ Seeded watering guidance for common plants")

    print("""
    ╔════════════════════════════════════════════════════════╗
    ║  PLATFORM SIMPLIFICATION MIGRATION COMPLETE            ║
    ║                                                        ║
    ║  Removed: Watering/irrigation tracking                ║
    ║  Added: User groups (amateur/farmer/researcher)       ║
    ║  Added: Advisory watering guidance                    ║
    ║                                                        ║
    ║  Archived data: Available for 30 days                 ║
    ╚════════════════════════════════════════════════════════╝
    """)


def downgrade() -> None:
    """
    Rollback: Restore watering system from archive (if within 30 days)

    WARNING: Only works if archive tables still exist (< 30 days)
    """

    # ============================================
    # STEP 1: Remove added fields
    # ============================================

    op.drop_column('plant_varieties', 'watering_guidance')
    op.drop_column('plant_varieties', 'typical_watering_frequency_days')
    op.drop_column('plant_varieties', 'drought_tolerant')
    op.drop_column('plant_varieties', 'water_needs')

    op.drop_column('users', 'enable_alerts')
    op.drop_column('users', 'show_trees')
    op.drop_column('users', 'user_group')

    # Drop user group enum
    op.execute("DROP TYPE usergroup")

    # ============================================
    # STEP 2: Recreate watering/irrigation tables
    # ============================================

    # Recreate irrigation_sources
    op.create_table('irrigation_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('source_type', sa.String(), nullable=False),
        sa.Column('flow_rate_liters_per_minute', sa.Float(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Recreate irrigation_zones
    op.create_table('irrigation_zones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('irrigation_source_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('delivery_type', sa.String(), nullable=False),
        sa.Column('schedule', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['irrigation_source_id'], ['irrigation_sources.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Recreate irrigation_events
    op.create_table('irrigation_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('irrigation_zone_id', sa.Integer(), nullable=False),
        sa.Column('executed_at', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Float(), nullable=False),
        sa.Column('volume_liters', sa.Float(), nullable=True),
        sa.Column('was_scheduled', sa.Boolean(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['irrigation_zone_id'], ['irrigation_zones.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Recreate watering_events
    op.create_table('watering_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('irrigation_zone_id', sa.Integer(), nullable=False),
        sa.Column('watered_at', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Float(), nullable=False),
        sa.Column('estimated_volume_liters', sa.Float(), nullable=True),
        sa.Column('is_manual', sa.Boolean(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['irrigation_zone_id'], ['irrigation_zones.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ============================================
    # STEP 3: Restore data from archive (if exists)
    # ============================================

    op.execute("""
        INSERT INTO irrigation_sources
        SELECT id, user_id, name, source_type, flow_rate_liters_per_minute,
               notes, created_at, updated_at
        FROM _archive_irrigation_sources
        WHERE delete_after > CURRENT_TIMESTAMP
    """)

    op.execute("""
        INSERT INTO irrigation_zones
        SELECT id, user_id, irrigation_source_id, name, delivery_type,
               schedule, notes, created_at, updated_at
        FROM _archive_irrigation_zones
        WHERE delete_after > CURRENT_TIMESTAMP
    """)

    op.execute("""
        INSERT INTO irrigation_events
        SELECT id, user_id, irrigation_zone_id, executed_at, duration_minutes,
               volume_liters, was_scheduled, notes, created_at
        FROM _archive_irrigation_events
        WHERE delete_after > CURRENT_TIMESTAMP
    """)

    op.execute("""
        INSERT INTO watering_events
        SELECT id, user_id, irrigation_zone_id, watered_at, duration_minutes,
               estimated_volume_liters, is_manual, notes, created_at
        FROM _archive_watering_events
        WHERE delete_after > CURRENT_TIMESTAMP
    """)

    # ============================================
    # STEP 4: Restore foreign key to gardens
    # ============================================

    op.add_column('gardens',
        sa.Column('irrigation_zone_id', sa.Integer(), nullable=True))

    op.create_foreign_key('gardens_irrigation_zone_id_fkey',
                         'gardens', 'irrigation_zones',
                         ['irrigation_zone_id'], ['id'],
                         ondelete='SET NULL')

    print("✓ Rollback complete: Watering system restored from archive")
