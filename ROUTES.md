# DBMCP API Routes Structure

The API has been organized into separate route modules for better maintainability and organization.

## Route Modules

### 1. Health Routes (`app/routes/health.py`)
- **GET** `/health` - Health check endpoint

### 2. Datasource Routes (`app/routes/datasources.py`)
- **POST** `/datasources/` - Create a new datasource
- **GET** `/datasources/` - List all datasources
- **GET** `/datasources/{datasource_id}` - Get a specific datasource
- **DELETE** `/datasources/{datasource_id}` - Delete a datasource

### 3. Query Routes (`app/routes/queries.py`)
- **POST** `/queries/` - Create a new named query
- **GET** `/queries/` - List all queries
- **GET** `/queries/{query_id}` - Get a specific query
- **DELETE** `/queries/{query_id}` - Delete a query

### 4. Query Execution Routes (`app/routes/execute.py`)
- **POST** `/execute/{query_id}` - Execute a named query with parameters
- **POST** `/execute/raw` - Execute a raw SQL query

## Benefits of This Structure

1. **Modularity**: Each group of related endpoints is in its own file
2. **Maintainability**: Easier to find and modify specific functionality
3. **Scalability**: Easy to add new route modules as the application grows
4. **Testing**: Each route module can be tested independently
5. **Documentation**: Clear separation of concerns in the API documentation

## Adding New Routes

To add new routes:

1. Create a new file in `app/routes/` (e.g., `app/routes/new_feature.py`)
2. Define your router with appropriate prefix and tags
3. Add your endpoints to the router
4. Import and include the router in `app/main.py`

Example:
```python
# app/routes/new_feature.py
from fastapi import APIRouter

router = APIRouter(prefix="/new-feature", tags=["new feature"])

@router.get("/")
async def get_new_feature():
    return {"message": "New feature endpoint"}

# app/main.py
from .routes import new_feature

app.include_router(new_feature.router)
```

## API Documentation

All routes are automatically documented in the OpenAPI schema and available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json 