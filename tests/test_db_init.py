#!/usr/bin/env python3
"""
Test database initialization script.
Performs the following steps:
1. Create the db and tables if not present
2. If present drop the db
3. Create the tables
4. Load the data
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_db_manager import TestDatabaseManager


def init_test_database(db_name: str = None) -> TestDatabaseManager:
    """
    Initialize a test database with the following steps:
    1. Create the db and tables if not present
    2. If present drop the db
    3. Create the tables
    4. Load the data
    
    Args:
        db_name: Optional name for the test database
        
    Returns:
        TestDatabaseManager instance with initialized database
    """
    print("🧪 Initializing test database...")
    
    # Create database manager
    db_manager = TestDatabaseManager(db_name)
    
    try:
        # Step 1: Create database if not present
        print("1. Creating database if not present...")
        db_manager.create_db()
        
        # Step 2: Drop database if present (to ensure clean state)
        print("2. Dropping database to ensure clean state...")
        db_manager.drop_db()
        
        # Step 3: Create database again and initialize tables
        print("3. Creating database and tables...")
        db_manager.create_db()
        db_manager.init_db()
        
        # Step 4: Load the data
        print("4. Loading test data...")
        db_manager.populate_dummy_data()
        
        print("✅ Test database initialized successfully!")
        print(f"   - Database name: {db_manager.get_db_name()}")
        print(f"   - Connection string: {db_manager.get_connection_string()}")
        
        return db_manager
        
    except Exception as e:
        print(f"❌ Error initializing test database: {e}")
        raise


def verify_database_state(db_manager: TestDatabaseManager) -> bool:
    """
    Verify that the database was initialized correctly.
    
    Args:
        db_manager: The TestDatabaseManager instance
        
    Returns:
        True if verification passes, False otherwise
    """
    print("\n🔍 Verifying database state...")
    
    try:
        # Check if tables exist and have data
        tables_to_check = ['users', 'products', 'orders', 'order_items', 'categories']
        
        for table in tables_to_check:
            count = db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}")
            print(f"   - {table}: {count[0]['count']} records")
        
        # Verify some sample data
        users = db_manager.execute_query("SELECT username, email FROM users LIMIT 3")
        print(f"   - Sample users: {[user['username'] for user in users]}")
        
        products = db_manager.execute_query("SELECT name, price FROM products LIMIT 3")
        product_names = [f"{p['name']} (${p['price']})" for p in products]
        print(f"   - Sample products: {product_names}")
        
        print("✅ Database verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False




def main():
    """Main function to run the database initialization."""
    print("Test Database Initialization")
    print("=" * 40)
    
    try:
        # Initialize the test database
        db_manager = init_test_database()
        
        # Verify the database state
        if verify_database_state(db_manager):
            print("\n🎉 Test database initialization completed successfully!")
            print("📖 The database is ready for testing.")
            
            # Show usage example
            
            return 0
        else:
            print("\n❌ Test database verification failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test database initialization failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 