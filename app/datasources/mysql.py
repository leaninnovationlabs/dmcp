import aiomysql
from typing import Dict, Any
from urllib.parse import urlparse
import logging

from .base import DatabaseConnection
from ..models.database import Datasource

logger = logging.getLogger(__name__)


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

    @classmethod
    async def create(cls, datasource: Datasource) -> 'MySQLConnection':
        """Create a new MySQL connection."""
        try:
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
            return cls(connection)
        except Exception as e:
            logger.error(f"Failed to create MySQL connection for datasource {datasource.id}: {e}")
            raise 