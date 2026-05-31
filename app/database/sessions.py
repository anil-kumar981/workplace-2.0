import os
from typing import AsyncGenerator
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core import config

from .base import Base

__all__ = ["Base"]

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
        if sslmode and sslmode[0] in (
            "require",
            "prefer",
            "allow",
            "verify-ca",
            "verify-full",
        ):
            connect_args["ssl"] = True
        new_query = urlencode(query_params, doseq=True)
        cleaned_url = urlunparse(parsed._replace(query=new_query))
    return cleaned_url, connect_args


# Format the database URL and fetch connection args
cleaned_url, connect_args = get_async_engine_args(config.DATABASE_URL)

# Create an asynchronous engine using the database URL from the configuration
engine = create_async_engine(
    cleaned_url,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,  # Checks connection liveness before every query
    pool_size=10,  # Keeps up to 10 connections always warm and open in memory
    max_overflow=20,  # Scales up to +20 connections if load is high
    pool_recycle=300,  # Recycles connections every 5 minutes (prevents Neon timeouts)
)

# Create an asynchronous session factory
async_session = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency provider for database session context.
    """
    async with async_session() as session:
        yield session
