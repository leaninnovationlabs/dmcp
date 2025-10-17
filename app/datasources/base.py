import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ResultWrapper:
    """Common result wrapper for all database connections."""

    def __init__(self, data: List[Dict[str, Any]], keys: List[str]):
        self.data = data
        self.keys = keys
        self.returns_rows = True

    async def fetchall(self) -> List[Dict[str, Any]]:
        return self.data

    async def fetchone(self) -> Optional[Dict[str, Any]]:
        return self.data[0] if self.data else None


class DatabaseConnection(ABC):
    """Base class for database connections."""

    def __init__(self, connection):
        self.connection = connection

    async def execute(
        self, sql: str, parameters: Dict[str, Any] = None
    ) -> ResultWrapper:
        """Execute a SQL query with parameters using template method pattern."""
        # Convert parameters to database-specific format
        converted_sql, param_values = self._convert_parameters(sql, parameters or {})

        # Execute the query (database-specific implementation)
        raw_result, columns = await self._execute_query(converted_sql, param_values)

        # Process results into common format
        data = self._process_results(raw_result, columns)

        return ResultWrapper(data, columns)

    @abstractmethod
    async def _execute_query(
        self, sql: str, param_values: List[Any]
    ) -> Tuple[Any, List[str]]:
        """Execute the actual query and return raw results and column names."""
        pass

    @abstractmethod
    def _convert_parameters(
        self, sql: str, parameters: Dict[str, Any]
    ) -> Tuple[str, List[Any]]:
        """Convert named parameters to database-specific format."""
        pass

    def _process_results(
        self, raw_result: Any, columns: List[str]
    ) -> List[Dict[str, Any]]:
        """Process raw results into list of dictionaries - can be overridden."""
        if raw_result and columns:
            if hasattr(raw_result, "__iter__") and not isinstance(
                raw_result, (str, bytes)
            ):
                # Handle different result formats
                if isinstance(raw_result[0], dict):
                    # Already dictionaries (PostgreSQL case)
                    return raw_result
                else:
                    # Tuples/lists that need to be converted to dicts
                    return [dict(zip(columns, row)) for row in raw_result]
        return []

    @abstractmethod
    async def close(self):
        """Close the database connection."""
        pass

    @classmethod
    @abstractmethod
    async def create(cls, datasource) -> "DatabaseConnection":
        """Factory method to create a connection from datasource configuration."""
        pass

    @classmethod
    def _handle_connection_error(cls, datasource, error: Exception):
        """Common error handling for connection creation."""
        logger.error(
            f"Failed to create {cls.__name__} for datasource {datasource.id}: {error}"
        )
        raise
