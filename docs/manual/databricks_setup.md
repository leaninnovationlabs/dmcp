# Databricks Datasource Configuration

This document explains how to configure and use Databricks as a datasource in DBMCP.

## Overview

Databricks is a cloud-based data engineering platform that provides a unified analytics platform. DBMCP supports connecting to Databricks SQL warehouses using the Databricks SQL Connector.

## Prerequisites

1. A Databricks workspace with SQL warehouse access
2. A Databricks personal access token
3. The `databricks-sql-connector` Python package (already included in dependencies)

## Configuration Parameters

### Required Parameters

- **Host**: Your Databricks workspace URL (e.g., `adb-1234567890123456.7.azuredatabricks.net`)
- **Password**: Your Databricks personal access token (stored as password)
- **Database**: The database/schema name (usually `default`)

### Additional Parameters

The following parameters should be provided in the `additional_params` field:

- **http_path**: The HTTP path to your SQL warehouse (e.g., `/sql/1.0/warehouses/1234567890abcdef`)
- **catalog**: The catalog name (e.g., `hive_metastore`)
- **schema**: The schema name (e.g., `default`)

## Example Configuration

### Via API

```json
{
  "name": "My Databricks Warehouse",
  "database_type": "databricks",
  "host": "adb-1234567890123456.7.azuredatabricks.net",
  "database": "default",
  "password": "dapi1234567890abcdef",
  "additional_params": {
    "http_path": "/sql/1.0/warehouses/1234567890abcdef",
    "catalog": "hive_metastore",
    "schema": "default"
  }
}
```

### Via Frontend

1. Navigate to the Datasources page
2. Click "Add Datasource"
3. Select "Databricks" from the database type dropdown
4. Fill in the required fields:
   - **Name**: A descriptive name for your datasource
   - **Host**: Your Databricks workspace URL
   - **Database**: The database name (usually `default`)
   - **Password**: Your Databricks personal access token
   - **Additional Parameters**: JSON object with `http_path`, `catalog`, and `schema`

## Getting Your Databricks Configuration

### 1. Workspace URL

Your workspace URL can be found in your Databricks workspace:
- Go to your Databricks workspace
- Look at the URL in your browser
- It will be something like: `https://adb-1234567890123456.7.azuredatabricks.net`

### 2. Personal Access Token

1. In your Databricks workspace, click on your user icon in the top right
2. Select "User Settings"
3. Go to the "Access Tokens" tab
4. Click "Generate New Token"
5. Give it a name and set an expiration
6. Copy the token (you won't be able to see it again)

### 3. SQL Warehouse HTTP Path

1. In your Databricks workspace, go to "SQL Warehouses"
2. Select your warehouse
3. Click on the warehouse name to open it
4. In the URL, you'll see the warehouse ID
5. The HTTP path will be: `/sql/1.0/warehouses/{warehouse-id}`

### 4. Catalog and Schema

- **Catalog**: Usually `hive_metastore` for Unity Catalog, or `hive_metastore` for legacy
- **Schema**: The schema name where your tables are located (often `default`)

## Testing the Connection

After creating the datasource, you can test the connection using the "Test Connection" button in the frontend or by making a POST request to `/datasources/{id}/test`.

## Creating Tools for Databricks

Once your Databricks datasource is configured, you can create tools that execute SQL queries against your Databricks warehouse. The SQL syntax follows standard SQL with some Databricks-specific features.

### Example Tool

```json
{
  "name": "get_sales_data",
  "description": "Get sales data from Databricks warehouse",
  "sql": "SELECT * FROM sales WHERE date >= :start_date AND date <= :end_date",
  "datasource_id": 1,
  "parameters": [
    {
      "name": "start_date",
      "type": "date",
      "description": "Start date for sales data",
      "required": true
    },
    {
      "name": "end_date",
      "type": "date",
      "description": "End date for sales data",
      "required": true
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **Connection Timeout**: Check your network connectivity and firewall settings
2. **Authentication Error**: Verify your personal access token is correct and not expired
3. **HTTP Path Error**: Ensure the warehouse ID in the HTTP path is correct
4. **Catalog/Schema Error**: Verify the catalog and schema names exist in your Databricks workspace

### Error Messages

- `Failed to connect to Databricks`: Check your workspace URL and network connectivity
- `Authentication failed`: Verify your personal access token
- `Warehouse not found`: Check the HTTP path and warehouse ID
- `Schema not found`: Verify the catalog and schema names

## Security Considerations

1. **Token Security**: Personal access tokens should be kept secure and rotated regularly
2. **Network Security**: Ensure your network allows connections to Databricks
3. **Data Access**: Configure appropriate permissions in Databricks for your user/token
4. **Encryption**: All connections to Databricks use TLS encryption by default

## Performance Tips

1. **Warehouse Size**: Use appropriately sized SQL warehouses for your workload
2. **Query Optimization**: Write efficient SQL queries to minimize execution time
3. **Connection Pooling**: The connector automatically handles connection pooling
4. **Caching**: Consider using Databricks caching features for frequently accessed data 