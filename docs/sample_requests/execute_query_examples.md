# Sample cURL Requests for Executing Named Queries

## 1. Execute Query Without Parameters

```bash
curl -X POST "http://localhost:8000/execute/1" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {},
    "pagination": {
      "page": 1,
      "page_size": 10
    }
  }'
```

## 2. Execute Query With Parameters

```bash
curl -X POST "http://localhost:8000/execute/1" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "status": "active"
    },
    "pagination": {
      "page": 1,
      "page_size": 20
    }
  }'
```

## 3. Execute Query With Multiple Parameters

```bash
curl -X POST "http://localhost:8000/execute/2" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "start_date": "2025-01-01",
      "end_date": "2025-12-31",
      "min_amount": 100.00,
      "status": "completed"
    },
    "pagination": {
      "page": 1,
      "page_size": 50
    }
  }'
```

## 4. Execute Query Without Pagination

```bash
curl -X POST "http://localhost:8000/execute/1" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "status": "active"
    }
  }'
```

## 5. Execute Query With Pagination Only

```bash
curl -X POST "http://localhost:8000/execute/1" \
  -H "Content-Type: application/json" \
  -d '{
    "pagination": {
      "page": 2,
      "page_size": 5
    }
  }'
```

## 6. Minimal Request (No Parameters, No Pagination)

```bash
curl -X POST "http://localhost:8000/execute/1" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Response Format

Successful response will return:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "status": "active",
      "created_at": "2025-01-15T10:30:00"
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "email": "jane@example.com",
      "status": "active",
      "created_at": "2025-01-16T14:20:00"
    }
  ],
  "columns": ["id", "name", "email", "status", "created_at"],
  "row_count": 2,
  "execution_time_ms": 15.5,
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_items": 25,
    "total_pages": 3,
    "has_next": true,
    "has_previous": false
  }
}
```

## Error Response Format

```json
{
  "success": false,
  "data": [],
  "columns": [],
  "row_count": 0,
  "execution_time_ms": 5.2,
  "error": "Query with ID 999 not found"
}
```

## Notes

- Replace `1` or `2` in the URL with the actual query ID you want to execute
- `parameters` should match the parameter names defined in the query (using `:parameter_name` format)
- `pagination` is optional - if not provided, all results will be returned
- `page` starts from 1 (not 0)
- `page_size` can be between 1 and 1000
- The response includes execution time in milliseconds
- If pagination is requested, the response includes pagination metadata 