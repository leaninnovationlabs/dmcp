#!/usr/bin/env python3
"""
Simple test script to verify the /users/me endpoint is working.
"""

import json
import os
import sys

import requests

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.jwt_validator import jwt_validator


def test_users_me_endpoint():
    """Test the /users/me endpoint."""

    # API base URL
    base_url = "http://localhost:8000/dmcp"

    # Generate a test token
    payload = {
        "user_id": 1,  # Assuming user ID 1 exists
        "username": "test_user",
        "email": "test@example.com",
    }
    token = jwt_validator.create_token(payload)

    print("🔐 Testing /users/me endpoint")
    print("=" * 50)

    # Test 1: Without token (should fail)
    print("\n1. Testing without token...")
    try:
        response = requests.get(f"{base_url}/users/me")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejected without token")
        else:
            print("   ❌ Should have returned 401")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: With invalid token (should fail)
    print("\n2. Testing with invalid token...")
    try:
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{base_url}/users/me", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejected invalid token")
        else:
            print("   ❌ Should have returned 401")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: With valid token (should succeed)
    print("\n3. Testing with valid token...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/users/me", headers=headers)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("   ✅ Successfully retrieved user data")
            print(f"   User data: {json.dumps(data, indent=2)}")
        elif response.status_code == 404:
            print("   ⚠️  User not found (user ID 1 doesn't exist in database)")
            print("   This is expected if no user with ID 1 exists")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "=" * 50)
    print("Test completed!")
    print("\n💡 If you see a 404 error, it means user ID 1 doesn't exist.")
    print("   You can create a user first or modify the user_id in the payload.")


if __name__ == "__main__":
    test_users_me_endpoint()
