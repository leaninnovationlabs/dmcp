import logging
from typing import Any, Dict, List, Tuple

import aiosqlite

from ..models.database import Datasource
from .base import DatabaseConnection

logger = logging.getLogger(__name__)


class SQLiteConnection(DatabaseConnection):
    def _convert_parameters(
        self, sql: str, parameters: Dict[str, Any]
    ) -> Tuple[str, List[Any]]:
        """Convert named parameters to SQLite ? placeholders."""
        if not parameters:
            return sql, []

        # SQLite uses ? for parameter placeholders
        for key in parameters.keys():
            sql = sql.replace(f":{key}", "?")

        return sql, list(parameters.values())

    async def _execute_query(
        self, sql: str, param_values: List[Any]
    ) -> Tuple[List[Tuple], List[str]]:
        """Execute SQLite query and return results with column names."""
        cursor = await self.connection.execute(sql, param_values)
        result = await cursor.fetchall()

        # Get column names from cursor description
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        return result, columns

    async def close(self):
        """Close the SQLite connection."""
        await self.connection.close()

    @classmethod
    async def create(cls, datasource: Datasource) -> "SQLiteConnection":
        """Create a new SQLite connection."""
        try:
            if datasource.connection_string:
                # Extract database path from connection string
                if datasource.connection_string.startswith("sqlite:///"):
                    db_path = datasource.connection_string[
                        10:
                    ]  # Remove 'sqlite:///' prefix
                else:
                    db_path = datasource.database
            else:
                db_path = datasource.database

            connection = await aiosqlite.connect(db_path)
            return cls(connection)
        except Exception as e:
            cls._handle_connection_error(datasource, e)
