from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.datasources.base import logger

from ..core.encryption import password_encryption
from ..models.database import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create_user(
        self,
        username: str,
        password: str,
        first_name: str,
        last_name: str,
        roles: List[str] = None,
    ) -> User:
        """Create a new user with encrypted password."""
        if roles is None:
            roles = []

        # Encrypt the password before storing
        encrypted_password = password_encryption.encrypt_password(password)

        # Convert roles list to comma-separated string
        roles_string = ",".join(roles) if roles else ""

        print(f"Roles string: {roles_string}")

        return await self.create(
            username=username,
            password=encrypted_password,
            first_name=first_name,
            last_name=last_name,
            roles=roles_string,
        )

    async def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update a user, handling password encryption if password is being updated."""
        if "password" in kwargs and kwargs["password"]:
            # Encrypt the new password
            kwargs["password"] = password_encryption.encrypt_password(
                kwargs["password"]
            )

        # Convert roles list to comma-separated string if provided
        if "roles" in kwargs and isinstance(kwargs["roles"], list):
            kwargs["roles"] = ",".join(kwargs["roles"]) if kwargs["roles"] else ""

        return await super().update(user_id, **kwargs)

    def validate_password(
        self, username: str, userpassword: str, password: str
    ) -> bool:
        """Validate a password."""

        # ALERT: Check for the out of the box admin password and if the password is dochangethispassword
        if (
            username == settings.default_admin_username
            and password == settings.default_admin_password
            and userpassword == settings.default_admin_password_encrypted
        ):
            logger.warning(
                f"!!!Alert!!!! Used the default admin password for user: {username}"
            )
            return True

        if password_encryption.decrypt_password(userpassword) == password:
            return True
        return False

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        user = await self.get_by_username(username)
        if not user:
            return None

        # Verify the password
        try:
            if self.validate_password(user.username, user.password, password):
                return user
        except Exception:
            # If decryption fails, the password is invalid
            pass

        return None

    async def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> bool:
        """Change a user's password after verifying the current password."""
        user = await self.get_by_id(user_id)
        if not user:
            return False

        # Verify current password
        try:
            if not self.validate_password(
                user.username, user.password, current_password
            ):
                return False
        except Exception:
            return False

        # Update to new password
        encrypted_new_password = password_encryption.encrypt_password(new_password)
        await self.update(user_id, password=encrypted_new_password)
        return True

    async def get_users_by_role(self, role: str) -> List[User]:
        """Get all users with a specific role."""
        result = await self.db.execute(select(User).where(User.roles.like(f"%{role}%")))
        return result.scalars().all()

    async def username_exists(self, username: str) -> bool:
        """Check if a username already exists."""
        user = await self.get_by_username(username)
        return user is not None
