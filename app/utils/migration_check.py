"""Migration version checking and validation.

Ensures database schema matches application code expectations.
Provides fail-fast behavior on version mismatch to prevent data corruption.
"""
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class MigrationVersion:
    """Represents a migration version with metadata."""

    def __init__(
        self,
        version: str,
        description: str,
        file_path: Optional[Path] = None
    ):
        self.version = version
        self.description = description
        self.file_path = file_path
        self.checksum = self._calculate_checksum() if file_path else None

    def _calculate_checksum(self) -> Optional[str]:
        """Calculate SHA256 checksum of migration file."""
        if not self.file_path or not self.file_path.exists():
            return None

        with open(self.file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def __repr__(self):
        return f"MigrationVersion(version={self.version}, description={self.description})"


class MigrationChecker:
    """Checks database migration version against expected state."""

    # Expected migrations (in order)
    EXPECTED_MIGRATIONS = [
        MigrationVersion("000", "Create migration version table"),
        MigrationVersion("001", "Add critical constraints"),
        MigrationVersion("002", "Add high priority constraints"),
        MigrationVersion("003", "Add check constraints"),
        MigrationVersion("add_compliance_audit_fields", "Add compliance audit fields to users"),
        MigrationVersion("add_is_admin_column", "Add is_admin column"),
        MigrationVersion("add_nutrient_profiles", "Add nutrient profile fields"),
    ]

    @staticmethod
    def check_migration_version(db: Session, strict: bool = True) -> Tuple[bool, List[str]]:
        """Check if database migration version matches expected state.

        Args:
            db: Database session
            strict: If True, fail on any version mismatch
                   If False, only warn on mismatch

        Returns:
            Tuple of (is_valid, error_messages)
            is_valid: True if migrations are up to date
            error_messages: List of validation errors/warnings

        Raises:
            RuntimeError: If strict=True and version mismatch detected
        """
        errors = []

        # Check if migration table exists
        try:
            result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'schema_migrations'
                )
            """))
            table_exists = result.scalar()

            if not table_exists:
                error = "Migration version table does not exist. Database may not be initialized."
                errors.append(error)

                if strict:
                    logger.error(error)
                    raise RuntimeError(
                        "Database migration table not found. "
                        "Run migrations before starting the application."
                    )
                else:
                    logger.warning(error)
                    return False, errors

        except Exception as e:
            error = f"Failed to check migration table: {str(e)}"
            errors.append(error)

            if strict:
                logger.error(error)
                raise RuntimeError(f"Database migration check failed: {str(e)}")
            else:
                logger.warning(error)
                return False, errors

        # Get applied migrations
        try:
            result = db.execute(text("""
                SELECT version, description, applied_at, checksum
                FROM schema_migrations
                ORDER BY applied_at
            """))
            applied_migrations = {
                row[0]: {
                    'description': row[1],
                    'applied_at': row[2],
                    'checksum': row[3]
                }
                for row in result
            }

        except Exception as e:
            error = f"Failed to query applied migrations: {str(e)}"
            errors.append(error)

            if strict:
                logger.error(error)
                raise RuntimeError(f"Failed to read migration history: {str(e)}")
            else:
                logger.warning(error)
                return False, errors

        # Check for missing expected migrations
        missing_migrations = []
        for expected_migration in MigrationChecker.EXPECTED_MIGRATIONS:
            if expected_migration.version not in applied_migrations:
                missing_migrations.append(expected_migration.version)

        if missing_migrations:
            error = f"Missing required migrations: {', '.join(missing_migrations)}"
            errors.append(error)

            if strict:
                logger.error(error)
                raise RuntimeError(
                    f"Database schema is outdated. Missing migrations: {', '.join(missing_migrations)}. "
                    "Please run pending migrations before starting the application."
                )
            else:
                logger.warning(error)

        # Check for unexpected migrations (applied but not expected)
        unexpected_migrations = []
        for applied_version in applied_migrations:
            if not any(m.version == applied_version for m in MigrationChecker.EXPECTED_MIGRATIONS):
                unexpected_migrations.append(applied_version)

        if unexpected_migrations:
            error = f"Unexpected migrations found: {', '.join(unexpected_migrations)}"
            errors.append(error)
            logger.warning(error)

        # Log success if no errors
        if not errors:
            logger.info(
                f"Database migration version check passed. "
                f"Applied migrations: {len(applied_migrations)}"
            )

        return len(errors) == 0, errors

    @staticmethod
    def get_migration_status(db: Session) -> Dict[str, any]:
        """Get detailed migration status.

        Returns:
            Dictionary with migration status information
        """
        try:
            # Check if table exists
            result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'schema_migrations'
                )
            """))
            table_exists = result.scalar()

            if not table_exists:
                return {
                    'initialized': False,
                    'applied_migrations': [],
                    'expected_migrations': [m.version for m in MigrationChecker.EXPECTED_MIGRATIONS],
                    'missing_migrations': [m.version for m in MigrationChecker.EXPECTED_MIGRATIONS],
                    'error': 'Migration table does not exist'
                }

            # Get applied migrations
            result = db.execute(text("""
                SELECT version, description, applied_at, checksum
                FROM schema_migrations
                ORDER BY applied_at
            """))
            applied_migrations = [
                {
                    'version': row[0],
                    'description': row[1],
                    'applied_at': row[2].isoformat() if row[2] else None,
                    'checksum': row[3]
                }
                for row in result
            ]

            applied_versions = {m['version'] for m in applied_migrations}
            expected_versions = {m.version for m in MigrationChecker.EXPECTED_MIGRATIONS}

            missing_migrations = expected_versions - applied_versions
            unexpected_migrations = applied_versions - expected_versions

            return {
                'initialized': True,
                'applied_migrations': applied_migrations,
                'expected_migrations': [m.version for m in MigrationChecker.EXPECTED_MIGRATIONS],
                'missing_migrations': list(missing_migrations),
                'unexpected_migrations': list(unexpected_migrations),
                'up_to_date': len(missing_migrations) == 0
            }

        except Exception as e:
            logger.error(f"Failed to get migration status: {str(e)}")
            return {
                'initialized': False,
                'error': str(e)
            }


def check_migrations_on_startup(db: Session, strict: bool = True) -> None:
    """Check migrations on application startup.

    Args:
        db: Database session
        strict: If True, fail on version mismatch (recommended for production)

    Raises:
        RuntimeError: If strict=True and migrations are out of date
    """
    logger.info("Checking database migration version...")

    is_valid, errors = MigrationChecker.check_migration_version(db, strict=strict)

    if not is_valid and errors:
        logger.error(
            f"Database migration check failed: {', '.join(errors)}"
        )

        if strict:
            # Already raised RuntimeError in check_migration_version
            pass
    else:
        logger.info("Database migration check passed")
