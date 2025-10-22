from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from .core.config import settings

# Create async engine for FastAPI routes (with connection pooling)
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)

# Create async session factory for FastAPI
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create a separate engine for MCP tools that works across event loops
# Using NullPool to avoid connection pool issues across loops
mcp_engine = create_async_engine(
    settings.database_url,
    echo=False,
    poolclass=NullPool,  # No connection pooling to avoid loop binding
)

# Create async session factory for MCP (works across event loops)
MCPSessionLocal = async_sessionmaker(
    mcp_engine,
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


# Create a new get db function for mcp server
async def get_mcp_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session for MCP server."""
    async with MCPSessionLocal() as session:
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
    SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)  # noqa: N806
    return SyncSessionLocal()
