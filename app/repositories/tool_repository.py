from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.exceptions import ToolNotFoundError
from ..models.database import Tool
from .base import BaseRepository


class ToolRepository(BaseRepository[Tool]):
    """Repository for tool operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Tool, db)

    async def get_by_name(self, name: str) -> Optional[Tool]:
        """Get tool by name."""
        return await self.find_one_by(name=name)

    async def get_with_datasource(self, tool_id: int) -> Optional[Tool]:
        """Get tool with its associated datasource."""
        result = await self.db.execute(select(Tool).where(Tool.id == tool_id).options(selectinload(Tool.datasource)))
        return result.scalar_one_or_none()

    async def get_all_with_datasource(self) -> List[Tool]:
        """Get all tools with their associated datasources."""
        result = await self.db.execute(select(Tool).options(selectinload(Tool.datasource)))
        return result.scalars().all()

    async def get_by_datasource(self, datasource_id: int) -> List[Tool]:
        """Get all tools for a specific datasource."""
        return await self.find_by(datasource_id=datasource_id)

    async def create_tool(self, **kwargs) -> Tool:
        """Create a new tool with validation."""
        # Check if tool with same name already exists
        existing = await self.get_by_name(kwargs.get("name"))
        if existing:
            raise ValueError(f"Tool with name '{kwargs['name']}' already exists")

        return await self.create(**kwargs)

    async def get_by_id(self, tool_id: int) -> Optional[Tool]:
        """Get tool by ID."""
        tool = await super().get_by_id(tool_id)
        if not tool:
            raise ToolNotFoundError(tool_id)
        return tool

    async def update_tool(self, tool_id: int, **kwargs) -> Optional[Tool]:
        """Update tool by ID."""
        tool = await self.get_by_id(tool_id)
        if not tool:
            raise ToolNotFoundError(tool_id)
        return await self.update(tool_id, **kwargs)

    async def delete_tool(self, tool_id: int) -> bool:
        """Delete tool by ID."""
        tool = await self.get_by_id(tool_id)
        if not tool:
            raise ToolNotFoundError(tool_id)
        return await self.delete(tool_id)
