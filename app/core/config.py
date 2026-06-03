import os
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV = os.getenv("ENV", "development")


class Settings(BaseSettings):
    """
    Centralized, strongly-typed configuration class using Pydantic Settings.
    Retrieves all values from OS environment variables and `.env` files automatically.
    Provides safe defaults for development and raises strict validation errors in production.
    """

    ENV: str = ENV
    PORT: int = 8000
    IP_ADDRESS: str = "127.0.0.1"

    APP_TITLE: str = "Enterprise CRM Backend"
    APP_DESCRIPTION: str = "High-performance, asynchronous REST API services built with FastAPI, SQLAlchemy 2.0, and Pydantic v2."
    APP_VERSION: str = "1.0.0"

    # Database and secrets (no hardcoding)
    DATABASE_URL: str | None = None
    JWT_SECRET_KEY: str | None = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_IN: str = "7d"
    SALT_ROUNDS: int = 12
    JWT_COOKIE_NAME: str = "access_token"

    # Mail parameters
    MAIL_HOST: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USER: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_SECURE: bool = False
    MAIL_FROM: str = ""

    # Cookies
    COOKIE_NAME: str = "access_token"
    COOKIE_MAX_AGE: int = 604800
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "Lax"
    COOKIE_SAME_SITE: str | None = None

    # Admin Credentials
    ADMIN_ID: str | None = "userId"
    ADMIN_NAME: str | None = "User Name"
    ADMIN_MAIL: str | None = "[EMAIL_ADDRESS]"
    ADMIN_PASSWORD: str | None = "password"

    # Tell Pydantic how to discover and parse the .env file automatically
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / f".env.{ENV}")
        if (BASE_DIR / f".env.{ENV}").exists()
        else str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """
        In production, require database URLs and secrets to be explicitly configured.
        In other environments, fall back to safe local development defaults.
        """
        if self.ENV == "production":
            if not self.DATABASE_URL:
                raise ValueError(
                    "DATABASE_URL must be explicitly configured in the production environment!"
                )
            if not self.JWT_SECRET_KEY:
                raise ValueError(
                    "JWT_SECRET_KEY must be explicitly configured in the production environment!"
                )
            self.COOKIE_SECURE = True
        else:
            if not self.DATABASE_URL:
                self.DATABASE_URL = (
                    "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
                )
            if not self.JWT_SECRET_KEY:
                self.JWT_SECRET_KEY = "dev-fallback-secret-never-use-in-prod-123456789"
            self.COOKIE_SECURE = False

        # Synchronize cookie same-site variable names
        if self.COOKIE_SAME_SITE:
            self.COOKIE_SAMESITE = self.COOKIE_SAME_SITE

        return self


# Global singleton configuration object instance
config = Settings()
