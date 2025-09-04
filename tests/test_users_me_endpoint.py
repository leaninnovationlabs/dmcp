#!/usr/bin/env python3
"""
Test script to verify the /users/me endpoint is working correctly.
This script tests the endpoint to ensure it returns the current user's information.
"""

import os
import sys
import httpx
import pytest

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.jwt_validator import jwt_validator


class TestUsersMeEndpoint:
    """Test class for /users/me endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        # Load test environment variables
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), '.test.env'))
        
        # API base URL
        self.base_url = "http://localhost:8000"
        
        # Generate test token with user_id that should exist in the database
        payload = {
            "user_id": 1,  # Assuming user ID 1 exists
            "username": "test_user",
            "email": "test@example.com"
        }
        self.test_token = jwt_validator.create_token(payload)
        self.headers = {"Authorization": f"Bearer {self.test_token}"}
        
        # Create HTTP client
        self.client = httpx.Client(timeout=30.0)
    
    def test_users_me_with_valid_token(self):
        """Test /users/me endpoint with valid authentication token."""
        try:
            # Make API request
            response = self.client.get(
                f"{self.base_url}/dmcp/users/me",
                headers=self.headers
            )
            
            # Assert response
            assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
            
            data = response.json()
            assert data["success"] is True, f"Expected success=True, got {data.get('success')}"
            assert "data" in data, "Response should contain 'data' field"
            
            user_data = data["data"]
            assert "id" in user_data, "User data should contain 'id' field"
            assert "username" in user_data, "User data should contain 'username' field"
            assert "first_name" in user_data, "User data should contain 'first_name' field"
            assert "last_name" in user_data, "User data should contain 'last_name' field"
            
            print(f"✅ /users/me endpoint working correctly!")
            print(f"User data: {user_data}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
    
    def test_users_me_without_token(self):
        """Test /users/me endpoint without authentication token."""
        try:
            # Make API request without token
            response = self.client.get(f"{self.base_url}/dmcp/users/me")
            
            # Should return 401 Unauthorized
            assert response.status_code == 401, f"Expected 401, got {response.status_code}"
            
            data = response.json()
            assert "detail" in data, "Error response should contain 'detail' field"
            
            print(f"✅ /users/me endpoint correctly rejects requests without token!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
    
    def test_users_me_with_invalid_token(self):
        """Test /users/me endpoint with invalid authentication token."""
        try:
            # Make API request with invalid token
            invalid_headers = {"Authorization": "Bearer invalid_token_here"}
            response = self.client.get(
                f"{self.base_url}/dmcp/users/me",
                headers=invalid_headers
            )
            
            # Should return 401 Unauthorized
            assert response.status_code == 401, f"Expected 401, got {response.status_code}"
            
            data = response.json()
            assert "detail" in data, "Error response should contain 'detail' field"
            
            print(f"✅ /users/me endpoint correctly rejects requests with invalid token!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise


def main():
    """Main test function."""
    print("🔐 /users/me Endpoint Test")
    print("=" * 50)
    
    # Create test instance
    test_instance = TestUsersMeEndpoint()
    test_instance.setup()
    
    try:
        # Run tests
        test_instance.test_users_me_without_token()
        test_instance.test_users_me_with_invalid_token()
        test_instance.test_users_me_with_valid_token()
        
        print("\n✅ All tests passed! /users/me endpoint is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        print("\n💡 Make sure:")
        print("   1. The server is running on http://localhost:8000")
        print("   2. There's a user with ID 1 in the database")
        print("   3. The authentication middleware is properly configured")


if __name__ == "__main__":
    main()
