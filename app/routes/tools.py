from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.tool_execution_service import ToolExecutionService

from ..core.responses import (
    create_success_response,
    raise_http_error,
)
from ..database import get_db
from ..models.schemas import (
    StandardAPIResponse,
    ToolCreate,
    ToolExecutionRequest,
    ToolUpdate,
)
from ..services.tool_service import ToolService

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("", response_model=StandardAPIResponse)
async def create_tool(
    tool: ToolCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new named tool with parameter support."""
    try:
        service = ToolService(db)
        result = await service.create_tool(tool)
        return create_success_response(data=result)
    except ValueError as e:
        raise_http_error(400, "Invalid tool data", [str(e)])
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.get("", response_model=StandardAPIResponse)
async def list_tools(db: AsyncSession = Depends(get_db)):
    """List all available named tools."""
    try:
        service = ToolService(db)
        result = await service.list_tools()
        return create_success_response(data=result)
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.get("/{tool_id}", response_model=StandardAPIResponse)
async def get_tool(
    tool_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific named tool by ID."""
    try:
        service = ToolService(db)
        tool = await service.get_tool(tool_id)
        if not tool:
            raise_http_error(404, "Tool not found")
        return create_success_response(data=tool)
    except HTTPException:
        raise
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.put("/{tool_id}", response_model=StandardAPIResponse)
async def update_tool(
    tool_id: int,
    tool_update: ToolUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing named tool by ID."""
    try:
        service = ToolService(db)
        result = await service.update_tool(tool_id, tool_update)
        return create_success_response(data=result)
    except HTTPException:
        raise
    except ValueError as e:
        raise_http_error(400, "Invalid tool data", [str(e)])
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.delete("/{tool_id}", response_model=StandardAPIResponse)
async def delete_tool(
    tool_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a named tool by ID."""
    try:
        service = ToolService(db)
        success = await service.delete_tool(tool_id)
        if not success:
            raise_http_error(404, "Tool not found")
        return create_success_response(data={"message": "Tool deleted successfully"})
    except HTTPException:
        raise
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.post("/{tool_id}/execute", response_model=StandardAPIResponse)
async def execute_named_tool(
    tool_id: int,
    execution_request: ToolExecutionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Execute a named tool with parameters and pagination."""
    try:
        service = ToolExecutionService(db)
        result = await service.execute_named_tool(tool_id, execution_request.parameters, execution_request.pagination)
        if result.error:
            raise_http_error(400, "Tool execution failed", [result.error])
        return create_success_response(data=result)
    except HTTPException:
        raise
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])
