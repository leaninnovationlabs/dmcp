from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import TagNotFoundError
from ..models.database import Tag
from .base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    """Repository for tag operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Tag, db)

    async def get_by_name(self, name: str) -> Optional[Tag]:
        """Get tag by name."""
        return await self.find_one_by(name=name)

    async def create_tag(self, **kwargs) -> Tag:
        """Create a new tag with validation."""
        existing = await self.get_by_name(kwargs.get("name"))
        if existing:
            raise ValueError(f"Tag with name '{kwargs['name']}' already exists")

        return await self.create(**kwargs)

    async def get_by_id(self, tag_id: int) -> Optional[Tag]:
        """Get tag by ID."""
        tag = await super().get_by_id(tag_id)
        if not tag:
            raise TagNotFoundError(tag_id)
        return tag

    async def update_tag(self, tag_id: int, **kwargs) -> Optional[Tag]:
        """Update tag by ID."""
        tag = await self.get_by_id(tag_id)
        if not tag:
            raise TagNotFoundError(tag_id)
        return await self.update(tag_id, **kwargs)

    async def delete_tag(self, tag_id: int) -> bool:
        """Delete tag by ID."""
        tag = await self.get_by_id(tag_id)
        if not tag:
            raise TagNotFoundError(tag_id)
        return await self.delete(tag_id)
