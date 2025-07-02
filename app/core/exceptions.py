from fastapi import HTTPException
from typing import Any, Dict, Optional


class DBMCPException(Exception):
    """Base exception for DBMCP application."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DatasourceNotFoundError(DBMCPException):
    """Raised when a datasource is not found."""
    
    def __init__(self, datasource_id: int):
        super().__init__(
            message=f"Datasource with ID {datasource_id} not found",
            status_code=404,
            details={"datasource_id": datasource_id}
        )


class QueryNotFoundError(DBMCPException):
    """Raised when a query is not found."""
    
    def __init__(self, query_id: int):
        super().__init__(
            message=f"Query with ID {query_id} not found",
            status_code=404,
            details={"query_id": query_id}
        )


class DatabaseConnectionError(DBMCPException):
    """Raised when database connection fails."""
    
    def __init__(self, datasource_id: int, error: str):
        super().__init__(
            message=f"Failed to connect to datasource {datasource_id}: {error}",
            status_code=500,
            details={"datasource_id": datasource_id, "error": error}
        )


class QueryExecutionError(DBMCPException):
    """Raised when query execution fails."""
    
    def __init__(self, query_id: Optional[int], error: str):
        super().__init__(
            message=f"Query execution failed: {error}",
            status_code=400,
            details={"query_id": query_id, "error": error}
        )


class ValidationError(DBMCPException):
    """Raised when data validation fails."""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation error in field '{field}': {message}",
            status_code=422,
            details={"field": field, "message": message}
        )


def handle_dbmcp_exception(exc: DBMCPException) -> HTTPException:
    """Convert DBMCP exceptions to FastAPI HTTP exceptions."""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            "details": exc.details
        }
    ) 