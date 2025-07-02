#!/usr/bin/env python3
"""
Test script to verify standardized API responses.
"""

import requests
import json
import time
import pytest
from fastapi.testclient import TestClient
from app.main import app

BASE_URL = "http://localhost:8000"

client = TestClient(app)

class TestStandardizedResponses:
    """Test cases for standardized API responses."""
    
    def test_health_endpoint_success(self):
        """Test health endpoint returns success response."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["errors"] is None
    
    def test_datasource_endpoints_success(self):
        """Test datasource endpoints return success responses."""
        # Test list datasources
        response = client.get("/datasources/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["errors"] is None
    
    def test_datasource_endpoints_error(self):
        """Test datasource endpoints return error responses."""
        # Test get non-existent datasource
        response = client.get("/datasources/999")
        assert response.status_code == 200  # API returns 200 with error in response
        
        data = response.json()
        assert data["success"] is False
        assert "errors" in data
        assert len(data["errors"]) > 0
    
    def test_tool_endpoints_success(self):
        """Test tool endpoints return success responses."""
        # Test list tools
        response = client.get("/tools/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["errors"] is None
    
    def test_tool_endpoints_error(self):
        """Test tool endpoints return error responses."""
        # Test get non-existent tool
        response = client.get("/tools/999")
        assert response.status_code == 200  # API returns 200 with error in response
        
        data = response.json()
        assert data["success"] is False
        assert "errors" in data
        assert len(data["errors"]) > 0
    
    def test_execute_endpoints_error(self):
        """Test execute endpoints return error responses."""
        # Test execute non-existent tool
        response = client.post("/execute/999", json={"parameters": {}})
        assert response.status_code == 200  # API returns 200 with error in response
        
        data = response.json()
        assert data["success"] is False
        assert "errors" in data
        assert len(data["errors"]) > 0
    
    def test_response_structure_consistency(self):
        """Test that all endpoints return consistent response structure."""
        endpoints = [
            ("GET", "/health", None, "Health Check"),
            ("GET", "/datasources/", None, "List Datasources"),
            ("GET", "/datasources/999", None, "Get Non-existent Datasource (Error)"),
            ("GET", "/tools/", None, "List Tools"),
            ("GET", "/tools/999", None, "Get Non-existent Tool (Error)"),
        ]
        
        for method, endpoint, data, description in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json=data or {})
            
            assert response.status_code == 200, f"Failed for {description}"
            
            response_data = response.json()
            
            # Check required fields
            assert "success" in response_data, f"Missing 'success' field in {description}"
            assert isinstance(response_data["success"], bool), f"'success' must be boolean in {description}"
            
            # Check that either data or errors is present (but not both)
            if response_data["success"]:
                assert "data" in response_data, f"Missing 'data' field in successful response for {description}"
                assert response_data["errors"] is None, f"Errors should be None in successful response for {description}"
            else:
                assert "errors" in response_data, f"Missing 'errors' field in error response for {description}"
                assert isinstance(response_data["errors"], list), f"'errors' must be list in {description}"
                assert len(response_data["errors"]) > 0, f"Errors list should not be empty in {description}"
                assert response_data["data"] is None, f"Data should be None in error response for {description}"

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