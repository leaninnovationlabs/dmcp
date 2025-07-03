# DBMCP API Routes Structure

The API has been organized into separate route modules for better maintainability and organization.

## Route Modules

### 1. Health Routes (`app/routes/health.py`)
- **GET** `/dbmcp/health` - Health check endpoint

### 2. Datasource Routes (`app/routes/datasources.py`)
- **POST** `/dbmcp/datasources/` - Create a new datasource
- **GET** `/dbmcp/datasources/` - List all datasources
- **GET** `/dbmcp/datasources/{datasource_id}` - Get a specific datasource
- **DELETE** `/dbmcp/datasources/{datasource_id}` - Delete a datasource

### 3. Tool Routes (`app/routes/tools.py`)
- **POST** `/dbmcp/tools/` - Create a new named tool
- **GET** `/dbmcp/tools/` - List all tools
- **GET** `/dbmcp/tools/{tool_id}` - Get a specific tool
- **DELETE** `/dbmcp/tools/{tool_id}` - Delete a tool

### 4. Tool Execution Routes (`app/routes/execute.py`)
- **POST** `/dbmcp/execute/{tool_id}` - Execute a named tool with parameters
- **POST** `/dbmcp/execute/raw` - Execute a raw SQL query

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