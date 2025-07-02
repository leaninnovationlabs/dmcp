# Jinja Template Examples for SQL Queries

This document provides practical examples of using Jinja templates in SQL queries with the DBMCP API.

## Example 1: Simple Variable Substitution

### Create a Query with Template

```bash
curl -X POST "http://localhost:8000/queries" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Get User by ID",
    "description": "Get user details by ID using Jinja template",
    "sql": "SELECT * FROM users WHERE id = {{ user_id }}",
    "datasource_id": 1
  }'
```

### Execute the Query

```bash
curl -X POST "http://localhost:8000/execute/query/1" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "user_id": 123
    }
  }'
```

**Expected Result:**
```sql
SELECT * FROM users WHERE id = 123;
```

## Example 2: Conditional Logic

### Create a Query with Conditional Filters

```bash
curl -X POST "http://localhost:8000/queries" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Search Users with Filters",
    "description": "Search users with optional filters using Jinja conditionals",
    "sql": "SELECT * FROM users WHERE 1=1 {% if user_id %} AND id = {{ user_id }} {% endif %} {% if name %} AND name = {{ name }} {% endif %} {% if email %} AND email = {{ email }} {% endif %}",
    "datasource_id": 1
  }'
```

### Execute with All Parameters

```bash
curl -X POST "http://localhost:8000/execute/query/2" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "user_id": 123,
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

**Expected Result:**
```sql
SELECT * FROM users WHERE 1=1 AND id = 123 AND name = 'John Doe' AND email = 'john@example.com';
```

### Execute with Partial Parameters

```bash
curl -X POST "http://localhost:8000/execute/query/2" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "name": "John Doe"
    }
  }'
```

**Expected Result:**
```sql
SELECT * FROM users WHERE 1=1 AND name = 'John Doe';
```

## Example 3: IN Clause with Lists

### Create a Query with IN Clause

```bash
curl -X POST "http://localhost:8000/queries" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Get Users by IDs",
    "description": "Get multiple users by their IDs using sql_in filter",
    "sql": "SELECT * FROM users WHERE id IN {{ user_ids | sql_in }}",
    "datasource_id": 1
  }'
```

### Execute with List Parameter

```bash
curl -X POST "http://localhost:8000/execute/query/3" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "user_ids": [1, 2, 3, 4, 5]
    }
  }'
```

**Expected Result:**
```sql
SELECT * FROM users WHERE id IN (1, 2, 3, 4, 5);
```

## Example 4: LIKE Pattern Search

### Create a Query with LIKE Pattern

```bash
curl -X POST "http://localhost:8000/queries" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Search Users by Name Pattern",
    "description": "Search users by name pattern using sql_like filter",
    "sql": "SELECT * FROM users WHERE name LIKE {{ pattern | sql_like }}",
    "datasource_id": 1
  }'
```

### Execute with Pattern

```bash
curl -X POST "http://localhost:8000/execute/query/4" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "pattern": "John%"
    }
  }'
```

**Expected Result:**
```sql
SELECT * FROM users WHERE name LIKE 'John\%';
```

## Example 5: Complex Business Logic

### Create a Query with Complex Conditions

```bash
curl -X POST "http://localhost:8000/queries" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Advanced Order Search",
    "description": "Search orders with multiple optional filters",
    "sql": "SELECT o.*, c.name as customer_name FROM orders o JOIN customers c ON o.customer_id = c.id WHERE 1=1 {% if customer_id %} AND o.customer_id = {{ customer_id }} {% endif %} {% if order_status %} AND o.status = {{ order_status }} {% endif %} {% if min_amount %} AND o.total_amount >= {{ min_amount }} {% endif %} {% if max_amount %} AND o.total_amount <= {{ max_amount }} {% endif %} {% if order_ids %} AND o.id IN {{ order_ids | sql_in }} {% endif %} {% if start_date %} AND o.created_at >= {{ start_date }} {% endif %} {% if end_date %} AND o.created_at <= {{ end_date }} {% endif %} ORDER BY o.created_at DESC",
    "datasource_id": 1
  }'
```

### Execute with Multiple Filters

```bash
curl -X POST "http://localhost:8000/execute/query/5" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "customer_id": 123,
      "order_status": "completed",
      "min_amount": 100.00,
      "max_amount": 1000.00,
      "start_date": "2024-01-01",
      "end_date": "2024-12-31"
    }
  }'
```

**Expected Result:**
```sql
SELECT o.*, c.name as customer_name FROM orders o JOIN customers c ON o.customer_id = c.id WHERE 1=1 AND o.customer_id = 123 AND o.status = 'completed' AND o.total_amount >= 100.0 AND o.total_amount <= 1000.0 AND o.created_at >= '2024-01-01' AND o.created_at <= '2024-12-31' ORDER BY o.created_at DESC;
```

## Example 6: Dynamic Table Selection

### Create a Query with Dynamic Table

```bash
curl -X POST "http://localhost:8000/queries" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dynamic Table Query",
    "description": "Query different tables dynamically",
    "sql": "SELECT * FROM {{ table_name }} WHERE created_at >= {{ start_date }} {% if end_date %} AND created_at <= {{ end_date }} {% endif %}",
    "datasource_id": 1
  }'
```

### Execute with Table Parameter

```bash
curl -X POST "http://localhost:8000/execute/query/6" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "table_name": "orders",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31"
    }
  }'
```

**Expected Result:**
```sql
SELECT * FROM orders WHERE created_at >= '2024-01-01' AND created_at <= '2024-12-31';
```

## Example 7: Raw Query with Templates

### Execute Raw Query with Template

```bash
curl -X POST "http://localhost:8000/execute/raw" \
  -H "Content-Type: application/json" \
  -d '{
    "datasource_id": 1,
    "sql": "SELECT COUNT(*) as count FROM {{ table_name }} WHERE status = {{ status }} {% if user_id %} AND user_id = {{ user_id }} {% endif %}",
    "parameters": {
      "table_name": "orders",
      "status": "active",
      "user_id": 123
    }
  }'
```

**Expected Result:**
```sql
SELECT COUNT(*) as count FROM orders WHERE status = 'active' AND user_id = 123;
```

## Example 8: Error Handling

### Missing Required Variable

```bash
curl -X POST "http://localhost:8000/execute/query/1" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {}
  }'
```

**Expected Error:**
```json
{
  "detail": "Missing required template variables: user_id"
}
```

### Template Syntax Error

```bash
curl -X POST "http://localhost:8000/execute/raw" \
  -H "Content-Type: application/json" \
  -d '{
    "datasource_id": 1,
    "sql": "SELECT * FROM users WHERE id = {{ user_id }",
    "parameters": {
      "user_id": 123
    }
  }'
```

**Expected Error:**
```json
{
  "detail": "Template compilation error: unexpected '}'"
}
```

## Example 9: Pagination with Templates

### Execute Query with Pagination

```bash
curl -X POST "http://localhost:8000/execute/query/2" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "name": "John"
    },
    "pagination": {
      "page": 1,
      "page_size": 10
    }
  }'
```

**Expected Result:**
```sql
SELECT * FROM users WHERE 1=1 AND name = 'John' LIMIT 10 OFFSET 0;
```

## Example 10: Security Validation

### Attempt to Use Dangerous Construct

```bash
curl -X POST "http://localhost:8000/execute/raw" \
  -H "Content-Type: application/json" \
  -d '{
    "datasource_id": 1,
    "sql": "SELECT * FROM users WHERE id = {{ config.DATABASE_URL }}",
    "parameters": {
      "config": {"DATABASE_URL": "test"}
    }
  }'
```

**Expected Error:**
```json
{
  "detail": "Template processing error: Potentially dangerous template construct detected"
}
```

## Testing All Examples

You can test all these examples by running:

```bash
# Create the queries first
curl -X POST "http://localhost:8000/queries" -H "Content-Type: application/json" -d @sample_requests/create_query_jinja_example1.json
curl -X POST "http://localhost:8000/queries" -H "Content-Type: application/json" -d @sample_requests/create_query_jinja_example2.json
# ... etc

# Then execute them
curl -X POST "http://localhost:8000/execute/query/1" -H "Content-Type: application/json" -d @sample_requests/execute_jinja_example1.json
curl -X POST "http://localhost:8000/execute/query/2" -H "Content-Type: application/json" -d @sample_requests/execute_jinja_example2.json
# ... etc
```

## Notes

1. **Template Detection**: The system automatically detects Jinja syntax and processes templates accordingly
2. **Security**: All templates run in safe mode with security validation
3. **Error Handling**: Missing variables and syntax errors are caught and reported clearly
4. **Performance**: Templates are compiled once and cached for better performance
5. **Compatibility**: Non-template SQL queries continue to work as before 