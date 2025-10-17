from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


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
    DATABRICKS = "databricks"


class ParameterType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"


class ParameterDefinition(BaseModel):
    """Structured parameter definition for queries."""

    name: str = Field(..., description="Parameter name")
    type: ParameterType = Field(..., description="Parameter type")
    description: Optional[str] = Field(None, description="Parameter description")
    required: bool = Field(False, description="Whether the parameter is required")
    default: Optional[Any] = Field(None, description="Default value for the parameter")
    validation: Optional[Dict[str, Any]] = Field(None, description="Validation rules")


class FieldDefinition(BaseModel):
    """Definition of a form field for datasource configuration."""

    name: str = Field(..., description="Field name")
    type: str = Field(..., description="Field type (text, password, number, select, etc.)")
    label: str = Field(..., description="Display label for the field")
    required: bool = Field(False, description="Whether the field is required")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    description: Optional[str] = Field(None, description="Field description")
    options: Optional[List[Dict[str, str]]] = Field(None, description="Options for select fields")
    validation: Optional[Dict[str, Any]] = Field(None, description="Validation rules")


class DatasourceFieldConfig(BaseModel):
    """Configuration for datasource fields by database type."""

    database_type: DatabaseType = Field(..., description="Database type")
    fields: List[FieldDefinition] = Field(..., description="List of field definitions")
    sections: List[Dict[str, Any]] = Field(..., description="Form sections configuration")


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


class DatasourceUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the datasource")
    database_type: Optional[DatabaseType] = Field(None, description="Type of database")
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    database: Optional[str] = Field(None, description="Database name")
    username: Optional[str] = Field(None, description="Database username")
    password: Optional[str] = Field(None, description="Database password")
    connection_string: Optional[str] = Field(None, description="Full connection string")
    ssl_mode: Optional[str] = Field(None, description="SSL mode for connection")
    additional_params: Optional[Dict[str, Any]] = Field(None, description="Additional connection parameters")


class DatasourceResponse(BaseModel):
    id: int
    name: str
    database_type: DatabaseType
    host: Optional[str]
    port: Optional[int]
    database: str
    username: Optional[str]
    # password field removed - not returned in API responses for security
    connection_string: Optional[str] = None
    ssl_mode: Optional[str]
    additional_params: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ToolCreate(BaseModel):
    name: str = Field(..., description="Name of the tool")
    description: Optional[str] = Field(None, description="Tool description")
    type: str = Field(default="query", description="Type of the tool (query, http, code)")
    sql: str = Field(..., description="SQL query with parameter placeholders")
    datasource_id: int = Field(..., description="ID of the datasource to use")
    parameters: Optional[List[ParameterDefinition]] = Field(default_factory=list, description="Parameter definitions")


class ToolUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the tool")
    description: Optional[str] = Field(None, description="Tool description")
    type: Optional[str] = Field(None, description="Type of the tool (query, http, code)")
    sql: Optional[str] = Field(None, description="SQL query with parameter placeholders")
    datasource_id: Optional[int] = Field(None, description="ID of the datasource to use")
    parameters: Optional[List[ParameterDefinition]] = Field(None, description="Parameter definitions")


class ToolResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    type: str
    sql: str
    datasource_id: int
    parameters: List[ParameterDefinition]
    tags: List[str]
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj):
        """Custom validation to convert parameter dictionaries to ParameterDefinition objects."""
        if hasattr(obj, "parameters") and isinstance(obj.parameters, list):
            # Convert parameter dictionaries to ParameterDefinition objects
            converted_params = []
            for param_dict in obj.parameters:
                if isinstance(param_dict, dict):
                    converted_params.append(ParameterDefinition(**param_dict))
                elif isinstance(param_dict, ParameterDefinition):
                    converted_params.append(param_dict)
                else:
                    # Handle legacy format or invalid data
                    continue
            obj.parameters = converted_params

        return super().model_validate(obj)


class PaginationRequest(BaseModel):
    page: int = Field(1, description="Page number (1-based)")
    page_size: int = Field(10, description="Number of items per page")


class PaginationResponse(BaseModel):
    page: int
    page_size: int
    total_pages: int
    total_items: int
    has_next: bool
    has_prev: bool


class ToolExecutionRequest(BaseModel):
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Tool parameters")
    pagination: Optional[PaginationRequest] = Field(None, description="Pagination settings")


class RawQueryRequest(BaseModel):
    datasource_id: int = Field(..., description="ID of the datasource to use")
    sql: str = Field(..., description="Raw SQL query")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Query parameters")
    pagination: Optional[PaginationRequest] = Field(None, description="Pagination settings")


class ToolExecutionResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    execution_time_ms: float
    pagination: Optional[PaginationResponse]
    error: Optional[str] = None


class QueryExecutionResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    execution_time_ms: float
    pagination: Optional[PaginationResponse]
    error: Optional[str] = None


# User-related schemas
class UserCreate(BaseModel):
    username: str = Field(..., description="Unique username for the user")
    password: str = Field(..., description="User password (will be encrypted)")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    roles: Optional[List[str]] = Field(default_factory=list, description="List of user roles")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, description="Unique username for the user")
    password: Optional[str] = Field(None, description="User password (will be encrypted)")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    roles: Optional[List[str]] = Field(None, description="List of user roles")


class UserResponse(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    roles: List[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle roles conversion from string to list."""
        if hasattr(obj, "roles") and isinstance(obj.roles, str):
            # Convert comma-separated string to list
            if obj.roles:
                obj.roles = [role.strip() for role in obj.roles.split(",") if role.strip()]
            else:
                obj.roles = []

        return super().model_validate(obj)


class UserLogin(BaseModel):
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")


class UserPasswordChange(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")


class TokenResponse(BaseModel):
    token: str = Field(..., description="Generated JWT token")
    expires_at: datetime = Field(..., description="Token expiration time")
    user_id: int = Field(..., description="User ID associated with the token")
    username: str = Field(..., description="Username associated with the token")
