#!/usr/bin/env python3
"""
Script to test user creation and database functionality.
This script creates a test user and verifies the user table is working.
"""

import asyncio
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import get_db
from app.models.schemas import UserCreate
from app.services.user_service import UserService


async def test_user_creation():
    """Test creating a user and basic operations."""
    print("Testing user creation and database functionality...")

    try:
        # Get database session
        async for db in get_db():
            user_service = UserService(db)

            # Test data
            test_user_data = UserCreate(
                username="testadmin",
                password="securepassword123",
                first_name="Test",
                last_name="Admin",
                roles=["admin", "user"],
            )

            print(f"Creating user: {test_user_data.username}")

            # Create user
            user = await user_service.create_user(test_user_data)

            print("✅ User created successfully!")
            print(f"   ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Name: {user.first_name} {user.last_name}")
            print(f"   Roles: {user.roles}")
            print(f"   Created: {user.created_at}")

            # Test retrieving the user
            print("\nTesting user retrieval...")
            retrieved_user = await user_service.get_user_by_id(user.id)

            if retrieved_user:
                print("✅ User retrieved successfully!")
                print(f"   Username: {retrieved_user.username}")
                print(f"   Roles: {retrieved_user.roles}")
            else:
                print("❌ Failed to retrieve user")

            # Test authentication
            print("\nTesting user authentication...")
            from app.models.schemas import UserLogin

            login_data = UserLogin(username="testadmin", password="securepassword123")

            authenticated_user = await user_service.authenticate_user(login_data)

            if authenticated_user:
                print("✅ User authenticated successfully!")
                print(f"   Username: {authenticated_user.username}")
            else:
                print("❌ User authentication failed")

            # Test getting all users
            print("\nTesting get all users...")
            all_users = await user_service.get_all_users()
            print(f"✅ Found {len(all_users)} users in database")

            for u in all_users:
                print(f"   - {u.username} ({u.first_name} {u.last_name}) - Roles: {u.roles}")

            break  # Exit the async generator

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n🎉 All tests completed successfully!")
    return True


async def main():
    """Main function to run the test."""
    print("=" * 60)
    print("DMCP User Management Test Script")
    print("=" * 60)

    success = await test_user_creation()

    if success:
        print("\n✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
