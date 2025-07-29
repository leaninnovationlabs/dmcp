import asyncpg
from typing import Dict, Any
from urllib.parse import urlparse
import logging

from .base import DatabaseConnection
from ..models.database import Datasource

logger = logging.getLogger(__name__)


class PostgreSQLConnection(DatabaseConnection):
    def __init__(self, connection):
        self.connection = connection
    
    def _convert_postgresql_types(self, value):
        """Convert PostgreSQL-specific types to JSON-serializable formats."""
        # Handle asyncpg BitString type
        if hasattr(value, '__class__') and 'BitString' in str(type(value)):
            return str(value)
        
        # Handle other potential PostgreSQL types
        if hasattr(value, '__class__') and hasattr(value, '__module__'):
            module = getattr(value, '__module__', '')
            if 'asyncpg' in module or 'pgproto' in module:
                # Convert any other asyncpg-specific types to string
                return str(value)
        
        return value
    
    def _convert_record_to_dict(self, record):
        """Convert an asyncpg Record to a dictionary with type conversion."""
        return {
            key: self._convert_postgresql_types(value) 
            for key, value in dict(record).items()
        }
    
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
        
        # Convert asyncpg Record objects to dictionaries with type conversion
        if result:
            # Convert each Record to dict with proper type handling
            data = [self._convert_record_to_dict(record) for record in result]
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

    @classmethod
    async def create(cls, datasource: Datasource) -> 'PostgreSQLConnection':
        """Create a new PostgreSQL connection."""
        try:
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
            
            return cls(connection)
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL connection for datasource {datasource.id}: {e}")
            raise 