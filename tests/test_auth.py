#!/usr/bin/env python3
"""
Test script to verify Bearer token authentication is working correctly.
This script tests various scenarios to ensure the middleware is functioning properly.
"""

import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.core.jwt_validator import jwt_validator


def generate_test_token():
    """Generate a test JWT token for authentication testing."""
    payload = {"user_id": 123, "username": "test_user", "email": "test@example.com"}
    return jwt_validator.create_token(payload)


def test_token_generation():
    """Test that we can generate and validate tokens correctly."""
    print("Testing token generation and validation...")

    # Generate a test token
    token = generate_test_token()
    print(f"Generated token: {token[:50]}..." if len(token) > 50 else f"Generated token: {token}")

    # Test validation
    try:
        payload = jwt_validator.validate_token(f"Bearer {token}")
        print(f"✅ Token validation successful: {payload}")
        return token
    except Exception as e:
        print(f"❌ Token validation failed: {e}")
        return None


def print_curl_examples(token):
    """Print example curl commands for testing the API."""
    print("\n" + "=" * 60)
    print("CURL EXAMPLES FOR TESTING")
    print("=" * 60)

    base_url = "http://localhost:8000/dmcp"

    print("\n🏥 1. Test health endpoint (should work WITHOUT token):")
    print(f'curl -X GET "{base_url}/health"')

    print("\n❌ 2. Test tools endpoint WITHOUT token (should fail with 401):")
    print(f'curl -X GET "{base_url}/tools"')

    print("\n✅ 3. Test tools endpoint WITH valid token (should work):")
    print(f'curl -X GET "{base_url}/tools" \\')
    print(f'  -H "Authorization: Bearer {token}"')

    print("\n✅ 4. Test datasources endpoint WITH valid token (should work):")
    print(f'curl -X GET "{base_url}/datasources" \\')
    print(f'  -H "Authorization: Bearer {token}"')

    print("\n❌ 5. Test with invalid token (should fail with 401):")
    print(f'curl -X GET "{base_url}/tools" \\')
    print('  -H "Authorization: Bearer invalid_token_here"')

    print("\n❌ 6. Test with malformed header (should fail with 401):")
    print(f'curl -X GET "{base_url}/tools" \\')
    print(f'  -H "Authorization: {token}"')  # Missing "Bearer " prefix


def main():
    """Main test function."""
    print("🔐 Bearer Token Authentication Test")
    print("=" * 50)

    # Test token generation
    token = test_token_generation()

    if token:
        print("\n✅ Authentication setup appears to be working correctly!")
        print_curl_examples(token)

        print("\n" + "=" * 60)
        print("EXPECTED BEHAVIOR:")
        print("=" * 60)
        print("✅ /dmcp/health - Should work without token")
        print("❌ /dmcp/tools - Should return 401 without token")
        print("❌ /dmcp/datasources - Should return 401 without token")
        print("❌ /dmcp/execute/* - Should return 401 without token")
        print("✅ All endpoints - Should work with valid Bearer token")
        print("\n💡 Start your server with: python -m uvicorn app.main:app --reload")
        print("💡 Then test the endpoints using the curl examples above")

    else:
        print("\n❌ Authentication setup has issues. Please check the configuration.")


if __name__ == "__main__":
    main()
