from typing import Dict, Any


class DatabaseConnection:
    """Base class for database connections."""
    
    async def execute(self, sql: str, parameters: Dict[str, Any] = None):
        """Execute a SQL query with parameters."""
        raise NotImplementedError
    
    async def close(self):
        """Close the database connection."""
        raise NotImplementedError 