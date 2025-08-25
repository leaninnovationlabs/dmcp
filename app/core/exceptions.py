from fastapi import HTTPException
from typing import Any, Dict, Optional


class DMCPException(Exception):
    """Base exception for DMCP application."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DatasourceNotFoundError(DMCPException):
    """Raised when a datasource is not found."""
    
    def __init__(self, datasource_id: int):
        super().__init__(
            message=f"Datasource with ID {datasource_id} not found",
            status_code=404,
            details={"datasource_id": datasource_id}
        )


class ToolNotFoundError(DMCPException):
    """Raised when a tool is not found."""
    
    def __init__(self, tool_id: int):
        super().__init__(
            message=f"Tool with ID {tool_id} not found",
            status_code=404,
            details={"tool_id": tool_id}
        )


class DatabaseConnectionError(DMCPException):
    """Raised when database connection fails."""
    
    def __init__(self, datasource_id: int, error: str):
        super().__init__(
            message=f"Failed to connect to datasource {datasource_id}: {error}",
            status_code=500,
            details={"datasource_id": datasource_id, "error": error}
        )


class ToolExecutionError(DMCPException):
    """Raised when tool execution fails."""
    
    def __init__(self, tool_id: Optional[int], error: str):
        super().__init__(
            message=f"Tool execution failed: {error}",
            status_code=400,
            details={"tool_id": tool_id, "error": error}
        )


class ValidationError(DMCPException):
    """Raised when data validation fails."""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation error in field '{field}': {message}",
            status_code=422,
            details={"field": field, "message": message}
        )


class AuthenticationError(DMCPException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=401,
            details={"error": "authentication_failed"}
        )


def handle_dmcp_exception(exc: DMCPException) -> HTTPException:
    """Convert DMCP exceptions to FastAPI HTTP exceptions using standardized error detail."""
    # Shape detail so global handler can produce StandardAPIResponse
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "success": False,
            "errors": [{"msg": exc.message}],
            "details": exc.details,
        }
    )