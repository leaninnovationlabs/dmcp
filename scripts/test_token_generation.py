#!/usr/bin/env python3
"""
Test script for token generation endpoint
"""

import os
import sys

import requests

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))


def test_token_generation():
    """Test the token generation endpoint"""

    # Configuration
    base_url = "http://localhost:8000/dmcp"

    # First, login to get a token
    login_data = {"username": "admin", "password": "admin123"}

    print("1. Logging in to get authentication token...")
    try:
        login_response = requests.post(f"{base_url}/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code}")
            print(login_response.text)
            return False

        login_result = login_response.json()
        if not login_result.get("success"):
            print("Login failed: Invalid response")
            print(login_result)
            return False

        auth_token = login_result["data"]["token"]
        print(f"✓ Login successful. Got token: {auth_token[:20]}...")

    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

    # Now test token generation
    print("\n2. Testing token generation endpoint...")
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }

    try:
        token_response = requests.post(
            f"{base_url}/users/me/generate-token", headers=headers
        )

        if token_response.status_code != 200:
            print(f"❌ Token generation failed: {token_response.status_code}")
            print(token_response.text)
            return False

        token_result = token_response.json()
        if not token_result.get("success"):
            print("❌ Token generation failed: Invalid response")
            print(token_result)
            return False

        new_token_data = token_result["data"]
        print("✓ Token generation successful!")
        print(f"   - New token: {new_token_data['token'][:20]}...")
        print(f"   - User: {new_token_data['username']}")
        print(f"   - User ID: {new_token_data['user_id']}")
        print(f"   - Expires at: {new_token_data['expires_at']}")

        # Test that the new token works
        print("\n3. Testing new token validity...")
        new_headers = {
            "Authorization": f"Bearer {new_token_data['token']}",
            "Content-Type": "application/json",
        }

        me_response = requests.get(f"{base_url}/users/me", headers=new_headers)
        if me_response.status_code == 200:
            print("✓ New token is valid and can be used for API calls")
        else:
            print("❌ New token validation failed")
            print(me_response.text)
            return False

        return True

    except Exception as e:
        print(f"❌ Token generation error: {e}")
        return False


if __name__ == "__main__":
    print("Testing Token Generation Endpoint")
    print("=" * 40)

    success = test_token_generation()

    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)
