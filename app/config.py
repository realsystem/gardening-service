"""Application configuration"""
import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Environment
    APP_ENV: str = "local"  # local, docker, test, production

    # Database
    DATABASE_URL: str = "postgresql://gardener:password@localhost:5432/gardening_db"

    @field_validator('DATABASE_URL')
    @classmethod
    def convert_postgres_to_postgresql(cls, v: str) -> str:
        """Convert postgres:// to postgresql:// for SQLAlchemy 2.0 compatibility.

        Fly.io Postgres sets DATABASE_URL with postgres:// scheme,
        but SQLAlchemy 2.0 requires postgresql:// scheme.
        """
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 1 week

    # Application
    APP_NAME: str = "Gardening Helper Service"
    DEBUG: bool = True

    # Feature Flags (runtime toggles for production safety)
    FEATURE_RULE_ENGINE_ENABLED: bool = True
    FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED: bool = True
    FEATURE_OPTIMIZATION_ENGINES_ENABLED: bool = True

    class Config:
        # Auto-detect environment-specific .env file
        # Priority: .env.{APP_ENV} > .env > defaults
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

    @classmethod
    def load_env_file(cls):
        """Determine which .env file to load based on APP_ENV"""
        app_env = os.getenv("APP_ENV", "local")
        env_file = f".env.{app_env}"
        if os.path.exists(env_file):
            return env_file
        elif os.path.exists(".env"):
            return ".env"
        return None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    env_file = Settings.load_env_file()
    if env_file:
        return Settings(_env_file=env_file)
    return Settings()
