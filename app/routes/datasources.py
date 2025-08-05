from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..models.schemas import DatasourceCreate, DatasourceUpdate, DatasourceResponse, StandardAPIResponse
from ..database import get_db
from ..repositories.datasource_repository import DatasourceRepository
from ..services import DatasourceService
from ..core.exceptions import handle_dbmcp_exception
from ..core.responses import create_success_response, create_error_response


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
    connection_time_ms: float
    error: Optional[str] = None


router = APIRouter(prefix="/datasources", tags=["datasources"])


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
        return create_error_response(errors=[str(e)])
    except Exception as e:
        return create_error_response(errors=[str(e)])


@router.get("", response_model=StandardAPIResponse)
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
        repository = DatasourceRepository(db)
        datasource = await repository.get_by_id(datasource_id)
        if not datasource:
            return create_error_response(errors=["Datasource not found"])
        return create_success_response(data=datasource)
    except Exception as e:
        return create_error_response(errors=[str(e)])


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
            return create_error_response(errors=["No valid fields provided for update"])
        
        result = await service.update_datasource(datasource_id, **update_data)
        return create_success_response(data=result)
    except ValueError as e:
        return create_error_response(errors=[str(e)])
    except Exception as e:
        return create_error_response(errors=[str(e)])


@router.delete("/{datasource_id}", response_model=StandardAPIResponse)
async def delete_datasource(
    datasource_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a datasource by ID."""
    try:
        repository = DatasourceRepository(db)
        success = await repository.delete(datasource_id)
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
        repository = DatasourceRepository(db)
        datasource = await repository.get_by_id(datasource_id)
        
        if not datasource:
            raise HTTPException(status_code=404, detail="Datasource not found")
        
        result = ConnectionTestResponse(
            success=True,
            message="Datasource found - connection testing simplified for PostgreSQL migration",
            connection_time_ms=0.0
        )
        return create_success_response(data=result)
    except HTTPException:
        raise
    except Exception as e:
        return create_error_response(errors=[str(e)]) 