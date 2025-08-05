#!/usr/bin/env python3
"""
Test script for the new auth endpoint.
"""

import requests
import json
import sys

# Base URL for the API
BASE_URL = "http://localhost:8000/dbmcp"

def test_generate_token():
    """Test the token generation endpoint."""
    print("Testing token generation...")
    
    # Test payload
    test_payload = {
        "user_id": 123,
        "username": "testuser",
        "role": "admin",
        "custom_field": "custom_value"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth",
            json={"payload": test_payload},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            token = response.json()["data"]["token"]
            print(f"\n✅ Token generated successfully!")
            print(f"Token: {token[:50]}...")
            return token
        else:
            print(f"\n❌ Token generation failed!")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_validate_token(token):
    """Test the token validation endpoint."""
    if not token:
        print("No token to validate")
        return
    
    print("\nTesting token validation...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/validate",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ Token validation successful!")
            payload = response.json()["data"]["payload"]
            print(f"Decoded payload: {json.dumps(payload, indent=2)}")
        else:
            print(f"\n❌ Token validation failed!")
            
    except Exception as e:
        print(f"Error: {e}")

def test_invalid_token():
    """Test with an invalid token."""
    print("\nTesting invalid token...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/validate",
            headers={
                "Authorization": "Bearer invalid_token_here",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            print("\n✅ Invalid token correctly rejected!")
        else:
            print(f"\n❌ Invalid token not properly handled!")
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all tests."""
    print("🚀 Testing Auth Endpoint")
    print("=" * 50)
    
    # Test 1: Generate token
    token = test_generate_token()
    
    # Test 2: Validate valid token
    test_validate_token(token)
    
    # Test 3: Validate invalid token
    test_invalid_token()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main() 