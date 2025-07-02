from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.schemas import QueryCreate, QueryResponse, StandardAPIResponse
from ..database import get_db
from ..services.query_service import QueryService
from ..core.exceptions import handle_dbmcp_exception
from ..core.responses import create_success_response, create_error_response

router = APIRouter(prefix="/queries", tags=["queries"])


@router.post("/", response_model=StandardAPIResponse)
async def create_query(
    query: QueryCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new named query with parameter support."""
    try:
        service = QueryService(db)
        result = await service.create_query(query)
        return create_success_response(data=result)
    except ValueError as e:
        return create_error_response(errors=[str(e)])
    except Exception as e:
        return create_error_response(errors=[str(e)])


@router.get("/", response_model=StandardAPIResponse)
async def list_queries(db: AsyncSession = Depends(get_db)):
    """List all available named queries."""
    try:
        service = QueryService(db)
        result = await service.list_queries()
        return create_success_response(data=result)
    except Exception as e:
        return create_error_response(errors=[str(e)])


@router.get("/{query_id}", response_model=StandardAPIResponse)
async def get_query(
    query_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific named query by ID."""
    try:
        service = QueryService(db)
        query = await service.get_query(query_id)
        if not query:
            return create_error_response(errors=["Query not found"])
        return create_success_response(data=query)
    except Exception as e:
        return create_error_response(errors=[str(e)])


@router.delete("/{query_id}", response_model=StandardAPIResponse)
async def delete_query(
    query_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a named query by ID."""
    try:
        service = QueryService(db)
        success = await service.delete_query(query_id)
        if not success:
            return create_error_response(errors=["Query not found"])
        return create_success_response(data={"message": "Query deleted successfully"})
    except Exception as e:
        return create_error_response(errors=[str(e)]) 