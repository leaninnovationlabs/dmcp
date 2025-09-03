from typing import Generic, TypeVar, Type, List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.ext.declarative import DeclarativeMeta
from datetime import datetime, timezone

from ..core.exceptions import DMCPException

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        try:
            instance = self.model(**kwargs)
            self.db.add(instance)
            await self.db.commit()
            await self.db.refresh(instance)
            return instance
        except Exception as e:
            await self.db.rollback()
            raise DMCPException(f"Failed to create {self.model.__name__}: {str(e)}")
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get a record by ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[ModelType]:
        """Get all records."""
        result = await self.db.execute(select(self.model))
        return result.scalars().all()
    
    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Update a record by ID."""
        try:
            # Add updated_at timestamp if the model has it
            if hasattr(self.model, 'updated_at'):
                kwargs['updated_at'] = datetime.now(timezone.utc)
            
            result = await self.db.execute(
                update(self.model)
                .where(self.model.id == id)
                .values(**kwargs)
                .returning(self.model)
            )
            await self.db.commit()
            return result.scalar_one_or_none()
        except Exception as e:
            await self.db.rollback()
            raise DMCPException(f"Failed to update {self.model.__name__}: {str(e)}")
    
    async def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        try:
            result = await self.db.execute(
                delete(self.model).where(self.model.id == id)
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            raise DMCPException(f"Failed to delete {self.model.__name__}: {str(e)}")
    
    async def find_by(self, **kwargs) -> List[ModelType]:
        """Find records by given criteria."""
        query = select(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def find_one_by(self, **kwargs) -> Optional[ModelType]:
        """Find one record by given criteria."""
        query = select(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() 