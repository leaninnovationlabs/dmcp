#!/usr/bin/env python3
import requests
import json

# Test the API error handling
BASE_URL = "http://localhost:8000"

def test_error_responses():
    """Test that error responses return proper HTTP status codes"""
    
    # Test 1: Try to get a non-existent datasource (should return 404)
    print("Testing 404 error for non-existent datasource...")
    response = requests.get(f"{BASE_URL}/datasources/999999")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Test 2: Try to create a datasource with invalid data (should return 400)
    print("Testing 400 error for invalid datasource data...")
    invalid_data = {
        "name": "",  # Empty name should be invalid
        "database_type": "invalid_type",
        "host": "localhost",
        "port": 5432,
        "database_name": "test",
        "username": "test",
        "password": "test"
    }
    response = requests.post(f"{BASE_URL}/datasources", json=invalid_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Test 3: Try to execute a non-existent tool (should return 400 or 404)
    print("Testing error for non-existent tool execution...")
    response = requests.post(f"{BASE_URL}/execute/999999", json={"parameters": {}})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

if __name__ == "__main__":
    try:
        test_error_responses()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}") 