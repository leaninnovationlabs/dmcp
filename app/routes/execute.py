from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.schemas import (
    ToolExecutionRequest,
    ToolExecutionResponse,
    RawQueryRequest,
    StandardAPIResponse,
)
from ..database import get_db
from ..services.tool_execution_service import ToolExecutionService
from ..core.exceptions import handle_dbmcp_exception
from ..core.responses import create_success_response, create_error_response

router = APIRouter(prefix="/execute", tags=["tool execution"])


@router.post("/{tool_id}", response_model=StandardAPIResponse)
async def execute_named_tool(
    tool_id: int,
    execution_request: ToolExecutionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Execute a named tool with parameters and pagination."""
    try:
        service = ToolExecutionService(db)
        result = await service.execute_named_tool(
            tool_id, execution_request.parameters, execution_request.pagination
        )
        return create_success_response(data=result)
    except Exception as e:
        return create_error_response(errors=[str(e)])


@router.post("/raw", response_model=StandardAPIResponse)
async def execute_raw_query(
    raw_request: RawQueryRequest,
    db: AsyncSession = Depends(get_db),
):
    """Execute a raw SQL query with parameters and pagination."""
    try:
        service = ToolExecutionService(db)
        result = await service.execute_raw_query(
            raw_request.datasource_id,
            raw_request.sql,
            raw_request.parameters,
            raw_request.pagination,
        )
        return create_success_response(data=result)
    except Exception as e:
        return create_error_response(errors=[str(e)]) 