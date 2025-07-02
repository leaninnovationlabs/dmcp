# Jinja Templates in SQL Queries

This document explains how to use Jinja templates in your SQL queries for dynamic query generation.

## Overview

The query execution service now supports Jinja templates, allowing you to create dynamic SQL queries with:
- Variable substitution
- Conditional logic
- Loops and iterations
- Custom SQL filters
- Security validation

## Basic Usage

### Simple Variable Substitution

```sql
SELECT * FROM users WHERE id = {{ user_id }}
```

Parameters:
```json
{
  "user_id": 123
}
```

Result:
```sql
SELECT * FROM users WHERE id = 123;
```

### String Variables

String variables are automatically quoted:

```sql
SELECT * FROM users WHERE name = {{ name }}
```

Parameters:
```json
{
  "name": "John Doe"
}
```

Result:
```sql
SELECT * FROM users WHERE name = 'John Doe';
```

## Conditional Logic

### Basic Conditionals

```sql
SELECT * FROM users 
WHERE 1=1
{% if user_id %}
AND id = {{ user_id }}
{% endif %}
{% if name %}
AND name = {{ name }}
{% endif %}
```

Parameters:
```json
{
  "user_id": 123,
  "name": "John"
}
```

Result:
```sql
SELECT * FROM users WHERE 1=1 AND id = 123 AND name = 'John';
```

### Complex Conditionals

```sql
SELECT * FROM users 
WHERE 1=1
{% if user_id %}
AND id = {{ user_id }}
{% endif %}
{% if name %}
AND name = {{ name }}
{% endif %}
{% if email %}
AND email = {{ email }}
{% endif %}
{% if status %}
AND status = {{ status }}
{% endif %}
```

## Custom SQL Filters

### IN Clause Filter

Use the `sql_in` filter to safely handle IN clauses with lists:

```sql
SELECT * FROM users WHERE id IN {{ user_ids | sql_in }}
```

Parameters:
```json
{
  "user_ids": [1, 2, 3, 4, 5]
}
```

Result:
```sql
SELECT * FROM users WHERE id IN (1, 2, 3, 4, 5);
```

### LIKE Pattern Filter

Use the `sql_like` filter to safely escape LIKE patterns:

```sql
SELECT * FROM users WHERE name LIKE {{ pattern | sql_like }}
```

Parameters:
```json
{
  "pattern": "John%"
}
```

Result:
```sql
SELECT * FROM users WHERE name LIKE 'John\%';
```

### SQL Quote Filter

Use the `sql_quote` filter for manual quoting:

```sql
SELECT * FROM users WHERE name = {{ name | sql_quote }}
```

## Advanced Examples

### Dynamic Table Selection

```sql
SELECT * FROM {{ table_name }} 
WHERE created_at >= {{ start_date }}
{% if end_date %}
AND created_at <= {{ end_date }}
{% endif %}
```

### Dynamic Column Selection

```sql
SELECT 
{% for column in columns %}
{{ column }}{% if not loop.last %},{% endif %}
{% endfor %}
FROM {{ table_name }}
WHERE id = {{ record_id }}
```

### Complex WHERE Clauses

```sql
SELECT * FROM orders 
WHERE 1=1
{% if customer_id %}
AND customer_id = {{ customer_id }}
{% endif %}
{% if order_status %}
AND status = {{ order_status }}
{% endif %}
{% if min_amount %}
AND total_amount >= {{ min_amount }}
{% endif %}
{% if max_amount %}
AND total_amount <= {{ max_amount }}
{% endif %}
{% if order_ids %}
AND id IN {{ order_ids | sql_in }}
{% endif %}
ORDER BY created_at DESC
```

## Security Features

### Automatic Security Validation

The template engine includes security measures:

1. **Dangerous Construct Detection**: Blocks access to Flask/application context variables
2. **File System Access Prevention**: Blocks file system access attempts
3. **Code Execution Prevention**: Blocks eval/exec calls
4. **Strict Undefined Variables**: Requires all variables to be explicitly provided

### Safe Mode

Templates run in safe mode by default, which:
- Validates against dangerous patterns
- Requires all variables to be provided
- Escapes special characters appropriately

## Error Handling

### Missing Variables

If required variables are missing:

```sql
SELECT * FROM users WHERE id = {{ user_id }}
```

Parameters: `{}`

Error:
```
Missing required template variables: user_id
```

### Template Syntax Errors

Invalid Jinja syntax will result in compilation errors:

```sql
SELECT * FROM users WHERE id = {{ user_id }  -- Missing closing brace
```

Error:
```
Template compilation error: unexpected '}'
```

## API Usage

### Execute Named Query with Templates

```python
# Query stored in database with template
sql = "SELECT * FROM users WHERE id = {{ user_id }} AND status = {{ status }}"

# Execute with parameters
result = await query_service.execute_named_query(
    query_id=1,
    parameters={
        "user_id": 123,
        "status": "active"
    }
)
```

### Execute Raw Query with Templates

```python
# Raw SQL with template
sql = """
SELECT * FROM orders 
WHERE customer_id = {{ customer_id }}
{% if order_date %}
AND order_date = {{ order_date }}
{% endif %}
"""

# Execute with parameters
result = await query_service.execute_raw_query(
    datasource_id=1,
    sql=sql,
    parameters={
        "customer_id": 456,
        "order_date": "2024-01-15"
    }
)
```

## Best Practices

### 1. Always Use Parameters

Instead of string concatenation, use template variables:

```sql
-- Good
SELECT * FROM users WHERE id = {{ user_id }}

-- Bad (SQL injection risk)
SELECT * FROM users WHERE id = {{ "user_id" }}
```

### 2. Use Conditional Logic for Optional Filters

```sql
SELECT * FROM users 
WHERE 1=1
{% if user_id %}
AND id = {{ user_id }}
{% endif %}
{% if name %}
AND name = {{ name }}
{% endif %}
```

### 3. Use Custom Filters for Complex Operations

```sql
-- Use sql_in for lists
WHERE id IN {{ user_ids | sql_in }}

-- Use sql_like for patterns
WHERE name LIKE {{ pattern | sql_like }}
```

### 4. Validate Template Variables

Always provide all required variables:

```python
# Check what variables are needed
variables = template_service.get_template_variables(sql)
print(f"Required variables: {variables}")

# Validate before execution
missing = template_service.validate_template_variables(sql, parameters)
if missing:
    print(f"Missing variables: {missing}")
```

### 5. Use Comments for Documentation

```sql
{# Get users with optional filters #}
SELECT * FROM users 
WHERE 1=1
{% if user_id %}
{# Filter by specific user ID #}
AND id = {{ user_id }}
{% endif %}
```

## Limitations

1. **No File System Access**: Templates cannot access files or external resources
2. **No Application Context**: Templates cannot access Flask/application context
3. **No Code Execution**: Templates cannot execute arbitrary Python code
4. **Variable Validation**: All variables must be explicitly provided

## Testing

Run the test suite to verify template functionality:

```bash
pytest tests/test_jinja_templates.py -v
```

Or run the example usage:

```bash
python tests/test_jinja_templates.py
``` 