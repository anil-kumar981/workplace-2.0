from dotenv import load_dotenv
import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV = os.getenv('ENV', 'development')

# Load .env file ONLY if it exists locally (helpful for local dev)
env_file = BASE_DIR / f".env.{ENV}"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    root_env = BASE_DIR / ".env"
    if root_env.exists():
        load_dotenv(dotenv_path=root_env)

class Config:
    """
    Centralized configuration class.
    Retrieves all values from OS environment variables.
    Provides safe defaults for development and raises strict validation errors in production.
    """
    ENV: str = ENV
    PORT: int = int(os.getenv('PORT', 8000))
    IP_ADDRESS: str = os.getenv('IP_ADDRESS', '127.0.0.1')
    
    APP_TITLE: str = os.getenv('APP_TITLE', 'Enterprise CRM Backend')
    APP_DESCRIPTION: str = os.getenv('APP_DESCRIPTION', 'High-performance, asynchronous REST API services built with FastAPI, SQLAlchemy 2.0, and Pydantic v2.')
    APP_VERSION: str = os.getenv('APP_VERSION', '1.0.0')

    
    # Do not hardcode database URLs or secrets here.
    DATABASE_URL: str | None = os.getenv('DATABASE_URL') or (
        None if ENV == 'production' else 'postgresql+asyncpg://postgres:postgres@localhost:5432/postgres'
    )
    
    JWT_SECRET_KEY: str | None = os.getenv('JWT_SECRET_KEY') or (
        None if ENV == 'production' else 'dev-fallback-secret-never-use-in-prod-123456789'
    )
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRES_IN: str = os.getenv('JWT_EXPIRES_IN', '1h')
    SALT_ROUNDS: int = int(os.getenv('SALT_ROUNDS', 12))
    JWT_COOKIE_NAME: str = os.getenv('JWT_COOKIE_NAME', 'access_token')
    
    # Mail parameters
    MAIL_HOST: str = os.getenv('MAIL_HOST', 'smtp.gmail.com')
    MAIL_PORT: int = int(os.getenv('MAIL_PORT', 587))
    MAIL_USER: str = os.getenv('MAIL_USER', '')
    MAIL_PASSWORD: str = os.getenv('MAIL_PASSWORD', '')
    MAIL_SECURE: bool = os.getenv('MAIL_SECURE', 'False').lower() in ('true', '1', 't')
    MAIL_FROM: str = os.getenv('MAIL_FROM', '')
    
    # Cookies
    COOKIE_MAX_AGE: int = int(os.getenv('COOKIE_MAX_AGE', 3600))
    COOKIE_SECURE: bool = os.getenv('COOKIE_SECURE', 'False').lower() in ('true', '1', 't')
    COOKIE_SAMESITE: str = os.getenv('COOKIE_SAMESITE', 'Lax')

    def __init__(self):
        # In production, require environment variables to be explicitly set
        if self.ENV == 'production':
            if not self.DATABASE_URL:
                raise ValueError("DATABASE_URL must be explicitly configured in the production environment!")
            if not self.JWT_SECRET_KEY:
                raise ValueError("JWT_SECRET_KEY must be explicitly configured in the production environment!")
        else:
            if not self.DATABASE_URL:
                raise ValueError("DATABASE_URL must be configured.")

config = Config()