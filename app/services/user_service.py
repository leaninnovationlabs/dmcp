from typing import List, Optional

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import DMCPException
from ..models.schemas import (
    UserCreate,
    UserLogin,
    UserPasswordChange,
    UserResponse,
    UserUpdate,
)
from ..repositories.user_repository import UserRepository

# Password hashing context for additional security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service for user-related business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        # Check if username already exists
        if await self.user_repo.username_exists(user_data.username):
            raise DMCPException("Username already exists")

        # Create user with encrypted password
        user = await self.user_repo.create_user(
            username=user_data.username,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            roles=user_data.roles or [],
        )

        # Convert to response format
        return UserResponse.model_validate(user)

    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Get a user by ID."""
        user = await self.user_repo.get_by_id(user_id)
        if user:
            return UserResponse.model_validate(user)
        return None

    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get a user by username."""
        user = await self.user_repo.get_by_username(username)
        if user:
            return UserResponse.model_validate(user)
        return None

    async def get_all_users(self) -> List[UserResponse]:
        """Get all users."""
        users = await self.user_repo.get_all()
        print(f"Users: {users}")
        return [UserResponse.model_validate(user) for user in users]

    async def update_user(
        self, user_id: int, user_data: UserUpdate
    ) -> Optional[UserResponse]:
        """Update a user."""
        # Check if username is being changed and if it already exists
        if user_data.username:
            existing_user = await self.user_repo.get_by_username(user_data.username)
            if existing_user and existing_user.id != user_id:
                raise DMCPException("Username already exists")

        # Prepare update data
        update_data = {}
        if user_data.username is not None:
            update_data["username"] = user_data.username
        if user_data.first_name is not None:
            update_data["first_name"] = user_data.first_name
        if user_data.last_name is not None:
            update_data["last_name"] = user_data.last_name
        if user_data.roles is not None:
            update_data["roles"] = user_data.roles
        if user_data.password is not None:
            update_data["password"] = user_data.password

        if not update_data:
            return await self.get_user_by_id(user_id)

        user = await self.user_repo.update_user(user_id, **update_data)
        if user:
            return UserResponse.model_validate(user)
        return None

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        return await self.user_repo.delete(user_id)

    async def authenticate_user(self, login_data: UserLogin) -> Optional[UserResponse]:
        """Authenticate a user."""
        user = await self.user_repo.authenticate_user(
            login_data.username, login_data.password
        )
        if user:
            return UserResponse.model_validate(user)
        return None

    async def change_password(
        self, user_id: int, password_data: UserPasswordChange
    ) -> bool:
        """Change a user's password."""
        return await self.user_repo.change_password(
            user_id, password_data.current_password, password_data.new_password
        )

    async def get_users_by_role(self, role: str) -> List[UserResponse]:
        """Get all users with a specific role."""
        users = await self.user_repo.get_users_by_role(role)
        return [UserResponse.model_validate(user) for user in users]

    async def add_role_to_user(self, user_id: int, role: str) -> Optional[UserResponse]:
        """Add a role to a user."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        current_roles = user.roles_list
        if role not in current_roles:
            current_roles.append(role)
            updated_user = await self.user_repo.update_user(
                user_id, roles=current_roles
            )
            if updated_user:
                return UserResponse.model_validate(updated_user)

        return UserResponse.model_validate(user)

    async def remove_role_from_user(
        self, user_id: int, role: str
    ) -> Optional[UserResponse]:
        """Remove a role from a user."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        current_roles = user.roles_list
        if role in current_roles:
            current_roles.remove(role)
            updated_user = await self.user_repo.update_user(
                user_id, roles=current_roles
            )
            if updated_user:
                return UserResponse.model_validate(updated_user)

        return UserResponse.model_validate(user)
