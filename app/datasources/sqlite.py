import aiosqlite
from typing import Dict, Any
import logging

from .base import DatabaseConnection
from ..models.database import Datasource

logger = logging.getLogger(__name__)


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

    @classmethod
    async def create(cls, datasource: Datasource) -> 'SQLiteConnection':
        """Create a new SQLite connection."""
        try:
            if datasource.connection_string:
                # Extract database path from connection string
                if datasource.connection_string.startswith('sqlite:///'):
                    db_path = datasource.connection_string[10:]  # Remove 'sqlite:///' prefix
                else:
                    db_path = datasource.database
            else:
                db_path = datasource.database
            
            connection = await aiosqlite.connect(db_path)
            return cls(connection)
        except Exception as e:
            logger.error(f"Failed to create SQLite connection for datasource {datasource.id}: {e}")
            raise 