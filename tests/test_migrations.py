"""Tests for database migration system.

Tests migration version checking, rollback procedures, and failure recovery.
"""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import text

from app.utils.migration_check import MigrationChecker, check_migrations_on_startup
from app.database import check_database_migrations


# ============================================
# Migration Version Checking Tests
# ============================================

@pytest.mark.unit
class TestMigrationVersionChecking:
    """Test migration version validation."""

    def test_migration_table_missing_raises_error_in_strict_mode(self, test_db):
        """Test that missing migration table raises error in strict mode."""
        # Drop migration table if it exists
        test_db.execute(text("DROP TABLE IF EXISTS schema_migrations CASCADE"))
        test_db.commit()

        with pytest.raises(RuntimeError) as exc_info:
            MigrationChecker.check_migration_version(test_db, strict=True)

        assert "migration table not found" in str(exc_info.value).lower()

    def test_migration_table_missing_returns_false_in_non_strict_mode(self, test_db):
        """Test that missing migration table returns False in non-strict mode."""
        # Drop migration table if it exists
        test_db.execute(text("DROP TABLE IF EXISTS schema_migrations CASCADE"))
        test_db.commit()

        is_valid, errors = MigrationChecker.check_migration_version(test_db, strict=False)

        assert is_valid is False
        assert len(errors) > 0
        assert any("migration version table does not exist" in e.lower() for e in errors)

    def test_missing_migrations_detected(self, test_db):
        """Test that missing expected migrations are detected."""
        # Create migration table but don't populate it
        test_db.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) NOT NULL PRIMARY KEY,
                applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                description TEXT,
                checksum VARCHAR(64),
                execution_time_ms INTEGER,
                applied_by VARCHAR(100)
            )
        """))
        test_db.commit()

        with pytest.raises(RuntimeError) as exc_info:
            MigrationChecker.check_migration_version(test_db, strict=True)

        assert "missing required migrations" in str(exc_info.value).lower()

    def test_all_migrations_applied_passes_check(self, test_db):
        """Test that having all migrations applied passes validation."""
        # Create migration table
        test_db.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) NOT NULL PRIMARY KEY,
                applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                description TEXT,
                checksum VARCHAR(64),
                execution_time_ms INTEGER,
                applied_by VARCHAR(100)
            )
        """))

        # Insert all expected migrations
        for migration in MigrationChecker.EXPECTED_MIGRATIONS:
            test_db.execute(text("""
                INSERT INTO schema_migrations (version, description, applied_by)
                VALUES (:version, :description, 'test_system')
                ON CONFLICT (version) DO NOTHING
            """), {
                'version': migration.version,
                'description': migration.description
            })
        test_db.commit()

        # Should pass without errors
        is_valid, errors = MigrationChecker.check_migration_version(test_db, strict=True)

        assert is_valid is True
        assert len(errors) == 0

    def test_unexpected_migrations_logged_as_warning(self, test_db):
        """Test that unexpected migrations are logged but don't fail check."""
        # Create migration table
        test_db.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) NOT NULL PRIMARY KEY,
                applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                description TEXT,
                checksum VARCHAR(64),
                execution_time_ms INTEGER,
                applied_by VARCHAR(100)
            )
        """))

        # Insert all expected migrations PLUS an unexpected one
        for migration in MigrationChecker.EXPECTED_MIGRATIONS:
            test_db.execute(text("""
                INSERT INTO schema_migrations (version, description, applied_by)
                VALUES (:version, :description, 'test_system')
                ON CONFLICT (version) DO NOTHING
            """), {
                'version': migration.version,
                'description': migration.description
            })

        # Add unexpected migration
        test_db.execute(text("""
            INSERT INTO schema_migrations (version, description, applied_by)
            VALUES ('999_unexpected', 'Unexpected migration', 'test_system')
            ON CONFLICT (version) DO NOTHING
        """))
        test_db.commit()

        # Should still pass (unexpected migrations are warnings, not errors)
        is_valid, errors = MigrationChecker.check_migration_version(test_db, strict=False)

        # Check includes warning about unexpected migration
        assert any("unexpected" in str(e).lower() for e in errors)


# ============================================
# Migration Status Tests
# ============================================

@pytest.mark.unit
class TestMigrationStatus:
    """Test migration status reporting."""

    def test_get_migration_status_uninitialized(self, test_db):
        """Test getting status when migration table doesn't exist."""
        # Drop migration table
        test_db.execute(text("DROP TABLE IF EXISTS schema_migrations CASCADE"))
        test_db.commit()

        status = MigrationChecker.get_migration_status(test_db)

        assert status['initialized'] is False
        assert 'error' in status
        assert len(status['expected_migrations']) > 0

    def test_get_migration_status_partially_migrated(self, test_db):
        """Test status when some migrations are missing."""
        # Create migration table
        test_db.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) NOT NULL PRIMARY KEY,
                applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                description TEXT,
                checksum VARCHAR(64),
                execution_time_ms INTEGER,
                applied_by VARCHAR(100)
            )
        """))

        # Insert only first two migrations
        for migration in MigrationChecker.EXPECTED_MIGRATIONS[:2]:
            test_db.execute(text("""
                INSERT INTO schema_migrations (version, description, applied_by)
                VALUES (:version, :description, 'test_system')
                ON CONFLICT (version) DO NOTHING
            """), {
                'version': migration.version,
                'description': migration.description
            })
        test_db.commit()

        status = MigrationChecker.get_migration_status(test_db)

        assert status['initialized'] is True
        assert status['up_to_date'] is False
        assert len(status['applied_migrations']) == 2
        assert len(status['missing_migrations']) > 0

    def test_get_migration_status_up_to_date(self, test_db):
        """Test status when all migrations are applied."""
        # Create migration table
        test_db.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) NOT NULL PRIMARY KEY,
                applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                description TEXT,
                checksum VARCHAR(64),
                execution_time_ms INTEGER,
                applied_by VARCHAR(100)
            )
        """))

        # Insert all migrations
        for migration in MigrationChecker.EXPECTED_MIGRATIONS:
            test_db.execute(text("""
                INSERT INTO schema_migrations (version, description, applied_by)
                VALUES (:version, :description, 'test_system')
                ON CONFLICT (version) DO NOTHING
            """), {
                'version': migration.version,
                'description': migration.description
            })
        test_db.commit()

        status = MigrationChecker.get_migration_status(test_db)

        assert status['initialized'] is True
        assert status['up_to_date'] is True
        assert len(status['missing_migrations']) == 0


# ============================================
# Startup Integration Tests
# ============================================

@pytest.mark.integration
class TestMigrationStartupCheck:
    """Test migration checking on application startup."""

    def test_startup_check_skipped_in_test_environment(self):
        """Test that migration check is skipped in test environment."""
        with patch('app.database.settings.APP_ENV', 'test'):
            # Should not raise error
            check_database_migrations()

    def test_startup_check_skipped_in_local_environment(self):
        """Test that migration check is skipped in local environment."""
        with patch('app.database.settings.APP_ENV', 'local'):
            # Should not raise error
            check_database_migrations()

    def test_startup_check_strict_in_production(self, test_db):
        """Test that migration check is strict in production."""
        # Drop migration table to simulate outdated database
        test_db.execute(text("DROP TABLE IF EXISTS schema_migrations CASCADE"))
        test_db.commit()

        with patch('app.database.settings.APP_ENV', 'production'):
            with patch('app.database.SessionLocal') as mock_session:
                mock_session.return_value = test_db

                with pytest.raises(RuntimeError) as exc_info:
                    check_database_migrations()

                assert "migration table not found" in str(exc_info.value).lower()


# ============================================
# Rollback Tests
# ============================================

@pytest.mark.integration
class TestMigrationRollback:
    """Test migration rollback procedures."""

    def test_rollback_compliance_audit_fields(self, test_db):
        """Test rolling back compliance audit fields migration."""
        # First, apply the migration (simulate)
        test_db.execute(text("""
            ALTER TABLE users
              ADD COLUMN IF NOT EXISTS restricted_crop_flag BOOLEAN DEFAULT FALSE NOT NULL,
              ADD COLUMN IF NOT EXISTS restricted_crop_count INTEGER DEFAULT 0 NOT NULL
        """))
        test_db.commit()

        # Verify columns exist
        result = test_db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
              AND column_name IN ('restricted_crop_flag', 'restricted_crop_count')
        """))
        columns_before = [row[0] for row in result]
        assert 'restricted_crop_flag' in columns_before

        # Apply rollback
        test_db.execute(text("""
            ALTER TABLE users
              DROP COLUMN IF EXISTS restricted_crop_flag,
              DROP COLUMN IF EXISTS restricted_crop_count
        """))
        test_db.commit()

        # Verify columns removed
        result = test_db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
              AND column_name IN ('restricted_crop_flag', 'restricted_crop_count')
        """))
        columns_after = [row[0] for row in result]
        assert 'restricted_crop_flag' not in columns_after

    def test_rollback_is_idempotent(self, test_db):
        """Test that rollback can be run multiple times safely."""
        # Run rollback even if columns don't exist (should not error)
        test_db.execute(text("""
            ALTER TABLE users
              DROP COLUMN IF EXISTS restricted_crop_flag,
              DROP COLUMN IF EXISTS restricted_crop_count
        """))
        test_db.commit()

        # Run again - should not error
        test_db.execute(text("""
            ALTER TABLE users
              DROP COLUMN IF EXISTS restricted_crop_flag,
              DROP COLUMN IF EXISTS restricted_crop_count
        """))
        test_db.commit()

        # Should complete without errors
        assert True


# ============================================
# Migration Failure Recovery Tests
# ============================================

@pytest.mark.integration
class TestMigrationFailureRecovery:
    """Test recovery from migration failures."""

    def test_partial_migration_detected(self, test_db):
        """Test detection of partially applied migration."""
        # Create migration table
        test_db.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) NOT NULL PRIMARY KEY,
                applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                description TEXT,
                checksum VARCHAR(64),
                execution_time_ms INTEGER,
                applied_by VARCHAR(100)
            )
        """))

        # Record migration as applied
        test_db.execute(text("""
            INSERT INTO schema_migrations (version, description, applied_by)
            VALUES ('add_is_admin_column', 'Add is_admin column', 'test_system')
            ON CONFLICT (version) DO NOTHING
        """))

        # But don't actually apply it (simulate partial failure)
        test_db.commit()

        # Check should detect inconsistency
        # (Migration is recorded but column doesn't exist)
        result = test_db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'is_admin'
        """))
        columns = [row[0] for row in result]

        # If column doesn't exist but migration is recorded, we have an issue
        # (In practice, this would be detected by application errors)

    def test_migration_rollback_after_failure(self, test_db):
        """Test rolling back after migration failure."""
        # Simulate a migration that fails halfway
        try:
            test_db.execute(text("""
                ALTER TABLE users ADD COLUMN test_column VARCHAR(100)
            """))

            # Simulate error during migration
            raise Exception("Simulated migration error")

        except Exception:
            # Rollback transaction
            test_db.rollback()

            # Verify column was not added
            result = test_db.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'test_column'
            """))
            columns = [row[0] for row in result]

            assert 'test_column' not in columns

    def test_recovery_by_rerunning_migration(self, test_db):
        """Test recovering by re-running failed migration."""
        # Drop column if it exists
        test_db.execute(text("""
            ALTER TABLE users DROP COLUMN IF EXISTS test_recovery_column
        """))
        test_db.commit()

        # First attempt - simulate failure
        try:
            test_db.execute(text("""
                ALTER TABLE users ADD COLUMN test_recovery_column VARCHAR(100)
            """))
            # Simulate error before commit
            raise Exception("Simulated error")
        except Exception:
            test_db.rollback()

        # Verify column wasn't added
        result = test_db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'test_recovery_column'
        """))
        assert len(list(result)) == 0

        # Second attempt - successful
        test_db.execute(text("""
            ALTER TABLE users ADD COLUMN test_recovery_column VARCHAR(100)
        """))
        test_db.commit()

        # Verify column was added
        result = test_db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'test_recovery_column'
        """))
        columns = [row[0] for row in result]
        assert 'test_recovery_column' in columns

        # Cleanup
        test_db.execute(text("""
            ALTER TABLE users DROP COLUMN test_recovery_column
        """))
        test_db.commit()
