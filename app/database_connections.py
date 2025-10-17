import asyncio
import logging
from typing import Dict

from .datasources import CONNECTION_REGISTRY, DatabaseConnection
from .models.database import Datasource

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """Manages database connections for different database types."""

    def __init__(self):
        self._connections: Dict[int, DatabaseConnection] = {}
        self._lock = None
    
    def _get_lock(self) -> asyncio.Lock:
        """Get or create a lock for the current event loop."""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
    
    async def get_connection(self, datasource: Datasource) -> DatabaseConnection:
        """Get or create a database connection for the given datasource."""
        async with self._get_lock():
            if datasource.id in self._connections:
                return self._connections[datasource.id]

            connection = await self._create_connection(datasource)
            self._connections[datasource.id] = connection
            return connection

    async def _create_connection(self, datasource: Datasource) -> DatabaseConnection:
        """Create a new database connection based on the datasource configuration."""
        try:
            # Get the connection class from the registry
            database_type_str = datasource.database_type.lower()
            connection_class = CONNECTION_REGISTRY.get(database_type_str)

            if not connection_class:
                raise ValueError(
                    f"Unsupported database type: {datasource.database_type}"
                )

            # Use the create class method to instantiate the connection
            return await connection_class.create(datasource)

        except Exception as e:
            logger.error(
                f"Failed to create connection for datasource {datasource.id}: {e}"
            )
            raise

    async def close_connection(self, datasource_id: int):
        """Close a specific database connection."""
        async with self._get_lock():
            if datasource_id in self._connections:
                await self._connections[datasource_id].close()
                del self._connections[datasource_id]

    async def close_all_connections(self):
        """Close all database connections."""
        async with self._get_lock():
            for connection in self._connections.values():
                await connection.close()
            self._connections.clear()
