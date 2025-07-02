from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..models.database import Datasource
from ..core.exceptions import DatasourceNotFoundError


class DatasourceRepository(BaseRepository[Datasource]):
    """Repository for datasource operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Datasource, db)
    
    async def get_by_name(self, name: str) -> Optional[Datasource]:
        """Get datasource by name."""
        return await self.find_one_by(name=name)
    
    async def get_with_tools(self, datasource_id: int) -> Optional[Datasource]:
        """Get datasource with its associated tools."""
        result = await self.db.execute(
            select(Datasource)
            .where(Datasource.id == datasource_id)
            .options(selectinload(Datasource.tools))
        )
        return result.scalar_one_or_none()
    
    async def get_all_with_tools(self) -> List[Datasource]:
        """Get all datasources with their associated tools."""
        result = await self.db.execute(
            select(Datasource).options(selectinload(Datasource.tools))
        )
        return result.scalars().all()
    
    async def create_datasource(self, **kwargs) -> Datasource:
        """Create a new datasource with validation."""
        # Check if datasource with same name already exists
        existing = await self.get_by_name(kwargs.get('name'))
        if existing:
            raise ValueError(f"Datasource with name '{kwargs['name']}' already exists")
        
        return await self.create(**kwargs)
    
    async def update_datasource(self, datasource_id: int, **kwargs) -> Datasource:
        """Update a datasource with validation."""
        datasource = await self.get_by_id(datasource_id)
        if not datasource:
            raise DatasourceNotFoundError(datasource_id)
        
        # If name is being updated, check for conflicts
        if 'name' in kwargs and kwargs['name'] != datasource.name:
            existing = await self.get_by_name(kwargs['name'])
            if existing:
                raise ValueError(f"Datasource with name '{kwargs['name']}' already exists")
        
        updated = await self.update(datasource_id, **kwargs)
        if not updated:
            raise DatasourceNotFoundError(datasource_id)
        
        return updated
    
    async def delete_datasource(self, datasource_id: int) -> bool:
        """Delete a datasource with validation."""
        datasource = await self.get_by_id(datasource_id)
        if not datasource:
            raise DatasourceNotFoundError(datasource_id)
        
        # Check if datasource has associated tools
        if datasource.tools:
            raise ValueError(f"Cannot delete datasource '{datasource.name}' - it has {len(datasource.tools)} associated tools")
        
        return await self.delete(datasource_id) 