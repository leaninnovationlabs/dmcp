#!/usr/bin/env python3
"""
Test script to verify standardized API responses.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_response_format(response_data, endpoint_name):
    """Test if response follows the standardized format."""
    required_fields = ["data", "success", "errors", "warnings"]
    
    print(f"\nTesting {endpoint_name}:")
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    # Check if all required fields are present
    for field in required_fields:
        if field not in response_data:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Check if errors and warnings are lists
    if not isinstance(response_data["errors"], list):
        print(f"❌ 'errors' field is not a list")
        return False
    
    if not isinstance(response_data["warnings"], list):
        print(f"❌ 'warnings' field is not a list")
        return False
    
    # Check if success is boolean
    if not isinstance(response_data["success"], bool):
        print(f"❌ 'success' field is not a boolean")
        return False
    
    print(f"✅ {endpoint_name} response format is correct")
    return True

def test_endpoints():
    """Test all endpoints for standardized response format."""
    endpoints = [
        ("GET", "/health", None, "Health Check"),
        ("GET", "/datasources/", None, "List Datasources"),
        ("GET", "/queries/", None, "List Queries"),
        ("GET", "/datasources/999", None, "Get Non-existent Datasource (Error)"),
        ("GET", "/queries/999", None, "Get Non-existent Query (Error)"),
    ]
    
    all_passed = True
    
    for method, path, data, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{path}")
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{path}", json=data)
            
            if response.status_code == 200:
                response_data = response.json()
                if not test_response_format(response_data, name):
                    all_passed = False
            else:
                print(f"❌ {name} returned status code {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error testing {name}: {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("Testing standardized API responses...")
    print("Make sure the server is running on http://localhost:8000")
    
    # Wait a moment for server to start if needed
    time.sleep(1)
    
    success = test_endpoints()
    
    if success:
        print("\n🎉 All endpoints return standardized responses!")
    else:
        print("\n❌ Some endpoints failed the standardized response test") 