from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DMCPException
from app.models.database import User
from app.models.schemas import UserCreate, UserLogin, UserPasswordChange, UserUpdate
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_repo(mock_db):
    """User repository with mock database."""
    return UserRepository(mock_db)


@pytest.fixture
def user_service(mock_db):
    """User service with mock database."""
    return UserService(mock_db)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "roles": ["user"],
    }


@pytest.fixture
def sample_user():
    """Sample user model instance."""
    return User(
        id=1,
        username="testuser",
        password="encrypted_password",
        first_name="Test",
        last_name="User",
        roles="user",
    )


class TestUserRepository:
    """Test cases for UserRepository."""

    @pytest.mark.asyncio
    async def test_create_user(self, user_repo, sample_user_data):
        """Test creating a user."""
        # Mock the create method from base repository
        user_repo.create = AsyncMock(return_value=User(**sample_user_data, id=1))

        user = await user_repo.create_user(
            username=sample_user_data["username"],
            password=sample_user_data["password"],
            first_name=sample_user_data["first_name"],
            last_name=sample_user_data["last_name"],
            roles=sample_user_data["roles"],
        )

        assert user.username == sample_user_data["username"]
        assert user.first_name == sample_user_data["first_name"]
        assert user.last_name == sample_user_data["last_name"]
        assert user.roles == "user"  # Should be stored as comma-separated string
        assert user.id == 1

    @pytest.mark.asyncio
    async def test_get_by_username(self, user_repo, sample_user):
        """Test getting user by username."""
        user_repo.db.execute = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        user_repo.db.execute.return_value = mock_result

        user = await user_repo.get_by_username("testuser")

        assert user == sample_user
        assert user.username == "testuser"

    @pytest.mark.asyncio
    async def test_username_exists(self, user_repo):
        """Test checking if username exists."""
        # Test when username exists
        user_repo.get_by_username = AsyncMock(
            return_value=User(id=1, username="testuser")
        )
        assert await user_repo.username_exists("testuser") is True

        # Test when username doesn't exist
        user_repo.get_by_username = AsyncMock(return_value=None)
        assert await user_repo.username_exists("nonexistent") is False


class TestUserService:
    """Test cases for UserService."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, sample_user_data):
        """Test successful user creation."""
        user_service.user_repo.username_exists = AsyncMock(return_value=False)
        user_service.user_repo.create_user = AsyncMock(
            return_value=User(**sample_user_data, id=1)
        )

        user_data = UserCreate(**sample_user_data)
        user = await user_service.create_user(user_data)

        assert user.username == sample_user_data["username"]
        assert user.first_name == sample_user_data["first_name"]
        assert user.last_name == sample_user_data["last_name"]
        assert user.roles == sample_user_data["roles"]

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, user_service, sample_user_data):
        """Test creating user with duplicate username."""
        user_service.user_repo.username_exists = AsyncMock(return_value=True)

        user_data = UserCreate(**sample_user_data)

        with pytest.raises(DMCPException, match="Username already exists"):
            await user_service.create_user(user_data)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, user_service):
        """Test successful user authentication."""
        mock_user = User(
            id=1,
            username="testuser",
            password="encrypted_password",
            first_name="Test",
            last_name="User",
            roles="user",
        )

        user_service.user_repo.authenticate_user = AsyncMock(return_value=mock_user)

        login_data = UserLogin(username="testuser", password="testpassword")
        user = await user_service.authenticate_user(login_data)

        assert user is not None
        assert user.username == "testuser"

    @pytest.mark.asyncio
    async def test_authenticate_user_failure(self, user_service):
        """Test failed user authentication."""
        user_service.user_repo.authenticate_user = AsyncMock(return_value=None)

        login_data = UserLogin(username="testuser", password="wrongpassword")
        user = await user_service.authenticate_user(login_data)

        assert user is None

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_service, sample_user):
        """Test successful user update."""
        user_service.user_repo.get_by_username = AsyncMock(return_value=None)
        user_service.user_repo.update_user = AsyncMock(return_value=sample_user)

        update_data = UserUpdate(first_name="Updated")
        user = await user_service.update_user(1, update_data)

        assert user is not None
        assert user.first_name == "Updated"

    @pytest.mark.asyncio
    async def test_add_role_to_user(self, user_service, sample_user):
        """Test adding role to user."""
        user_service.user_repo.get_by_id = AsyncMock(return_value=sample_user)
        user_service.user_repo.update_user = AsyncMock(return_value=sample_user)

        user = await user_service.add_role_to_user(1, "admin")

        assert user is not None
        assert "admin" in user.roles

    @pytest.mark.asyncio
    async def test_remove_role_from_user(self, user_service, sample_user):
        """Test removing role from user."""
        sample_user.roles = "user,admin"
        user_service.user_repo.get_by_id = AsyncMock(return_value=sample_user)
        user_service.user_repo.update_user = AsyncMock(return_value=sample_user)

        user = await user_service.remove_role_from_user(1, "admin")

        assert user is not None
        assert "admin" not in user.roles
        assert "user" in user.roles


class TestUserSchemas:
    """Test cases for User Pydantic schemas."""

    def test_user_create_schema(self, sample_user_data):
        """Test UserCreate schema validation."""
        user_data = UserCreate(**sample_user_data)

        assert user_data.username == "testuser"
        assert user_data.password == "testpassword123"
        assert user_data.first_name == "Test"
        assert user_data.last_name == "User"
        assert user_data.roles == ["user"]

    def test_user_update_schema(self):
        """Test UserUpdate schema validation."""
        update_data = UserUpdate(first_name="Updated", roles=["admin"])

        assert update_data.first_name == "Updated"
        assert update_data.roles == ["admin"]
        assert update_data.username is None
        assert update_data.password is None
        assert update_data.last_name is None

    def test_user_login_schema(self):
        """Test UserLogin schema validation."""
        login_data = UserLogin(username="testuser", password="testpassword")

        assert login_data.username == "testuser"
        assert login_data.password == "testpassword"

    def test_user_password_change_schema(self):
        """Test UserPasswordChange schema validation."""
        password_data = UserPasswordChange(
            current_password="oldpass", new_password="newpass"
        )

        assert password_data.current_password == "oldpass"
        assert password_data.new_password == "newpass"
