from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.exceptions import ToolNotFoundError
from ..models.database import Tool
from ..models.schemas import SearchField
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

    def _escape_wildcards(self, text: str) -> str:
        """Escape SQL wildcard characters to prevent unintended pattern matching."""
        return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    def _build_search_pattern(self, query: str) -> str:
        """Build search pattern with user wildcards preserved."""
        escaped = self._escape_wildcards(query)
        return f"%{escaped}%"

    async def search_tools(self, query: str, fields: SearchField, limit: int, offset: int) -> Tuple[List[Tool], int]:
        """Search tools with case-insensitive wildcard matching."""
        search_pattern = self._build_search_pattern(query)

        stmt = select(Tool)

        if fields == SearchField.NAME:
            stmt = stmt.where(func.lower(Tool.name).like(func.lower(search_pattern)))
        elif fields == SearchField.DESCRIPTION:
            stmt = stmt.where(func.lower(Tool.description).like(func.lower(search_pattern)))
        else:
            stmt = stmt.where(
                or_(
                    func.lower(Tool.name).like(func.lower(search_pattern)),
                    func.lower(Tool.description).like(func.lower(search_pattern)),
                )
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar()

        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        tools = result.scalars().all()

        return tools, total_count
