#!/usr/bin/env python3
"""
Simple test script to verify the DBMCP server setup.
"""

import asyncio
import aiosqlite
import os
from app.database import init_db
from app.services.datasource_service import DatasourceService
from app.services.query_service import QueryService
from app.models.schemas import DatasourceCreate, QueryCreate, DatabaseType


async def test_database_setup():
    """Test the database setup and basic operations."""
    print("Testing database setup...")
    
    # Initialize database
    await init_db()
    print("✓ Database initialized successfully")
    
    # Test creating a SQLite datasource
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        # Create a test datasource
        datasource_service = DatasourceService(db)
        test_datasource = DatasourceCreate(
            name="test_sqlite",
            database_type=DatabaseType.SQLITE,
            database="./test.db",
            description="Test SQLite database"
        )
        
        try:
            datasource = await datasource_service.create_datasource(test_datasource)
            print(f"✓ Created datasource: {datasource.name} (ID: {datasource.id})")
        except ValueError as e:
            if "already exists" in str(e):
                # Get existing datasource
                datasources = await datasource_service.list_datasources()
                datasource = next((ds for ds in datasources if ds.name == "test_sqlite"), None)
                print(f"✓ Using existing datasource: {datasource.name} (ID: {datasource.id})")
            else:
                raise
        
        # Create a test query
        query_service = QueryService(db)
        test_query = QueryCreate(
            name="test_query",
            description="Test query to create a simple table",
            sql="CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT, value REAL)",
            datasource_id=datasource.id
        )
        
        try:
            query = await query_service.create_query(test_query)
            print(f"✓ Created query: {query.name} (ID: {query.id})")
        except ValueError as e:
            if "already exists" in str(e):
                # Get existing query
                queries = await query_service.list_queries()
                query = next((q for q in queries if q.name == "test_query"), None)
                print(f"✓ Using existing query: {query.name} (ID: {query.id})")
            else:
                raise
        
        # List datasources
        datasources = await datasource_service.list_datasources()
        print(f"✓ Found {len(datasources)} datasources")
        
        # List queries
        queries = await query_service.list_queries()
        print(f"✓ Found {len(queries)} queries")


async def test_sqlite_connection():
    """Test SQLite connection directly."""
    print("\nTesting SQLite connection...")
    
    # Create a test SQLite database
    async with aiosqlite.connect("./test.db") as db:
        # Create a test table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert some test data
        await db.execute("""
            INSERT OR REPLACE INTO users (id, name, email) VALUES 
            (1, 'John Doe', 'john@example.com'),
            (2, 'Jane Smith', 'jane@example.com'),
            (3, 'Bob Johnson', 'bob@example.com')
        """)
        
        await db.commit()
        print("✓ Created test table and inserted data")
        
        # Query the data
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            print(f"✓ Retrieved {len(rows)} users from database")


async def main():
    """Main test function."""
    print("Starting DBMCP server tests...\n")
    
    try:
        await test_database_setup()
        await test_sqlite_connection()
        
        print("\n🎉 All tests passed! The DBMCP server is ready to use.")
        print("\nTo start the server, run:")
        print("  uv run uvicorn app.main:app --reload")
        print("\nThen visit http://localhost:8000/docs for the API documentation.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 