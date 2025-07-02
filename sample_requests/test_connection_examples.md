# Sample cURL Requests for Testing Database Connections

## Test Connection by Datasource ID

```bash
curl -X POST "http://localhost:8000/datasources/1/test" \
  -H "Content-Type: application/json"
```

## Response Format

### Successful Connection
```json
{
  "success": true,
  "message": "Successfully connected to sqlite database './test.db'",
  "connection_time_ms": 15.5,
  "error": null
}
```

### Failed Connection
```json
{
  "success": false,
  "message": "Failed to connect to database",
  "connection_time_ms": 5.2,
  "error": "Connection refused: database './invalid.db' not found"
}
```

### Datasource Not Found
```json
{
  "detail": "Datasource with ID 999 not found"
}
```

## Notes

- Replace `1` in the URL with the actual datasource ID you want to test
- The endpoint performs a simple `SELECT 1` query to verify the connection
- Connection time is measured in milliseconds
- The test is safe and doesn't modify any data
- Works with all supported database types (SQLite, PostgreSQL, MySQL)

## Testing Different Database Types

### SQLite
```bash
curl -X POST "http://localhost:8000/datasources/1/test"
```

### PostgreSQL
```bash
curl -X POST "http://localhost:8000/datasources/2/test"
```

### MySQL
```bash
curl -X POST "http://localhost:8000/datasources/3/test"
```

## Use Cases

1. **Validate datasource configuration** before creating queries
2. **Troubleshoot connection issues** when queries fail
3. **Monitor database availability** in production environments
4. **Test credentials** and connection parameters 