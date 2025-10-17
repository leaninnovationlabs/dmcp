import re
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import TagNotFoundError
from ..models.schemas import TagCreate, TagResponse, TagUpdate
from ..repositories.tag_repository import TagRepository


class TagService:
    """Service for tag operations."""

    def __init__(self, db: AsyncSession):
        self.repository = TagRepository(db)

    def _validate_tag_name(self, name: str) -> str:
        """Validate and normalize tag name.
        
        Args:
            name: Tag name to validate
            
        Returns:
            Normalized tag name (lowercase)
            
        Raises:
            ValueError: If tag name doesn't meet validation requirements
        """
        if not name or not name.strip():
            raise ValueError("Tag name cannot be empty")
        
        if len(name) > 50:
            raise ValueError("Tag name must be 50 characters or less")
        
        normalized_name = name.strip().lower()
        
        return normalized_name

    def _validate_color(self, color: Optional[str]) -> Optional[str]:
        """Validate hex color code format.
        
        Args:
            color: Hex color code to validate (e.g., #FF5733)
            
        Returns:
            Validated color code or None
            
        Raises:
            ValueError: If color format is invalid
        """
        if not color:
            return None
        
        color = color.strip()
        
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValueError("Color must be a valid hex code (e.g., #FF5733)")
        
        return color.upper()

    async def create_tag(self, tag: TagCreate) -> TagResponse:
        """Create a new tag."""
        try:
            normalized_name = self._validate_tag_name(tag.name)
            
            validated_color = self._validate_color(tag.color)
            
            db_tag = await self.repository.create_tag(
                name=normalized_name,
                description=tag.description,
                color=validated_color,
            )
            return TagResponse.model_validate(db_tag)
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Failed to create tag: {str(e)}")

    async def list_tags(self) -> List[TagResponse]:
        """List all tags."""
        try:
            tags = await self.repository.get_all()
            return [TagResponse.model_validate(tag) for tag in tags]
        except Exception as e:
            raise Exception(f"Failed to list tags: {str(e)}")

    async def get_tag(self, tag_id: int) -> Optional[TagResponse]:
        """Get a specific tag by ID."""
        try:
            tag = await self.repository.get_by_id(tag_id)
            if tag:
                return TagResponse.model_validate(tag)
            return None
        except TagNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"Failed to get tag: {str(e)}")

    async def update_tag(self, tag_id: int, tag_update: TagUpdate) -> TagResponse:
        """Update a tag."""
        try:
            current_tag = await self.repository.get_by_id(tag_id)
            if not current_tag:
                raise TagNotFoundError(tag_id)

            update_data = {}
            
            if tag_update.name is not None:
                update_data["name"] = self._validate_tag_name(tag_update.name)
            
            if tag_update.description is not None:
                update_data["description"] = tag_update.description
            
            if tag_update.color is not None:
                update_data["color"] = self._validate_color(tag_update.color)

            updated_tag = await self.repository.update_tag(tag_id, **update_data)
            if updated_tag:
                return TagResponse.model_validate(updated_tag)
            raise TagNotFoundError(tag_id)
        except (TagNotFoundError, ValueError):
            raise
        except Exception as e:
            raise Exception(f"Failed to update tag: {str(e)}")

    async def delete_tag(self, tag_id: int) -> bool:
        """Delete a tag by ID."""
        try:
            return await self.repository.delete_tag(tag_id)
        except TagNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"Failed to delete tag: {str(e)}")
