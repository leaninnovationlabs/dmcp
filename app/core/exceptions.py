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


class ToolNotFoundError(DBMCPException):
    """Raised when a tool is not found."""
    
    def __init__(self, tool_id: int):
        super().__init__(
            message=f"Tool with ID {tool_id} not found",
            status_code=404,
            details={"tool_id": tool_id}
        )


class DatabaseConnectionError(DBMCPException):
    """Raised when database connection fails."""
    
    def __init__(self, datasource_id: int, error: str):
        super().__init__(
            message=f"Failed to connect to datasource {datasource_id}: {error}",
            status_code=500,
            details={"datasource_id": datasource_id, "error": error}
        )


class ToolExecutionError(DBMCPException):
    """Raised when tool execution fails."""
    
    def __init__(self, tool_id: Optional[int], error: str):
        super().__init__(
            message=f"Tool execution failed: {error}",
            status_code=400,
            details={"tool_id": tool_id, "error": error}
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