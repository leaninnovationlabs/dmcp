from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..models.schemas import DatasourceCreate, DatasourceResponse, StandardAPIResponse
from ..database import get_db
from ..services.datasource_service import DatasourceService
from ..core.exceptions import handle_dbmcp_exception
from ..core.responses import create_success_response, create_error_response


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
    connection_time_ms: float
    error: Optional[str] = None


router = APIRouter(prefix="/datasources", tags=["datasources"])


@router.post("/", response_model=StandardAPIResponse)
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
        return create_error_response(errors=[str(e)])
    except Exception as e:
        return create_error_response(errors=[str(e)])


@router.get("/", response_model=StandardAPIResponse)
async def list_datasources(db: AsyncSession = Depends(get_db)):
    """List all available datasources."""
    try:
        service = DatasourceService(db)
        result = await service.list_datasources()
        return create_success_response(data=result)
    except Exception as e:
        return create_error_response(errors=[str(e)])


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
            return create_error_response(errors=["Datasource not found"])
        return create_success_response(data=datasource)
    except Exception as e:
        return create_error_response(errors=[str(e)])


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
            return create_error_response(errors=["Datasource not found"])
        return create_success_response(data={"message": "Datasource deleted successfully"})
    except ValueError as e:
        return create_error_response(errors=[str(e)])
    except Exception as e:
        return create_error_response(errors=[str(e)])


@router.post("/{datasource_id}/test", response_model=StandardAPIResponse)
async def test_datasource_connection(
    datasource_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Test the database connection for a specific datasource."""
    try:
        service = DatasourceService(db)
        result = await service.test_connection(datasource_id)
        return create_success_response(data=result)
    except HTTPException:
        raise
    except Exception as e:
        return create_error_response(errors=[str(e)]) 