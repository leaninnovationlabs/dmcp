#!/usr/bin/env python3
"""
Test runner for datasource API endpoint tests.
This script runs the focused datasource tests against http://localhost:8000
"""

import os
import sys
import subprocess
import pytest
import httpx

def check_server_running():
    """Check if the API server is running at localhost:8000."""
    try:
        response = httpx.get("http://localhost:8000/dbmcp/health", timeout=5.0)
        return response.status_code == 200
    except httpx.ConnectError:
        return False

def main():
    """Run the datasource API tests."""
    print("🧪 Running Datasource API Tests")
    print("=" * 50)
    
    # Change to the tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(tests_dir)
    
    # Check if .test.env exists
    test_env_path = os.path.join(tests_dir, '.test.env')
    if not os.path.exists(test_env_path):
        print("❌ Error: .test.env file not found in tests directory")
        print("Please ensure the test environment file exists with PostgreSQL configuration")
        return 1
    
    print("✅ Found .test.env file")
    
    # Check if we're in the right directory
    if not os.path.exists('../app'):
        print("❌ Error: app directory not found")
        print("Please run this script from the project root or tests directory")
        return 1
    
    print("✅ Found app directory")
    
    # Check if API server is running
    print("🔍 Checking if API server is running at http://localhost:8000...")
    if not check_server_running():
        print("❌ Error: API server is not running at http://localhost:8000")
        print("Please start the server first with:")
        print("  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("  or")
        print("  python api_run.py")
        return 1
    
    print("✅ API server is running at http://localhost:8000")
    
    # Run the focused datasource tests
    test_file = "test_datasource_endpoints.py"
    
    if not os.path.exists(test_file):
        print(f"❌ Error: {test_file} not found")
        return 1
    
    print(f"✅ Found test file: {test_file}")
    print("\n🚀 Running tests against http://localhost:8000...")
    print("=" * 50)
    
    # Run pytest with verbose output and show print statements
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        test_file, 
        "-v", 
        "-s", 
        "--tb=short"
    ], cwd=tests_dir)
    
    print("\n" + "=" * 50)
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        print("\n💡 Tips:")
        print("   - Make sure PostgreSQL is running")
        print("   - Check that the database credentials in .test.env are correct")
        print("   - Ensure the test database exists")
        print("   - Verify the API server is running at http://localhost:8000")
        print("   - Check server logs for any errors")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(main()) 