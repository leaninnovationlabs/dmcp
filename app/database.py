from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
from typing import AsyncGenerator

from .models.database import Base
from .core.config import settings


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initialize the database and create tables."""
    # Note: Database schema is now managed by Alembic
    # Run 'alembic upgrade head' to apply migrations
    # This function is kept for backward compatibility but doesn't create tables
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# For backward compatibility with sync operations if needed
def get_sync_db() -> Session:
    """Get a synchronous database session for operations that need it."""
    sync_url = settings.database_url.replace("+aiosqlite", "").replace("+asyncpg", "").replace("+aiomysql", "")
    sync_engine = create_engine(
        sync_url,
        echo=False,
    )
    SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
    return SyncSessionLocal() 