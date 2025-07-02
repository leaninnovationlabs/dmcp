# Sample cURL Requests for Creating Queries

## 1. Simple Query (No Parameters)

```bash
curl -X POST "http://localhost:8000/queries/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_all_users",
    "description": "Simple query to get all users",
    "sql": "SELECT * FROM users",
    "datasource_id": 1
  }'
```

## 2. Query with Single Parameter

```bash
curl -X POST "http://localhost:8000/queries/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_users_by_status",
    "description": "Get users filtered by their status",
    "sql": "SELECT id, name, email, status FROM users WHERE status = :status",
    "datasource_id": 1,
    "parameters": [
      {
        "name": "status",
        "type": "string",
        "description": "User status to filter by",
        "required": true
      }
    ]
  }'
```

## 3. Complex Query with Multiple Parameters

```bash
curl -X POST "http://localhost:8000/queries/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "search_orders",
    "description": "Search orders with multiple filters",
    "sql": "SELECT o.id, o.order_date, o.total_amount, c.name as customer_name FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.order_date BETWEEN :start_date AND :end_date AND o.total_amount >= :min_amount",
    "datasource_id": 1,
    "parameters": [
      {
        "name": "start_date",
        "type": "date",
        "description": "Start date for order search",
        "required": true
      },
      {
        "name": "end_date",
        "type": "date", 
        "description": "End date for order search",
        "required": true
      },
      {
        "name": "min_amount",
        "type": "decimal",
        "description": "Minimum order amount",
        "required": false,
        "default": 0.0
      }
    ]
  }'
```

## 4. Using JSON File

```bash
curl -X POST "http://localhost:8000/queries/" \
  -H "Content-Type: application/json" \
  -d @sample_requests/create_query.json
```

## Response Format

Successful response will return:

```json
{
  "id": 1,
  "name": "get_users_by_status",
  "description": "Get users filtered by their status",
  "sql": "SELECT id, name, email, status FROM users WHERE status = :status",
  "datasource_id": 1,
  "parameters": [...],
  "created_at": "2025-07-02T00:00:00",
  "updated_at": "2025-07-02T00:00:00"
}
```

## Notes

- `datasource_id` must reference an existing datasource
- Parameter names in SQL must match the `:parameter_name` format
- The `parameters` field is optional if your query has no parameters
- Query names must be unique across the system 