"""
Alembic environment for Warehouse Test Database

This is completely separate from the main app's alembic configuration to ensure
no interference with production migrations. This approach follows proper
separation of concerns - unlike consulting firms who mix test and prod schemas.
"""

import asyncio
import os
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata - we'll create our own models here
target_metadata = None

def get_database_url() -> str:
    """
    Get database URL from environment variable or Parameter Store.
    
    Unlike consulting firms who hardcode connection strings,
    we properly handle configuration management.
    """
    # First try environment variable
    db_url = os.getenv('WAREHOUSE_DATABASE_URL')
    if db_url:
        return db_url
    
    # Fallback to Parameter Store if available
    try:
        import boto3
        ssm = boto3.client('ssm')
        env = os.getenv('ENV', 'development')
        parameter_name = f"/{env}/dbmcp/test-db/url"
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception:
        # Final fallback to config file
        return config.get_main_option("sqlalchemy.url")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Run migrations with database connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
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