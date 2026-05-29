import os
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from .base import Base
from app.core import config

# Strip system-wide PGSSLMODE environment variable if present on the host.
# asyncpg does not support sslmode as a direct connection keyword argument.
os.environ.pop("PGSSLMODE", None)

def get_async_engine_args(database_url: str):
    """
    Format connection URL and return (cleaned_url, connect_args) for asyncpg.
    Strips 'sslmode' query parameter and converts to asyncpg-compliant ssl=True.
    """
    if not database_url:
        return database_url, {}
    connect_args = {}
    cleaned_url = database_url
    if "sslmode=" in database_url:
        parsed = urlparse(database_url)
        query_params = parse_qs(parsed.query)
        sslmode = query_params.pop("sslmode", None)
        if sslmode and sslmode[0] in ("require", "prefer", "allow", "verify-ca", "verify-full"):
            connect_args["ssl"] = True
        new_query = urlencode(query_params, doseq=True)
        cleaned_url = urlunparse(parsed._replace(query=new_query))
    return cleaned_url, connect_args

# Format the database URL and fetch connection args
cleaned_url, connect_args = get_async_engine_args(config.DATABASE_URL)

# Create an asynchronous engine using the database URL from the configuration
engine = create_async_engine(cleaned_url, connect_args=connect_args, echo=True)

# Create an asynchronous session factory
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency provider for database session context.
    """
    async with async_session() as session:
        yield session





