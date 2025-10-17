import re
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import DatasourceNotFoundError, ToolNotFoundError
from ..models.schemas import ToolCreate, ToolResponse, ToolUpdate
from ..repositories.datasource_repository import DatasourceRepository
from ..repositories.tool_repository import ToolRepository
from ..models.schemas import ToolCreate, ToolUpdate, ToolResponse
from ..core.exceptions import ToolNotFoundError, DatasourceNotFoundError


class ToolService:
    """Service for tool operations."""

    def __init__(self, db: AsyncSession):
        self.repository = ToolRepository(db)
        self.datasource_repository = DatasourceRepository(db)

    def _validate_and_normalize_tags(self, tags: Optional[List[str]]) -> List[str]:
        """Validate and normalize tags.
        
        Args:
            tags: List of tag strings to validate
            
        Returns:
            List of normalized, deduplicated tags
            
        Raises:
            ValueError: If tags don't meet validation requirements
        """
        if not tags:
            return []
            
        # Validate individual tags
        for tag in tags:
            if not tag or not tag.strip():
                raise ValueError("Tags cannot be empty")
            if len(tag) > 50:
                raise ValueError("Tag must be 50 characters or less")
            if not re.match(r'^[a-zA-Z0-9_-]+$', tag):
                raise ValueError("Tag contains invalid characters. Only alphanumeric, hyphens, and underscores are allowed")
        
        normalized_tags = list(set(tag.lower().strip() for tag in tags))
        
        if len(normalized_tags) > 10:
            raise ValueError("Maximum 10 tags allowed per tool")
            
        return normalized_tags

    async def create_tool(self, tool: ToolCreate) -> ToolResponse:
        """Create a new named tool."""
        try:
            # Verify datasource exists
            datasource = await self.datasource_repository.get_by_id(tool.datasource_id)
            if not datasource:
                raise DatasourceNotFoundError(tool.datasource_id)

            # Validate tool type (optional validation) - accept both uppercase and lowercase
            valid_types = ["query", "http", "code"]
            valid_types_upper = [t.upper() for t in valid_types]
            normalized_type = tool.type.lower() if tool.type else ""
            
            if normalized_type not in valid_types:
                raise ValueError(f"Tool type must be one of: {', '.join(valid_types)}")
            
            # Use normalized lowercase type
            tool.type = normalized_type
            
            # Convert ParameterDefinition objects to dictionaries for JSON storage
            parameters_dict = []
            if tool.parameters:
                for param in tool.parameters:
                    param_dict = param.model_dump()
                    parameters_dict.append(param_dict)

            # Validate and normalize tags
            tags = self._validate_and_normalize_tags(tool.tags)

            db_tool = await self.repository.create_tool(
                name=tool.name,
                description=tool.description,
                type=tool.type,
                sql=tool.sql,
                datasource_id=tool.datasource_id,
                parameters=parameters_dict,
                tags=tags,
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

    async def update_tool(self, tool_id: int, tool_update: ToolUpdate) -> ToolResponse:
        """Update a named tool."""
        try:
            # Get current tool to merge with updates
            current_tool = await self.repository.get_by_id(tool_id)
            if not current_tool:
                raise ToolNotFoundError(tool_id)

            # Verify datasource exists if it's being changed
            datasource_id = (
                tool_update.datasource_id
                if tool_update.datasource_id is not None
                else current_tool.datasource_id
            )
            datasource = await self.datasource_repository.get_by_id(datasource_id)
            if not datasource:
                raise DatasourceNotFoundError(datasource_id)
            
            # Handle tool type validation and normalization if provided
            tool_type = current_tool.type
            if tool_update.type is not None:
                valid_types = ["query", "http", "code"]
                normalized_type = tool_update.type.lower()
                if normalized_type not in valid_types:
                    raise ValueError(f"Tool type must be one of: {', '.join(valid_types)}")
                tool_type = normalized_type
            
            # Prepare update data, using current values if not provided
            update_data = {
                'name': tool_update.name if tool_update.name is not None else current_tool.name,
                'description': tool_update.description if tool_update.description is not None else current_tool.description,
                'type': tool_type,
                'sql': tool_update.sql if tool_update.sql is not None else current_tool.sql,
                'datasource_id': datasource_id,
            }

            # Convert ParameterDefinition objects to dictionaries for JSON storage
            if tool_update.parameters is not None:
                parameters_dict = []
                for param in tool_update.parameters:
                    param_dict = param.model_dump()
                    parameters_dict.append(param_dict)
                update_data["parameters"] = parameters_dict
            else:
                update_data["parameters"] = current_tool.parameters

            # Handle tags
            if tool_update.tags is not None:
                update_data['tags'] = self._validate_and_normalize_tags(tool_update.tags)
            else:
                update_data['tags'] = current_tool.tags

            updated_tool = await self.repository.update_tool(tool_id, **update_data)
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
