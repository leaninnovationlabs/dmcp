from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime


class StandardAPIResponse(BaseModel):
    """Standardized API response format for all endpoints."""
    data: Optional[Any] = Field(None, description="Response payload")
    success: bool = Field(..., description="Whether the operation was successful")
    errors: List[Dict[str, str]] = Field(default_factory=list, description="List of error messages")
    warnings: List[Dict[str, str]] = Field(default_factory=list, description="List of warning messages")


class ErrorMessage(BaseModel):
    """Standard error message format."""
    msg: str = Field(..., description="Error message")


class WarningMessage(BaseModel):
    """Standard warning message format."""
    msg: str = Field(..., description="Warning message")


class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class DatasourceCreate(BaseModel):
    name: str = Field(..., description="Name of the datasource")
    database_type: DatabaseType = Field(..., description="Type of database")
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    database: str = Field(..., description="Database name")
    username: Optional[str] = Field(None, description="Database username")
    password: Optional[str] = Field(None, description="Database password")
    connection_string: Optional[str] = Field(None, description="Full connection string")
    ssl_mode: Optional[str] = Field(None, description="SSL mode for connection")
    additional_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional connection parameters"
    )


class DatasourceResponse(BaseModel):
    id: int
    name: str
    database_type: DatabaseType
    host: Optional[str]
    port: Optional[int]
    database: str
    username: Optional[str]
    connection_string: Optional[str] = None
    ssl_mode: Optional[str]
    additional_params: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QueryCreate(BaseModel):
    name: str = Field(..., description="Name of the query")
    description: Optional[str] = Field(None, description="Query description")
    sql: str = Field(..., description="SQL query with parameter placeholders")
    datasource_id: int = Field(..., description="ID of the datasource to use")
    parameters: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Parameter definitions"
    )


class QueryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    sql: str
    datasource_id: int
    parameters: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginationRequest(BaseModel):
    page: int = Field(1, ge=1, description="Page number (1-based)")
    page_size: int = Field(10, ge=1, le=1000, description="Number of items per page")


class PaginationResponse(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class QueryExecutionRequest(BaseModel):
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Query parameters"
    )
    pagination: Optional[PaginationRequest] = Field(
        None, description="Pagination settings"
    )


class RawQueryRequest(BaseModel):
    datasource_id: int = Field(..., description="ID of the datasource to use")
    sql: str = Field(..., description="Raw SQL query")
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Query parameters"
    )
    pagination: Optional[PaginationRequest] = Field(
        None, description="Pagination settings"
    )


class QueryExecutionResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    execution_time_ms: float
    pagination: Optional[PaginationResponse]
    error: Optional[str] = None 