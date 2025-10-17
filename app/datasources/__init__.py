from .base import DatabaseConnection, ResultWrapper
from .databricks import DatabricksConnection
from .mysql import MySQLConnection
from .postgresql import PostgreSQLConnection
from .sqlite import SQLiteConnection

# Registry of database connection classes
CONNECTION_REGISTRY = {
    "postgresql": PostgreSQLConnection,
    "mysql": MySQLConnection,
    "sqlite": SQLiteConnection,
    "databricks": DatabricksConnection,
}

__all__ = [
    "DatabaseConnection",
    "ResultWrapper",
    "PostgreSQLConnection",
    "MySQLConnection",
    "SQLiteConnection",
    "DatabricksConnection",
    "CONNECTION_REGISTRY",
]
