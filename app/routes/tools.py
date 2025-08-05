from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.schemas import ToolCreate, ToolUpdate, ToolResponse, StandardAPIResponse
from ..database import get_db
from ..services.tool_service import ToolService
from ..core.exceptions import handle_dbmcp_exception
from ..core.responses import create_success_response, create_error_response

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
        return create_error_response(errors=[str(e)])
    except Exception as e:
        return create_error_response(errors=[str(e)])


@router.get("", response_model=StandardAPIResponse)
async def list_tools(db: AsyncSession = Depends(get_db)):
    """List all available named tools."""
    try:
        service = ToolService(db)
        result = await service.list_tools()
        return create_success_response(data=result)
    except Exception as e:
        return create_error_response(errors=[str(e)])


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
            return create_error_response(errors=["Tool not found"])
        return create_success_response(data=tool)
    except Exception as e:
        return create_error_response(errors=[str(e)])


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
    except ValueError as e:
        return create_error_response(errors=[str(e)])
    except Exception as e:
        return create_error_response(errors=[str(e)])


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
            return create_error_response(errors=["Tool not found"])
        return create_success_response(data={"message": "Tool deleted successfully"})
    except Exception as e:
        return create_error_response(errors=[str(e)]) 