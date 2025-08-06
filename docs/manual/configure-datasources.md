---
outline: deep
---

# Configure DataSources

DataSources are the foundation of DBMCP - they define the connections to your databases. This guide will walk you through configuring various types of database connections.

## Overview

A DataSource in DBMCP contains:
- **Connection Information**: Host, port, database name, credentials
- **Database Type**: PostgreSQL, MySQL, SQLite, or Databricks
- **Security Settings**: SSL configuration, connection pooling
- **Additional Parameters**: Custom connection options

## Supported Database Types

### 1. PostgreSQL
- **Driver**: `postgresql`
- **Port**: 5432 (default)
- **Features**: Full async support, SSL, connection pooling

### 2. MySQL/MariaDB
- **Driver**: `mysql`
- **Port**: 3306 (default)
- **Features**: Full async support, SSL, connection pooling

### 3. SQLite
- **Driver**: `sqlite`
- **Features**: File-based, no network configuration needed

### 4. Databricks
- **Driver**: `databricks`
- **Features**: Cloud data warehouse, OAuth authentication

## Creating DataSources

### Via Web UI

1. Navigate to http://localhost:8000/dbmcp/ui
2. Click on "DataSources" in the sidebar
3. Click "Add New DataSource"
4. Fill in the connection details
5. Click "Test Connection" to verify
6. Click "Save" to create the datasource

### Via API

#### PostgreSQL Example

```bash
curl -X POST http://localhost:8000/dbmcp/datasources \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production_postgres",
    "database_type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "myapp",
    "username": "postgres",
    "password": "your_password",
    "ssl_mode": "prefer",
    "additional_params": {
      "pool_size": 10,
      "max_overflow": 20
    }
  }'
```

#### MySQL Example

```bash
curl -X POST http://localhost:8000/dbmcp/datasources \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "analytics_mysql",
    "database_type": "mysql",
    "host": "analytics.example.com",
    "port": 3306,
    "database": "analytics",
    "username": "analytics_user",
    "password": "your_password",
    "ssl_mode": "required",
    "additional_params": {
      "charset": "utf8mb4",
      "autocommit": true
    }
  }'
```

#### SQLite Example

```bash
curl -X POST http://localhost:8000/dbmcp/datasources \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "local_sqlite",
    "database_type": "sqlite",
    "database": "/path/to/your/database.db",
    "additional_params": {
      "timeout": 30,
      "check_same_thread": false
    }
  }'
```

#### Databricks Example

```bash
curl -X POST http://localhost:8000/dbmcp/datasources \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "databricks_warehouse",
    "database_type": "databricks",
    "host": "your-workspace.cloud.databricks.com",
    "port": 443,
    "database": "default",
    "username": "token",
    "password": "your_databricks_token",
    "additional_params": {
      "http_path": "/sql/1.0/warehouses/your-warehouse-id",
      "catalog": "hive_metastore",
      "schema": "default"
    }
  }'
```

## Connection Parameters

### Common Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Unique name for the datasource |
| `database_type` | string | Yes | One of: `postgresql`, `mysql`, `sqlite`, `databricks` |
| `host` | string | Yes* | Database host (not required for SQLite) |
| `port` | integer | Yes* | Database port (not required for SQLite) |
| `database` | string | Yes | Database name or file path |
| `username` | string | Yes* | Database username (not required for SQLite) |
| `password` | string | Yes* | Database password (not required for SQLite) |
| `ssl_mode` | string | No | SSL mode for secure connections |
| `additional_params` | object | No | Additional connection parameters |

### SSL Modes

For PostgreSQL and MySQL, you can specify SSL modes:

- `disable` - No SSL
- `allow` - Try SSL, fallback to non-SSL
- `prefer` - Try SSL, fallback to non-SSL (default)
- `require` - Require SSL
- `verify-ca` - Require SSL and verify CA
- `verify-full` - Require SSL and verify CA + hostname

### Additional Parameters

#### PostgreSQL
```json
{
  "pool_size": 10,
  "max_overflow": 20,
  "pool_timeout": 30,
  "pool_recycle": 3600
}
```

#### MySQL
```json
{
  "charset": "utf8mb4",
  "autocommit": true,
  "pool_size": 10,
  "max_overflow": 20
}
```

#### SQLite
```json
{
  "timeout": 30,
  "check_same_thread": false,
  "isolation_level": "READ_COMMITTED"
}
```

#### Databricks
```json
{
  "http_path": "/sql/1.0/warehouses/your-warehouse-id",
  "catalog": "hive_metastore",
  "schema": "default",
  "session_configuration": {
    "ansi_mode": true
  }
}
```

## Testing Connections

### Via Web UI
1. In the DataSource creation/edit form
2. Click "Test Connection" button
3. Check the result message

### Via API

```bash
curl -X POST http://localhost:8000/dbmcp/datasources/test \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "database_type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "testdb",
    "username": "testuser",
    "password": "testpass"
  }'
```

## Managing DataSources

### List All DataSources

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/dbmcp/datasources
```

### Get Specific DataSource

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/dbmcp/datasources/{id}
```

### Update DataSource

```bash
curl -X PUT http://localhost:8000/dbmcp/datasources/{id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "updated_name",
    "host": "new_host",
    "port": 5432,
    "database": "new_database",
    "username": "new_user",
    "password": "new_password"
  }'
```

### Delete DataSource

```bash
curl -X DELETE http://localhost:8000/dbmcp/datasources/{id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Security Best Practices

### 1. Credential Management
- Use environment variables for sensitive data
- Rotate passwords regularly
- Use service accounts with minimal privileges

### 2. Network Security
- Use SSL/TLS for all connections
- Restrict database access to specific IPs
- Use VPN or private networks when possible

### 3. Connection Security
- Enable SSL for all production connections
- Use connection pooling to manage resources
- Set appropriate timeouts

### 4. Databricks Specific
- Use personal access tokens instead of passwords
- Configure workspace access properly
- Use appropriate warehouse sizes

## Troubleshooting

### Common Connection Issues

#### 1. Connection Refused
- Check if database server is running
- Verify host and port are correct
- Check firewall settings

#### 2. Authentication Failed
- Verify username and password
- Check if user has proper permissions
- Ensure database exists

#### 3. SSL Issues
- Check SSL certificate validity
- Verify SSL mode configuration
- Ensure client certificates are properly configured

#### 4. Databricks Specific
- Verify workspace URL is correct
- Check if token has proper permissions
- Ensure warehouse is running

### Debugging Tips

1. **Enable Debug Logging**
   ```env
   LOG_LEVEL=DEBUG
   ```

2. **Test with Simple Tools**
   - Create a simple "SELECT 1" tool
   - Test basic connectivity

3. **Check Network Connectivity**
   ```bash
   telnet your_host your_port
   ```

4. **Verify Database Permissions**
   ```sql
   -- PostgreSQL
   GRANT CONNECT ON DATABASE your_db TO your_user;
   GRANT USAGE ON SCHEMA public TO your_user;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO your_user;
   ```

## Next Steps

Now that you have configured your DataSources, you can:

1. **[Create Tools](./create-tools.md)** - Build MCP tools from your database queries
2. **[Connect MCP Clients](./connect-mcp-clients.md)** - Integrate with AI assistants

Ready to create your first tool? Let's move on to the [Tool Creation Guide](./create-tools.md)! 