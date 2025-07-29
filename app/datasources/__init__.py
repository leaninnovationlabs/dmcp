from .base import DatabaseConnection, ResultWrapper
from .postgresql import PostgreSQLConnection
from .mysql import MySQLConnection
from .sqlite import SQLiteConnection

# Registry of database connection classes
CONNECTION_REGISTRY = {
    'postgresql': PostgreSQLConnection,
    'mysql': MySQLConnection,
    'sqlite': SQLiteConnection,
}

__all__ = [
    'DatabaseConnection',
    'ResultWrapper',
    'PostgreSQLConnection', 
    'MySQLConnection',
    'SQLiteConnection',
    'CONNECTION_REGISTRY'
] 