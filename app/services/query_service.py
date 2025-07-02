from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.query_repository import QueryRepository
from ..repositories.datasource_repository import DatasourceRepository
from ..models.schemas import QueryCreate, QueryResponse
from ..core.exceptions import QueryNotFoundError, DatasourceNotFoundError


class QueryService:
    """Service for query operations."""
    
    def __init__(self, db: AsyncSession):
        self.repository = QueryRepository(db)
        self.datasource_repository = DatasourceRepository(db)
    
    async def create_query(self, query: QueryCreate) -> QueryResponse:
        """Create a new named query."""
        try:
            # Verify datasource exists
            datasource = await self.datasource_repository.get_by_id(query.datasource_id)
            if not datasource:
                raise DatasourceNotFoundError(query.datasource_id)
            
            # Convert ParameterDefinition objects to dictionaries for JSON storage
            parameters_dict = []
            if query.parameters:
                for param in query.parameters:
                    param_dict = param.model_dump()
                    parameters_dict.append(param_dict)
            
            db_query = await self.repository.create_query(
                name=query.name,
                description=query.description,
                sql=query.sql,
                datasource_id=query.datasource_id,
                parameters=parameters_dict,
            )
            return QueryResponse.model_validate(db_query)
        except (DatasourceNotFoundError, ValueError):
            raise
        except Exception as e:
            raise Exception(f"Failed to create query: {str(e)}")
    
    async def list_queries(self) -> List[QueryResponse]:
        """List all named queries."""
        try:
            queries = await self.repository.get_all_with_datasource()
            return [QueryResponse.model_validate(q) for q in queries]
        except Exception as e:
            raise Exception(f"Failed to list queries: {str(e)}")
    
    async def get_query(self, query_id: int) -> Optional[QueryResponse]:
        """Get a specific named query by ID."""
        try:
            query = await self.repository.get_with_datasource(query_id)
            if query:
                return QueryResponse.model_validate(query)
            return None
        except Exception as e:
            raise Exception(f"Failed to get query: {str(e)}")
    
    async def update_query(self, query_id: int, **kwargs) -> QueryResponse:
        """Update a named query."""
        try:
            # If datasource_id is being updated, verify it exists
            if 'datasource_id' in kwargs:
                datasource = await self.datasource_repository.get_by_id(kwargs['datasource_id'])
                if not datasource:
                    raise DatasourceNotFoundError(kwargs['datasource_id'])
            
            # Convert ParameterDefinition objects to dictionaries if parameters are being updated
            if 'parameters' in kwargs and kwargs['parameters']:
                parameters_dict = []
                for param in kwargs['parameters']:
                    param_dict = param.model_dump()
                    parameters_dict.append(param_dict)
                kwargs['parameters'] = parameters_dict
            
            updated_query = await self.repository.update_query(query_id, **kwargs)
            return QueryResponse.model_validate(updated_query)
        except (QueryNotFoundError, DatasourceNotFoundError, ValueError):
            raise
        except Exception as e:
            raise Exception(f"Failed to update query: {str(e)}")
    
    async def delete_query(self, query_id: int) -> bool:
        """Delete a named query by ID."""
        try:
            return await self.repository.delete_query(query_id)
        except QueryNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"Failed to delete query: {str(e)}")
    
    async def get_queries_by_datasource(self, datasource_id: int) -> List[QueryResponse]:
        """Get all queries for a specific datasource."""
        try:
            # Verify datasource exists
            datasource = await self.datasource_repository.get_by_id(datasource_id)
            if not datasource:
                raise DatasourceNotFoundError(datasource_id)
            
            queries = await self.repository.get_by_datasource(datasource_id)
            return [QueryResponse.model_validate(q) for q in queries]
        except DatasourceNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"Failed to get queries by datasource: {str(e)}") 