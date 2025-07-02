from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.tool_repository import ToolRepository
from ..repositories.datasource_repository import DatasourceRepository
from ..models.schemas import ToolCreate, ToolResponse
from ..core.exceptions import ToolNotFoundError, DatasourceNotFoundError


class ToolService:
    """Service for tool operations."""
    
    def __init__(self, db: AsyncSession):
        self.repository = ToolRepository(db)
        self.datasource_repository = DatasourceRepository(db)
    
    async def create_tool(self, tool: ToolCreate) -> ToolResponse:
        """Create a new named tool."""
        try:
            # Verify datasource exists
            datasource = await self.datasource_repository.get_by_id(tool.datasource_id)
            if not datasource:
                raise DatasourceNotFoundError(tool.datasource_id)
            
            # Convert ParameterDefinition objects to dictionaries for JSON storage
            parameters_dict = []
            if tool.parameters:
                for param in tool.parameters:
                    param_dict = param.model_dump()
                    parameters_dict.append(param_dict)
            
            db_tool = await self.repository.create_tool(
                name=tool.name,
                description=tool.description,
                sql=tool.sql,
                datasource_id=tool.datasource_id,
                parameters=parameters_dict,
            )
            return ToolResponse.model_validate(db_tool)
        except (DatasourceNotFoundError, ValueError):
            raise
        except Exception as e:
            raise Exception(f"Failed to create tool: {str(e)}")
    
    async def list_tools(self) -> List[ToolResponse]:
        """List all named tools."""
        try:
            tools = await self.repository.get_all_with_datasource()
            return [ToolResponse.model_validate(tool) for tool in tools]
        except Exception as e:
            raise Exception(f"Failed to list tools: {str(e)}")
    
    async def get_tool(self, tool_id: int) -> Optional[ToolResponse]:
        """Get a specific named tool by ID."""
        try:
            tool = await self.repository.get_with_datasource(tool_id)
            if tool:
                return ToolResponse.model_validate(tool)
            return None
        except (ToolNotFoundError, DatasourceNotFoundError, ValueError):
            raise
        except Exception as e:
            raise Exception(f"Failed to get tool: {str(e)}")
    
    async def update_tool(self, tool_id: int, tool_update: ToolCreate) -> ToolResponse:
        """Update a named tool."""
        try:
            # Verify datasource exists if it's being changed
            datasource = await self.datasource_repository.get_by_id(tool_update.datasource_id)
            if not datasource:
                raise DatasourceNotFoundError(tool_update.datasource_id)
            
            # Convert ParameterDefinition objects to dictionaries for JSON storage
            parameters_dict = []
            if tool_update.parameters:
                for param in tool_update.parameters:
                    param_dict = param.model_dump()
                    parameters_dict.append(param_dict)
            
            updated_tool = await self.repository.update_tool(
                tool_id,
                name=tool_update.name,
                description=tool_update.description,
                sql=tool_update.sql,
                datasource_id=tool_update.datasource_id,
                parameters=parameters_dict,
            )
            if updated_tool:
                return ToolResponse.model_validate(updated_tool)
            raise ToolNotFoundError(tool_id)
        except (ToolNotFoundError, DatasourceNotFoundError, ValueError):
            raise
        except Exception as e:
            raise Exception(f"Failed to update tool: {str(e)}")
    
    async def delete_tool(self, tool_id: int) -> bool:
        """Delete a named tool by ID."""
        try:
            return await self.repository.delete_tool(tool_id)
        except ToolNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"Failed to delete tool: {str(e)}")
    
    async def get_tools_by_datasource(self, datasource_id: int) -> List[ToolResponse]:
        """Get all tools for a specific datasource."""
        try:
            # Verify datasource exists
            datasource = await self.datasource_repository.get_by_id(datasource_id)
            if not datasource:
                raise DatasourceNotFoundError(datasource_id)
            
            tools = await self.repository.get_by_datasource(datasource_id)
            return [ToolResponse.model_validate(t) for t in tools]
        except DatasourceNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"Failed to get tools by datasource: {str(e)}") 