from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.responses import create_success_response, raise_http_error
from ..database import get_db
from ..models.schemas import StandardAPIResponse, TagCreate, TagUpdate
from ..services.tag_service import TagService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("", response_model=StandardAPIResponse)
async def create_tag(
    tag: TagCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new tag."""
    try:
        service = TagService(db)
        result = await service.create_tag(tag)
        return create_success_response(data=result)
    except ValueError as e:
        raise_http_error(400, "Invalid tag data", [str(e)])
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.get("", response_model=StandardAPIResponse)
async def list_tags(db: AsyncSession = Depends(get_db)):
    """List all available tags."""
    try:
        service = TagService(db)
        result = await service.list_tags()
        return create_success_response(data=result)
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.get("/{tag_id}", response_model=StandardAPIResponse)
async def get_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific tag by ID."""
    try:
        service = TagService(db)
        tag = await service.get_tag(tag_id)
        if not tag:
            raise_http_error(404, "Tag not found")
        return create_success_response(data=tag)
    except HTTPException:
        raise
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.put("/{tag_id}", response_model=StandardAPIResponse)
async def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing tag by ID."""
    try:
        service = TagService(db)
        result = await service.update_tag(tag_id, tag_update)
        return create_success_response(data=result)
    except HTTPException:
        raise
    except ValueError as e:
        raise_http_error(400, "Invalid tag data", [str(e)])
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])


@router.delete("/{tag_id}", response_model=StandardAPIResponse)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a tag by ID."""
    try:
        service = TagService(db)
        success = await service.delete_tag(tag_id)
        if not success:
            raise_http_error(404, "Tag not found")
        return create_success_response(data={"message": "Tag deleted successfully"})
    except HTTPException:
        raise
    except Exception as e:
        raise_http_error(500, "Internal server error", [str(e)])
