from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.responses import (
    create_success_response,
    raise_http_error,
)
from ..database import get_db
from ..models.schemas import (
    DatabaseType,
    DatasourceCreate,
    DatasourceUpdate,
    FieldDefinition,
    StandardAPIResponse,
)
from ..services.datasource_service import DatasourceService


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
    connection_time_ms: float
    error: Optional[str] = None


router = APIRouter(prefix="/datasources", tags=["datasources"])


@router.get("/field-config", response_model=StandardAPIResponse)
async def get_datasource_field_config():
    """Get field configuration for all datasource types."""
    try:
        # Hardcoded field configurations for each database type
        field_configs = {
            "sqlite": {
                "database_type": DatabaseType.SQLITE,
                "fields": [
                    FieldDefinition(
                        name="sqlite_database",
                        type="text",
                        label="Database File Path",
                        required=True,
                        placeholder="/path/to/database.db",
                        description="Path to the SQLite database file",
                    )
                ],
                "sections": [
                    {
                        "id": "sqlite-config",
                        "title": "SQLite Configuration",
                        "description": "Configure your SQLite database connection",
                    }
                ],
            },
            "postgresql": {
                "database_type": DatabaseType.POSTGRESQL,
                "fields": [
                    FieldDefinition(
                        name="host",
                        type="text",
                        label="Host",
                        required=True,
                        placeholder="localhost",
                    ),
                    FieldDefinition(
                        name="port",
                        type="number",
                        label="Port",
                        required=True,
                        placeholder="5432",
                    ),
                    FieldDefinition(
                        name="database",
                        type="text",
                        label="Database Name",
                        required=True,
                        placeholder="mydatabase",
                    ),
                    FieldDefinition(
                        name="username",
                        type="text",
                        label="Username",
                        required=True,
                        placeholder="myuser",
                    ),
                    FieldDefinition(
                        name="password",
                        type="password",
                        label="Password",
                        required=False,
                        placeholder="mypassword"
                    ),
                    FieldDefinition(
                        name="ssl_mode",
                        type="select",
                        label="SSL Mode",
                        required=False,
                        options=[
                            {"value": "", "label": "None"},
                            {"value": "require", "label": "Require"},
                            {"value": "verify-ca", "label": "Verify CA"},
                            {"value": "verify-full", "label": "Verify Full"},
                        ],
                    ),
                ],
                "sections": [
                    {
                        "id": "postgresql-config",
                        "title": "PostgreSQL/MySQL Configuration",
                        "description": "Configure your PostgreSQL or MySQL database connection",
                    }
                ],
            },
            "mysql": {
                "database_type": DatabaseType.MYSQL,
                "fields": [
                    FieldDefinition(
                        name="host",
                        type="text",
                        label="Host",
                        required=True,
                        placeholder="localhost",
                    ),
                    FieldDefinition(
                        name="port",
                        type="number",
                        label="Port",
                        required=True,
                        placeholder="3306",
                    ),
                    FieldDefinition(
                        name="database",
                        type="text",
                        label="Database Name",
                        required=True,
                        placeholder="mydatabase",
                    ),
                    FieldDefinition(
                        name="username",
                        type="text",
                        label="Username",
                        required=True,
                        placeholder="myuser",
                    ),
                    FieldDefinition(
                        name="password",
                        type="password",
                        label="Password",
                        required=False,
                        placeholder="mypassword"
                    ),
                    FieldDefinition(
                        name="ssl_mode",
                        type="select",
                        label="SSL Mode",
                        required=False,
                        options=[
                            {"value": "", "label": "None"},
                            {"value": "require", "label": "Require"},
                            {"value": "verify-ca", "label": "Verify CA"},
                            {"value": "verify-full", "label": "Verify Full"},
                        ],
                    ),
                ],
                "sections": [
                    {
                        "id": "postgresql-config",
                        "title": "PostgreSQL/MySQL Configuration",
                        "description": "Configure your PostgreSQL or MySQL database connection",
                    }
                ],
            },
            "databricks": {
                "database_type": DatabaseType.DATABRICKS,
                "fields": [
                    FieldDefinition(
                        name="databricks_host",
                        type="text",
                        label="Workspace URL",
                        required=True,
                        placeholder="https://your-workspace.cloud.databricks.com",
                    ),
                    FieldDefinition(
                        name="http_path",
                        type="text",
                        label="HTTP Path",
                        required=True,
                        placeholder="/sql/1.0/warehouses/default",
                    ),
                    FieldDefinition(
                        name="databricks_token",
                        type="password",
                        label="Access Token",
                        required=True,
                        placeholder="dapi...",
                    ),
                    FieldDefinition(
                        name="catalog",
                        type="text",
                        label="Catalog",
                        required=False,
                        placeholder="hive_metastore",
                    ),
                    FieldDefinition(
                        name="schema",
                        type="text",
                        label="Schema",
                        required=False,
                        placeholder="default",
                    ),
                ],
                "sections": [
                    {
                        "id": "databricks-config",
                        "title": "Databricks Configuration",
                        "description": "Configure your Databricks SQL warehouse connection",
                    }
                ],
            },
        }

        return create_success_response(data=field_configs)
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.post("", response_model=StandardAPIResponse)
async def create_datasource(
    datasource: DatasourceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new datasource with database connection information."""
    try:
        service = DatasourceService(db)
        result = await service.create_datasource(datasource)
        return create_success_response(data=result)
    except ValueError as e:
        raise_http_error(400, "Invalid datasource data", [str(e)])
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.get("", response_model=StandardAPIResponse)
async def list_datasources(db: AsyncSession = Depends(get_db)):
    """List all available datasources."""
    try:
        service = DatasourceService(db)
        result = await service.list_datasources()
        return create_success_response(data=result)
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.get("/{datasource_id}", response_model=StandardAPIResponse)
async def get_datasource(
    datasource_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific datasource by ID."""
    try:
        service = DatasourceService(db)
        datasource = await service.get_datasource(datasource_id)
        if not datasource:
            raise_http_error(404, "Datasource not found")
        return create_success_response(data=datasource)
    except HTTPException:
        raise
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.put("/{datasource_id}", response_model=StandardAPIResponse)
async def update_datasource(
    datasource_id: int,
    datasource_update: DatasourceUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing datasource by ID."""
    try:
        service = DatasourceService(db)
        # Convert Pydantic model to dict, excluding None values
        update_data = datasource_update.model_dump(exclude_unset=True)

        if not update_data:
            raise_http_error(400, "No valid fields provided for update")

        result = await service.update_datasource(datasource_id, **update_data)
        return create_success_response(data=result)
    except HTTPException:
        raise
    except ValueError as e:
        raise_http_error(400, "Invalid datasource data", [str(e)])
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.delete("/{datasource_id}", response_model=StandardAPIResponse)
async def delete_datasource(
    datasource_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a datasource by ID."""
    try:
        service = DatasourceService(db)
        success = await service.delete_datasource(datasource_id)
        if not success:
            raise_http_error(404, "Datasource not found")
        return create_success_response(
            data={"message": "Datasource deleted successfully"}
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise_http_error(400, "Invalid datasource data", [str(e)])
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.post("/test-connection", response_model=StandardAPIResponse)
async def test_connection_params(
    datasource: DatasourceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Test database connection with provided parameters without saving."""
    try:
        service = DatasourceService(db)
        result = await service.test_connection_params(datasource)
        if not result["success"]:
            raise_http_error(400, "Connection test failed", [result["message"]])
        return create_success_response(data=result)
    except HTTPException:
        raise
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.post("/{datasource_id}/test", response_model=StandardAPIResponse)
async def test_datasource_connection(
    datasource_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Test the database connection for a specific datasource."""
    try:
        service = DatasourceService(db)
        result = await service.test_connection(datasource_id)
        print(result)
        if not result["success"]:
            raise_http_error(400, "Connection test failed", [result["message"]])
        return create_success_response(data=result)
    except HTTPException:
        raise
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])
