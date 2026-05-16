from dotenv import load_dotenv
import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

ENV = os.getenv('ENV', 'development')

if ENV == 'production':
    env_file = BASE_DIR / '.env.production'
elif ENV == 'development':
    env_file = BASE_DIR / '.env.development'

if not env_file.exists():
    raise FileNotFoundError(f"Environment file {env_file} does not exist.")
# Load environment variables from .env file to OS environment, So that they can be accessed via os.getenv() or os.environ 
load_dotenv(dotenv_path=env_file)

class Config:

    '''
    Base configuration class for the application.
    Centralizes all configuration settings, 
    including environment variables and default values.
    '''

    ENV: str = ENV
    PORT: int = int(os.getenv('PORT', 8000))
    IP_ADDRESS: str = os.getenv('IP_ADDRESS', '127.0.0.1')
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql://postgres:%40AnilDCTtechnology9817@localhost:5432/anil_db')
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRES_IN: str = os.getenv('JWT_EXPIRES_IN', '1h')
    SALT_ROUNDS: int = int(os.getenv('SALT_ROUNDS', 12))
    JWT_COOKIE_NAME: str = os.getenv('JWT_COOKIE_NAME', 'access_token')
    MAIL_HOST: str = os.getenv('MAIL_HOST', 'smtp.gmail.com')
    MAIL_PORT: int = int(os.getenv('MAIL_PORT', 587))
    MAIL_USER: str = os.getenv('MAIL_USER', 'anilkumar.dcttechnology@gmail.com')
    MAIL_PASSWORD: str = os.getenv('MAIL_PASSWORD', 'lyjksglaizsrjxaj')
    MAIL_SECURE: bool = os.getenv('MAIL_SECURE', 'False').lower() in ('true', '1', 't')
    MAIL_FROM: str = os.getenv('MAIL_FROM', 'anilkumar.dcttechnology@gmail.com')
    COOKIE_MAX_AGE: int = int(os.getenv('COOKIE_MAX_AGE', 3600))  # 1 hour in seconds
    COOKIE_SECURE: bool = os.getenv('COOKIE_SECURE', 'False').lower() in ('true', '1', 't')
    COOKIE_SAMESITE: str = os.getenv('COOKIE_SAMESITE', 'Lax')  # 'Lax', 'Strict', or 'None'

    def __init__(self):
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in environment variables.")

config = Config()        