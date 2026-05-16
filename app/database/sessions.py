from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from .base import Base
from app.core import config

# Create an asynchronous engine using the database URL from the configuration
engine = create_async_engine(config.DATABASE_URL, echo=True)

# Create an asynchronous session factory
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)





