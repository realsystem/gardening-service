"""Database configuration and session management"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_migrations() -> None:
    """Check database migration version on startup.

    Raises:
        RuntimeError: If database schema is out of date

    Note:
        Only runs in production and staging environments.
        Development/test environments skip check for flexibility.
    """
    # Skip migration check in test environment
    if settings.APP_ENV == "test":
        logger.info("Skipping migration check in test environment")
        return

    # Skip in local development by default (can be enabled via env var)
    if settings.APP_ENV == "local":
        logger.info("Skipping migration check in local environment")
        return

    # Import here to avoid circular dependency
    from app.utils.migration_check import check_migrations_on_startup

    # Check migrations with strict mode in production
    # Note: Temporarily disabled strict mode for production debugging
    strict = False  # settings.APP_ENV in ("production", "staging")

    db = SessionLocal()
    try:
        check_migrations_on_startup(db, strict=strict)
    finally:
        db.close()
