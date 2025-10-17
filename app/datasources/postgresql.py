import logging
from typing import Any, Dict, List, Tuple

import asyncpg

from ..models.database import Datasource
from .base import DatabaseConnection

logger = logging.getLogger(__name__)


class PostgreSQLConnection(DatabaseConnection):
    def _convert_postgresql_types(self, value):
        """Convert PostgreSQL-specific types to JSON-serializable formats."""
        # Handle asyncpg BitString type
        if hasattr(value, "__class__") and "BitString" in str(type(value)):
            return str(value)

        # Handle other potential PostgreSQL types
        if hasattr(value, "__class__") and hasattr(value, "__module__"):
            module = getattr(value, "__module__", "")
            if "asyncpg" in module or "pgproto" in module:
                # Convert any other asyncpg-specific types to string
                return str(value)

        return value

    def _convert_record_to_dict(self, record):
        """Convert an asyncpg Record to a dictionary with type conversion."""
        return {
            key: self._convert_postgresql_types(value)
            for key, value in dict(record).items()
        }

    def _convert_parameters(
        self, sql: str, parameters: Dict[str, Any]
    ) -> Tuple[str, List[Any]]:
        """Convert named parameters to PostgreSQL positional parameters."""
        if not parameters:
            return sql, []

        # Replace named parameters with positional parameters
        param_keys = list(parameters.keys())
        for i, key in enumerate(param_keys):
            sql = sql.replace(f":{key}", f"${i + 1}")

        return sql, list(parameters.values())

    async def _execute_query(
        self, sql: str, param_values: List[Any]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Execute PostgreSQL query and return results with column names."""
        result = await self.connection.fetch(sql, *param_values)

        # Convert asyncpg Record objects to dictionaries with type conversion
        if result:
            data = [self._convert_record_to_dict(record) for record in result]
            keys = list(data[0].keys()) if data else []
        else:
            data = []
            keys = []

        return data, keys

    def _process_results(
        self, raw_result: List[Dict[str, Any]], columns: List[str]
    ) -> List[Dict[str, Any]]:
        """PostgreSQL results are already processed by _execute_query."""
        return raw_result

    async def close(self):
        """Close the PostgreSQL connection."""
        await self.connection.close()

    @classmethod
    async def create(cls, datasource: Datasource) -> "PostgreSQLConnection":
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
                    "host": datasource.host or "localhost",
                    "port": datasource.port or 5432,
                    "database": datasource.database,
                    "user": datasource.username,
                    "password": datasource.decrypted_password,
                }

                # Add SSL mode if specified
                if datasource.ssl_mode:
                    connection_params["ssl"] = datasource.ssl_mode

                # Add additional parameters
                if datasource.additional_params:
                    connection_params.update(datasource.additional_params)

                connection = await asyncpg.connect(**connection_params)

            return cls(connection)
        except Exception as e:
            cls._handle_connection_error(datasource, e)
