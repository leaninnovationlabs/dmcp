from .base import DatabaseConnection, ResultWrapper
from .postgresql import PostgreSQLConnection
from .mysql import MySQLConnection
from .sqlite import SQLiteConnection
from .databricks import DatabricksConnection

# Registry of database connection classes
CONNECTION_REGISTRY = {
    'postgresql': PostgreSQLConnection,
    'mysql': MySQLConnection,
    'sqlite': SQLiteConnection,
    'databricks': DatabricksConnection,
}

__all__ = [
    'DatabaseConnection',
    'ResultWrapper',
    'PostgreSQLConnection', 
    'MySQLConnection',
    'SQLiteConnection',
    'DatabricksConnection',
    'CONNECTION_REGISTRY'
] 