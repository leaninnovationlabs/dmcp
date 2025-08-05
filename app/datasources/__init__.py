from .base import DatabaseConnection, ResultWrapper
from .postgresql import PostgreSQLConnection
from .mysql import MySQLConnection

# Registry of database connection classes
CONNECTION_REGISTRY = {
    'postgresql': PostgreSQLConnection,
    'mysql': MySQLConnection,
}

__all__ = [
    'DatabaseConnection',
    'ResultWrapper',
    'PostgreSQLConnection', 
    'MySQLConnection',
    'CONNECTION_REGISTRY'
]
