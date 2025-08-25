# Datasource API Tests

This directory contains comprehensive unit tests for the datasource API endpoints using pytest framework. **Tests use real HTTP requests to `http://localhost:8000`**.

## Test Files

### `test_datasource_endpoints.py`
Focused test file that specifically tests the two main requirements:
1. **Create a new data source** using PostgreSQL configuration from `.test.env`
2. **Test connection** to the created data source

### `test_datasource_api.py`
Comprehensive test file with full coverage of all datasource API endpoints:
- Create datasource (success and failure cases)
- List datasources
- Get datasource by ID
- Update datasource
- Delete datasource
- Test connection
- Authentication tests

### `conftest.py`
Pytest configuration and fixtures for test setup.

### `run_datasource_tests.py`
Simple test runner script for easy execution.

## Prerequisites

1. **API Server**: Ensure the API server is running at `http://localhost:8000`
2. **PostgreSQL Database**: Ensure PostgreSQL is running and accessible
3. **Test Database**: Create a test database (default: `test_db`)
4. **Environment File**: Ensure `.test.env` exists with proper configuration
5. **Dependencies**: Install test dependencies using `uv`

## Configuration

The tests use the PostgreSQL configuration from `tests/.test.env`:

```env
TEST_DB_HOST=localhost
TEST_DB_PORT=5432
TEST_DB_NAME=test_db
TEST_DB_USER=postgres
TEST_DB_PASSWORD=password
TEST_DB_URL=postgresql://postgres:password@localhost:5432/test_db
TEST_DB_SSL_MODE=disable
TEST_DB_POOL_SIZE=5
TEST_DB_MAX_OVERFLOW=10
APP_TOKEN=your_jwt_token_here
```

## Starting the API Server

Before running tests, start the API server:

```bash
# Option 1: Using uvicorn directly
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using the provided script
python api_run.py
```

## Running Tests

### Option 1: Using the test runner script (recommended)
```bash
# From project root
python tests/run_datasource_tests.py

# From tests directory
python run_datasource_tests.py
```

### Option 2: Using pytest directly
```bash
# Run focused tests
pytest tests/test_datasource_endpoints.py -v -s

# Run all datasource tests
pytest tests/ -k "datasource" -v -s

# From tests directory
pytest test_datasource_endpoints.py -v -s
```

### Option 3: Run all datasource tests
```bash
# From project root
pytest tests/ -k "datasource" -v -s

# From tests directory
pytest -k "datasource" -v -s
```

## Test Coverage

### Main Requirements (test_datasource_endpoints.py)

1. **test_1_create_datasource_with_postgres_config**
   - Creates a datasource using PostgreSQL config from `.test.env`
   - Validates response structure and data
   - Stores datasource ID for connection test

2. **test_2_test_connection_to_created_datasource**
   - Tests connection to the datasource created in test 1
   - Validates connection response structure
   - Handles both success and failure scenarios

3. **test_3_integration_test_create_and_connect**
   - Integration test that creates a datasource and immediately tests connection
   - Demonstrates end-to-end workflow

4. **test_4_health_check**
   - Verifies API server is running and accessible
   - Tests health endpoint

### Comprehensive Coverage (test_datasource_api.py)

- **Authentication**: Tests with and without valid JWT tokens
- **CRUD Operations**: Create, Read, Update, Delete datasources
- **Connection Testing**: Test database connections with valid and invalid credentials
- **Error Handling**: Invalid data, nonexistent resources, authentication failures
- **Response Validation**: Ensures proper API response structure

## Test Output

The tests provide detailed output including:
- Configuration being used
- API request details and URLs
- Response validation
- Connection test results
- Success/failure status with timing information

Example output:
```
============================================================
TEST 1: Creating datasource with PostgreSQL config from .test.env
============================================================
📋 Using config: {'name': 'Test PostgreSQL Database', ...}
🚀 Making API request to create datasource...
🌐 URL: http://localhost:8000/dmcp/datasources
📊 Response: {'success': True, 'data': {...}}
✅ Successfully created datasource with ID: 1

============================================================
TEST 2: Testing connection to the created datasource
============================================================
🔗 Testing connection to datasource ID: 1
🌐 URL: http://localhost:8000/dmcp/datasources/1/test
📊 Connection test response: {'success': True, 'data': {...}}
✅ Connection test successful!
⏱️  Connection time: 150.5ms
📝 Message: Connection successful
```

## Key Differences from Mock Testing

- **Real HTTP Requests**: Tests make actual HTTP requests to `http://localhost:8000`
- **Server Dependency**: API server must be running before tests
- **Network Testing**: Tests real network connectivity and server responses
- **Database Integration**: Tests actual database connections and operations
- **Authentication**: Uses real JWT token validation

## Troubleshooting

### Common Issues

1. **API Server Not Running**
   ```bash
   # Start the server first
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Database Connection Failed**
   - Ensure PostgreSQL is running
   - Verify database credentials in `.test.env`
   - Check if test database exists

3. **Authentication Errors**
   - Ensure JWT token is valid in `.test.env`
   - Check token expiration

4. **Network Connection Issues**
   - Verify server is accessible at `http://localhost:8000`
   - Check firewall settings
   - Ensure no other service is using port 8000

5. **Import Errors**
   - Ensure you're running from the correct directory
   - Verify Python path includes the app directory

6. **Test Dependencies**
   - Install test dependencies: `uv add --dev pytest pytest-asyncio httpx`
   - Ensure all required packages are installed

### Debug Mode

Run tests with additional debugging:
```bash
pytest tests/test_datasource_endpoints.py -v -s --tb=long
```

### Server Health Check

The test runner automatically checks if the server is running:
```bash
python tests/run_datasource_tests.py
```

## Test Structure

```
tests/
├── test_datasource_endpoints.py    # Main focused tests
├── test_datasource_api.py          # Comprehensive tests
├── conftest.py                     # Pytest configuration
├── run_datasource_tests.py         # Test runner
├── .test.env                       # Test environment config
└── README_datasource_tests.md      # This file
```

## API Endpoints Tested

- `POST /dmcp/datasources` - Create datasource
- `GET /dmcp/datasources` - List datasources
- `GET /dmcp/datasources/{id}` - Get specific datasource
- `PUT /dmcp/datasources/{id}` - Update datasource
- `DELETE /dmcp/datasources/{id}` - Delete datasource
- `POST /dmcp/datasources/{id}/test` - Test connection
- `GET /dmcp/health` - Health check

All endpoints are tested with proper authentication and error handling using real HTTP requests. 