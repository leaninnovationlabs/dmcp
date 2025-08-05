from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from ..models.database import Datasource
from ..models.schemas import DatasourceCreate, DatasourceResponse


class DatasourceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_datasource(self, datasource: DatasourceCreate) -> DatasourceResponse:
        """Create a new datasource."""
        db_datasource = Datasource(
            name=datasource.name,
            database_type=datasource.database_type.value,
            host=datasource.host,
            port=datasource.port,
            database=datasource.database,
            username=datasource.username,
            connection_string=datasource.connection_string,
            ssl_mode=datasource.ssl_mode,
            additional_params=datasource.additional_params or {},
        )
        
        # Set password using the property to trigger encryption
        db_datasource.decrypted_password = datasource.password
        
        self.db.add(db_datasource)
        await self.db.commit()
        await self.db.refresh(db_datasource)
        
        return DatasourceResponse.model_validate(db_datasource)

    async def list_datasources(self) -> List[DatasourceResponse]:
        """List all datasources."""
        result = await self.db.execute(select(Datasource))
        datasources = result.scalars().all()
        return [DatasourceResponse.model_validate(ds) for ds in datasources]

    async def get_datasource(self, datasource_id: int) -> Optional[DatasourceResponse]:
        """Get a specific datasource by ID."""
        result = await self.db.execute(select(Datasource).where(Datasource.id == datasource_id))
        datasource = result.scalar_one_or_none()
        if datasource:
            return DatasourceResponse.model_validate(datasource)
        return None

    async def update_datasource(self, datasource_id: int, **kwargs) -> DatasourceResponse:
        """Update an existing datasource."""
        result = await self.db.execute(select(Datasource).where(Datasource.id == datasource_id))
        datasource = result.scalar_one_or_none()
        
        if not datasource:
            raise ValueError(f"Datasource with ID {datasource_id} not found")
        
        # Update fields
        for key, value in kwargs.items():
            if key == 'password':
                # Use the property to trigger encryption
                datasource.decrypted_password = value
            elif hasattr(datasource, key):
                setattr(datasource, key, value)
        
        await self.db.commit()
        await self.db.refresh(datasource)
        
        return DatasourceResponse.model_validate(datasource)

    async def delete_datasource(self, datasource_id: int) -> bool:
        """Delete a datasource by ID."""
        result = await self.db.execute(delete(Datasource).where(Datasource.id == datasource_id))
        await self.db.commit()
        return result.rowcount > 0