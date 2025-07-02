from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..models.database import Query
from ..core.exceptions import QueryNotFoundError


class QueryRepository(BaseRepository[Query]):
    """Repository for query operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Query, db)
    
    async def get_by_name(self, name: str) -> Optional[Query]:
        """Get query by name."""
        return await self.find_one_by(name=name)
    
    async def get_with_datasource(self, query_id: int) -> Optional[Query]:
        """Get query with its associated datasource."""
        result = await self.db.execute(
            select(Query)
            .where(Query.id == query_id)
            .options(selectinload(Query.datasource))
        )
        return result.scalar_one_or_none()
    
    async def get_all_with_datasource(self) -> List[Query]:
        """Get all queries with their associated datasources."""
        result = await self.db.execute(
            select(Query).options(selectinload(Query.datasource))
        )
        return result.scalars().all()
    
    async def get_by_datasource(self, datasource_id: int) -> List[Query]:
        """Get all queries for a specific datasource."""
        return await self.find_by(datasource_id=datasource_id)
    
    async def create_query(self, **kwargs) -> Query:
        """Create a new query with validation."""
        # Check if query with same name already exists
        existing = await self.get_by_name(kwargs.get('name'))
        if existing:
            raise ValueError(f"Query with name '{kwargs['name']}' already exists")
        
        return await self.create(**kwargs)
    
    async def update_query(self, query_id: int, **kwargs) -> Query:
        """Update a query with validation."""
        query = await self.get_by_id(query_id)
        if not query:
            raise QueryNotFoundError(query_id)
        
        # If name is being updated, check for conflicts
        if 'name' in kwargs and kwargs['name'] != query.name:
            existing = await self.get_by_name(kwargs['name'])
            if existing:
                raise ValueError(f"Query with name '{kwargs['name']}' already exists")
        
        updated = await self.update(query_id, **kwargs)
        if not updated:
            raise QueryNotFoundError(query_id)
        
        return updated
    
    async def delete_query(self, query_id: int) -> bool:
        """Delete a query with validation."""
        query = await self.get_by_id(query_id)
        if not query:
            raise QueryNotFoundError(query_id)
        
        return await self.delete(query_id) 