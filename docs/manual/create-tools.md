---
outline: deep
---

# Create Tools

Tools in DMCP are named queries that can be executed by AI assistants through the MCP protocol. They allow you to expose database operations as simple, reusable functions that AI models can understand and use.

## What are Tools?

A Tool in DMCP consists of:
- **Name**: Human-readable identifier for the tool
- **Description**: Clear explanation of what the tool does
- **SQL Query**: The actual database query to execute
- **Parameters**: Input parameters that can be passed to the query
- **DataSource**: Which database connection to use
- **Tool Type**: The type of operation (query, mutation, etc.)

## Tool Types

### 1. Query Tools
- **Purpose**: Retrieve data from the database
- **Use Case**: Reports, analytics, data exploration
- **Example**: "Get user statistics", "List recent orders"

### 2. Mutation Tools
- **Purpose**: Modify data in the database
- **Use Case**: Data updates, inserts, deletes
- **Example**: "Update user status", "Create new record"

### 3. Utility Tools
- **Purpose**: Database maintenance and utilities
- **Use Case**: Schema exploration, connection testing
- **Example**: "List tables", "Test connection"

## Creating Tools

### Via Web UI

1. Navigate to http://localhost:8000/dmcp/ui (when server is running)
2. Click on "Tools" in the sidebar
3. Click "Add New Tool"
4. Fill in the tool details:
   - **Name**: A descriptive name
   - **Description**: What the tool does
   - **SQL**: Your query with parameters
   - **DataSource**: Select your configured datasource
   - **Parameters**: Define input parameters
5. Click "Test" to verify the tool works
6. Click "Save" to create the tool

### Via API

#### Simple Query Tool

```bash
curl -X POST http://localhost:8000/dmcp/tools \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_user_count",
    "description": "Get the total number of users in the system",
    "sql": "SELECT COUNT(*) as user_count FROM users",
    "datasource_id": 1,
    "parameters": []
  }'
```

#### Parameterized Query Tool

```bash
curl -X POST http://localhost:8000/dmcp/tools \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_users_by_status",
    "description": "Get users filtered by their status",
    "sql": "SELECT id, name, email, status, created_at FROM users WHERE status = {{ status }} ORDER BY created_at DESC",
    "datasource_id": 1,
    "parameters": [
      {
        "name": "status",
        "type": "string",
        "description": "User status to filter by",
        "required": true,
        "default": "active"
      }
    ]
  }'
```

#### Complex Analytics Tool

```bash
curl -X POST http://localhost:8000/dmcp/tools \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "sales_analytics",
    "description": "Get sales analytics for a specific date range",
    "sql": "SELECT 
              DATE(created_at) as sale_date,
              COUNT(*) as total_orders,
              SUM(total_amount) as total_revenue,
              AVG(total_amount) as avg_order_value
            FROM orders 
            WHERE created_at BETWEEN {{ start_date }} AND {{ end_date }}
            GROUP BY DATE(created_at)
            ORDER BY sale_date DESC",
    "datasource_id": 1,
    "parameters": [
      {
        "name": "start_date",
        "type": "string",
        "description": "Start date (YYYY-MM-DD)",
        "required": true
      },
      {
        "name": "end_date",
        "type": "string",
        "description": "End date (YYYY-MM-DD)",
        "required": true
      }
    ]
  }'
```

## Parameter Types

### Supported Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text values | `"active"`, `"john@example.com"` |
| `integer` | Whole numbers | `42`, `1000` |
| `float` | Decimal numbers | `3.14`, `99.99` |
| `boolean` | True/false values | `true`, `false` |
| `date` | Date values | `"2024-01-01"` |
| `datetime` | Date and time | `"2024-01-01T10:30:00"` |

### Parameter Properties

```json
{
  "name": "parameter_name",
  "type": "string",
  "description": "What this parameter does",
  "required": true,
  "default": "default_value",
  "enum": ["option1", "option2", "option3"]
}
```

## Jinja Template Support

DMCP supports Jinja2 templating in your SQL queries, allowing for dynamic query construction.

### Basic Variable Substitution

```sql
SELECT * FROM users WHERE status = {{ status }}
```

### Conditional Logic

```sql
SELECT * FROM users 
WHERE 1=1
{% if status %}
  AND status = {{ status }}
{% endif %}
{% if email %}
  AND email LIKE '%{{ email }}%'
{% endif %}
```

### Loops and Lists

```sql
SELECT * FROM products 
WHERE category IN (
  {% for category in categories %}
    '{{ category }}'{% if not loop.last %},{% endif %}
  {% endfor %}
)
```

### Date Formatting

```sql
SELECT * FROM orders 
WHERE created_at >= '{{ start_date }}' 
  AND created_at <= '{{ end_date }}'
```

## Best Practices

### 1. Naming Conventions

- Use descriptive, action-oriented names
- Follow consistent naming patterns
- Avoid abbreviations unless widely understood

**Good Examples:**
- `get_user_by_id`
- `create_new_order`
- `update_user_status`
- `delete_expired_sessions`

**Bad Examples:**
- `q1`
- `get_data`
- `update`
- `delete`

### 2. Descriptions

Write clear, concise descriptions that explain:
- What the tool does
- What parameters it expects
- What results it returns

**Good Example:**
```
"Retrieves user information by email address. Returns user details including name, email, status, and creation date. Use this tool when you need to look up a specific user."
```

### 3. SQL Best Practices

- Use parameterized queries to prevent SQL injection
- Include appropriate WHERE clauses for performance
- Use meaningful column aliases
- Add LIMIT clauses for large result sets

```sql
-- Good: Parameterized and limited
SELECT id, name, email, status 
FROM users 
WHERE email = {{ email }} 
LIMIT 1

-- Bad: No parameters, no limits
SELECT * FROM users
```

### 4. Parameter Design

- Make parameters required only when necessary
- Provide sensible defaults when possible
- Use enums for constrained values
- Include clear descriptions

```json
{
  "parameters": [
    {
      "name": "status",
      "type": "string",
      "description": "User status to filter by",
      "required": false,
      "default": "active",
      "enum": ["active", "inactive", "suspended"]
    }
  ]
}
```

## Advanced Examples

### 1. Pagination Tool

```sql
SELECT id, name, email, created_at
FROM users
ORDER BY created_at DESC
LIMIT {{ limit }} OFFSET {{ offset }}
```

Parameters:
```json
[
  {
    "name": "limit",
    "type": "integer",
    "description": "Number of records to return",
    "required": false,
    "default": 10
  },
  {
    "name": "offset",
    "type": "integer", 
    "description": "Number of records to skip",
    "required": false,
    "default": 0
  }
]
```

### 2. Search Tool

```sql
SELECT id, name, email, status
FROM users
WHERE 1=1
{% if search_term %}
  AND (name ILIKE '%{{ search_term }}%' OR email ILIKE '%{{ search_term }}%')
{% endif %}
{% if status %}
  AND status = {{ status }}
{% endif %}
ORDER BY name
LIMIT {{ limit }}
```

### 3. Aggregation Tool

```sql
SELECT 
  DATE_TRUNC('{{ time_unit }}', created_at) as time_period,
  COUNT(*) as total_users,
  COUNT(CASE WHEN status = 'active' THEN 1 END) as active_users
FROM users
WHERE created_at >= '{{ start_date }}'
  AND created_at <= '{{ end_date }}'
GROUP BY DATE_TRUNC('{{ time_unit }}', created_at)
ORDER BY time_period
```

Parameters:
```json
[
  {
    "name": "time_unit",
    "type": "string",
    "description": "Time unit for aggregation",
    "required": true,
    "enum": ["day", "week", "month", "quarter", "year"]
  },
  {
    "name": "start_date",
    "type": "date",
    "description": "Start date for analysis",
    "required": true
  },
  {
    "name": "end_date", 
    "type": "date",
    "description": "End date for analysis",
    "required": true
  }
]
```

## Managing Tools

### List All Tools

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/dmcp/tools
```

### Get Specific Tool

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/dmcp/tools/{id}
```

### Update Tool

```bash
curl -X PUT http://localhost:8000/dmcp/tools/{id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "updated_tool_name",
    "description": "Updated description",
    "sql": "SELECT * FROM users WHERE status = {{ status }}",
    "parameters": [
      {
        "name": "status",
        "type": "string",
        "required": true
      }
    ]
  }'
```

### Delete Tool

```bash
curl -X DELETE http://localhost:8000/dmcp/tools/{id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Tool

```bash
curl -X POST http://localhost:8000/dmcp/tools/{id}/test \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "status": "active",
      "limit": 10
    }
  }'
```

## Testing Tools

### Via Web UI
1. In the tool creation/edit form
2. Click "Test" button
3. Provide test parameters
4. Review the results

### Via API

```bash
curl -X POST http://localhost:8000/dmcp/execute/{tool_id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "status": "active",
      "limit": 5
    }
  }'
```

## Troubleshooting

### Common Issues

#### 1. SQL Syntax Errors
- Check your SQL syntax
- Verify table and column names
- Test queries directly in your database

#### 2. Parameter Issues
- Ensure parameter names match in SQL and parameters array
- Check parameter types and required fields
- Verify default values are correct

#### 3. DataSource Issues
- Confirm the datasource is working
- Check database permissions
- Verify connection parameters

#### 4. Jinja Template Errors
- Check Jinja syntax
- Ensure variables are properly quoted
- Test templates with sample data

### Debugging Tips

1. **Test with Simple Queries First**
   ```sql
   SELECT 1 as test
   ```

2. **Use Parameter Validation**
   - Test with different parameter combinations
   - Verify required vs optional parameters

3. **Check Query Performance**
   - Use EXPLAIN for complex queries
   - Add appropriate indexes
   - Limit result sets

4. **Monitor Tool Usage**
   - Check execution logs
   - Monitor performance metrics
   - Track error rates

## Next Steps

Now that you have created your tools, you can:

1. **[Connect MCP Clients](./connect-mcp-clients.md)** - Integrate with AI assistants
2. **Test your tools** - Use the MCP Inspector to verify functionality
3. **Optimize performance** - Monitor and improve tool efficiency

Ready to connect your tools to AI assistants? Let's move on to the [MCP Client Connection Guide](./connect-mcp-clients.md)! 