import aiomysql
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse
import logging

from .base import DatabaseConnection
from ..models.database import Datasource

logger = logging.getLogger(__name__)


class MySQLConnection(DatabaseConnection):
    
    def _convert_parameters(self, sql: str, parameters: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """Convert named parameters to MySQL %s placeholders."""
        if not parameters:
            return sql, []
        
        # MySQL uses %s for parameter placeholders
        for key in parameters.keys():
            sql = sql.replace(f":{key}", "%s")
        
        return sql, list(parameters.values())
    
    async def _execute_query(self, sql: str, param_values: List[Any]) -> Tuple[List[Tuple], List[str]]:
        """Execute MySQL query and return results with column names."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(sql, param_values)
            result = await cursor.fetchall()
            
            # Get column names from cursor description
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            return result, columns
    
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
            cls._handle_connection_error(datasource, e) 