import asyncio
from typing import Dict, Any, Optional
import asyncpg
import aiomysql
import aiosqlite
from urllib.parse import urlparse
import logging

from .models.database import Datasource
from .models.schemas import DatabaseType

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Base class for database connections."""
    
    async def execute(self, sql: str, parameters: Dict[str, Any] = None):
        """Execute a SQL query with parameters."""
        raise NotImplementedError
    
    async def close(self):
        """Close the database connection."""
        raise NotImplementedError


class PostgreSQLConnection(DatabaseConnection):
    def __init__(self, connection):
        self.connection = connection
    
    async def execute(self, sql: str, parameters: Dict[str, Any] = None):
        """Execute a SQL query with parameters."""
        # Convert parameters to PostgreSQL format
        if parameters:
            # Replace named parameters with positional parameters
            for key, value in parameters.items():
                sql = sql.replace(f":{key}", f"${list(parameters.keys()).index(key) + 1}")
            param_values = list(parameters.values())
        else:
            param_values = []
        
        result = await self.connection.fetch(sql, *param_values)
        
        # Convert asyncpg Record objects to dictionaries
        if result:
            # Convert each Record to dict
            data = [dict(record) for record in result]
            keys = list(data[0].keys()) if data else []
        else:
            data = []
            keys = []
        
        # Create a result object that mimics the expected interface
        class ResultWrapper:
            def __init__(self, data, keys):
                self.data = data
                self.keys = keys
                self.returns_rows = True
            
            async def fetchall(self):
                return self.data
            
            async def fetchone(self):
                return self.data[0] if self.data else None
        
        return ResultWrapper(data, keys)
    
    async def close(self):
        """Close the PostgreSQL connection."""
        await self.connection.close()


class MySQLConnection(DatabaseConnection):
    def __init__(self, connection):
        self.connection = connection
    
    async def execute(self, sql: str, parameters: Dict[str, Any] = None):
        """Execute a SQL query with parameters."""
        async with self.connection.cursor() as cursor:
            if parameters:
                # MySQL uses %s for parameter placeholders
                for key, value in parameters.items():
                    sql = sql.replace(f":{key}", "%s")
                param_values = list(parameters.values())
            else:
                param_values = []
            
            await cursor.execute(sql, param_values)
            result = await cursor.fetchall()
            
            # Get column names from cursor description
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Convert raw tuples to dictionaries
            if result and columns:
                data = [dict(zip(columns, row)) for row in result]
            else:
                data = []
            
            # Create a result object that mimics the expected interface
            class ResultWrapper:
                def __init__(self, data, keys):
                    self.data = data
                    self.keys = keys
                    self.returns_rows = True
                
                async def fetchall(self):
                    return self.data
                
                async def fetchone(self):
                    return self.data[0] if self.data else None
            
            return ResultWrapper(data, columns)
    
    async def close(self):
        """Close the MySQL connection."""
        self.connection.close()
        await self.connection.wait_closed()


class SQLiteConnection(DatabaseConnection):
    def __init__(self, connection):
        self.connection = connection
    
    async def execute(self, sql: str, parameters: Dict[str, Any] = None):
        """Execute a SQL query with parameters."""
        if parameters:
            # SQLite uses ? for parameter placeholders
            for key, value in parameters.items():
                sql = sql.replace(f":{key}", "?")
            param_values = list(parameters.values())
        else:
            param_values = []
        
        cursor = await self.connection.execute(sql, param_values)
        result = await cursor.fetchall()
        
        # Get column names from cursor description
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Convert raw tuples to dictionaries
        if result and columns:
            data = [dict(zip(columns, row)) for row in result]
        else:
            data = []
        
        # Create a result object that mimics the expected interface
        class ResultWrapper:
            def __init__(self, data, keys):
                self.data = data
                self.keys = keys
                self.returns_rows = True
            
            async def fetchall(self):
                return self.data
            
            async def fetchone(self):
                return self.data[0] if self.data else None
        
        return ResultWrapper(data, columns)
    
    async def close(self):
        """Close the SQLite connection."""
        await self.connection.close()


class DatabaseConnectionManager:
    """Manages database connections for different database types."""
    
    def __init__(self):
        self._connections: Dict[int, DatabaseConnection] = {}
        self._lock = asyncio.Lock()
    
    async def get_connection(self, datasource: Datasource) -> DatabaseConnection:
        """Get or create a database connection for the given datasource."""
        async with self._lock:
            if datasource.id in self._connections:
                return self._connections[datasource.id]
            
            connection = await self._create_connection(datasource)
            self._connections[datasource.id] = connection
            return connection
    
    async def _create_connection(self, datasource: Datasource) -> DatabaseConnection:
        """Create a new database connection based on the datasource configuration."""
        try:
            if datasource.database_type == DatabaseType.POSTGRESQL:
                return await self._create_postgresql_connection(datasource)
            elif datasource.database_type == DatabaseType.MYSQL:
                return await self._create_mysql_connection(datasource)
            elif datasource.database_type == DatabaseType.SQLITE:
                return await self._create_sqlite_connection(datasource)
            else:
                raise ValueError(f"Unsupported database type: {datasource.database_type}")
        except Exception as e:
            logger.error(f"Failed to create connection for datasource {datasource.id}: {e}")
            raise
    
    async def _create_postgresql_connection(self, datasource: Datasource) -> PostgreSQLConnection:
        """Create a PostgreSQL connection."""
        if datasource.connection_string:
            # Use connection string if provided
            # Note: Connection strings with passwords should be handled carefully
            # The password in connection string should be encrypted if stored
            connection = await asyncpg.connect(datasource.connection_string)
        else:
            # Build connection parameters
            connection_params = {
                'host': datasource.host or 'localhost',
                'port': datasource.port or 5432,
                'database': datasource.database,
                'user': datasource.username,
                'password': datasource.decrypted_password,
            }

            # Add SSL mode if specified
            if datasource.ssl_mode:
                connection_params['ssl'] = datasource.ssl_mode
            
            # Add additional parameters
            if datasource.additional_params:
                connection_params.update(datasource.additional_params)
            
            connection = await asyncpg.connect(**connection_params)
        
        return PostgreSQLConnection(connection)
    
    async def _create_mysql_connection(self, datasource: Datasource) -> MySQLConnection:
        """Create a MySQL connection."""
        if datasource.connection_string:
            # Parse connection string
            parsed = urlparse(datasource.connection_string)
            connection_params = {
                'host': parsed.hostname or 'localhost',
                'port': parsed.port or 3306,
                'user': parsed.username or datasource.username,
                'password': parsed.password or datasource.password,
                'db': datasource.database,
            }
        else:
            connection_params = {
                'host': datasource.host or 'localhost',
                'port': datasource.port or 3306,
                'user': datasource.username,
                'password': datasource.decrypted_password,
                'db': datasource.database,
            }
        
        # Add additional parameters
        if datasource.additional_params:
            connection_params.update(datasource.additional_params)
        
        connection = await aiomysql.connect(**connection_params)
        return MySQLConnection(connection)
    
    async def _create_sqlite_connection(self, datasource: Datasource) -> SQLiteConnection:
        """Create a SQLite connection."""
        if datasource.connection_string:
            # Extract database path from connection string
            if datasource.connection_string.startswith('sqlite:///'):
                db_path = datasource.connection_string[10:]  # Remove 'sqlite:///' prefix
            else:
                db_path = datasource.database
        else:
            db_path = datasource.database
        
        connection = await aiosqlite.connect(db_path)
        return SQLiteConnection(connection)
    
    async def close_connection(self, datasource_id: int):
        """Close a specific database connection."""
        async with self._lock:
            if datasource_id in self._connections:
                await self._connections[datasource_id].close()
                del self._connections[datasource_id]
    
    async def close_all_connections(self):
        """Close all database connections."""
        async with self._lock:
            for connection in self._connections.values():
                await connection.close()
            self._connections.clear() 