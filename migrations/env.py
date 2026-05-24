import os
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

__all__ = ["async_engine_from_config"]

# Strip system-wide PGSSLMODE environment variable if present on the host.
# asyncpg does not support sslmode as a direct connection keyword argument.
os.environ.pop("PGSSLMODE", None)

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.database.base import Base
from app.models import User, Role, Permission, role_permissions
from app.core.config import config as app_config
from sqlalchemy.ext.asyncio import create_async_engine

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

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


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    cleaned_url, _ = get_async_engine_args(app_config.DATABASE_URL)
    context.configure(
        url=cleaned_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    cleaned_url, connect_args = get_async_engine_args(app_config.DATABASE_URL)
    connectable = create_async_engine(
        cleaned_url,
        connect_args=connect_args,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
