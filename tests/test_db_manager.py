import os
from pathlib import Path
from typing import Any, Dict, Optional

import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class TestDatabaseManager:
    """
    Manages a test PostgreSQL database for testing purposes.
    Creates, populates, and drops a test database with dummy data.
    """

    def __init__(self, db_name: Optional[str] = None):
        """
        Initialize the test database manager.

        Args:
            db_name: Optional name for the test database. If None, uses config from .test.env.
        """
        # Load environment variables from .test.env
        env_path = Path(__file__).parent / ".test.env"
        if env_path.exists():
            load_dotenv(env_path)

        # Get database configuration
        self.db_host = os.getenv("TEST_DB_HOST", "localhost")
        self.db_port = int(os.getenv("TEST_DB_PORT", "5432"))
        self.db_user = os.getenv("TEST_DB_USER", "test_user")
        self.db_password = os.getenv("TEST_DB_PASSWORD", "test_password")
        self.db_name = db_name or os.getenv("TEST_DB_NAME", "test_db")
        self.ssl_mode = os.getenv("TEST_DB_SSL_MODE", "disable")

        # Build connection strings
        self.connection_string = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        self.admin_connection_string = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/postgres"

        self.engine = None
        self.SessionLocal = None

    def init_db(self) -> None:
        """Initialize the test database and create tables."""
        # Create PostgreSQL engine
        self.engine = create_engine(
            self.connection_string,
            echo=False,
            pool_pre_ping=True,
            pool_size=int(os.getenv("TEST_DB_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("TEST_DB_MAX_OVERFLOW", "10")),
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # Create tables
        self._create_tables()

    def _create_tables(self) -> None:
        """Create test tables with PostgreSQL schema."""
        with self.engine.connect() as conn:
            # Create users table
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    full_name VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            )

            # Create products table
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    price DECIMAL(10,2) NOT NULL,
                    category VARCHAR(100),
                    stock_quantity INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            )

            # Create orders table
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    order_number VARCHAR(50) UNIQUE NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            )

            # Create order_items table
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price DECIMAL(10,2) NOT NULL,
                    total_price DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """)
            )

            # Create categories table
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS categories (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    parent_id INTEGER,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES categories (id)
                )
            """)
            )

            conn.commit()

    def populate_dummy_data(self) -> None:
        """Populate the database with dummy data."""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized. Call init_db() first.")

        session = self.SessionLocal()

        try:
            # Create dummy users
            users_data = [
                {
                    "username": "john_doe",
                    "email": "john@example.com",
                    "full_name": "John Doe",
                },
                {
                    "username": "jane_smith",
                    "email": "jane@example.com",
                    "full_name": "Jane Smith",
                },
                {
                    "username": "bob_wilson",
                    "email": "bob@example.com",
                    "full_name": "Bob Wilson",
                },
                {
                    "username": "alice_brown",
                    "email": "alice@example.com",
                    "full_name": "Alice Brown",
                },
                {
                    "username": "charlie_davis",
                    "email": "charlie@example.com",
                    "full_name": "Charlie Davis",
                },
            ]

            for user_data in users_data:
                session.execute(
                    text("""
                    INSERT INTO users (username, email, full_name, is_active)
                    VALUES (:username, :email, :full_name, :is_active)
                """),
                    {**user_data, "is_active": True},
                )

            # Create dummy categories
            categories_data = [
                {
                    "name": "Electronics",
                    "description": "Electronic devices and gadgets",
                },
                {"name": "Clothing", "description": "Apparel and accessories"},
                {"name": "Books", "description": "Books and publications"},
                {
                    "name": "Home & Garden",
                    "description": "Home improvement and garden supplies",
                },
                {"name": "Sports", "description": "Sports equipment and accessories"},
            ]

            for cat_data in categories_data:
                session.execute(
                    text("""
                    INSERT INTO categories (name, description, is_active)
                    VALUES (:name, :description, :is_active)
                """),
                    {**cat_data, "is_active": True},
                )

            # Create dummy products
            products_data = [
                {
                    "name": "Laptop",
                    "description": "High-performance laptop",
                    "price": 999.99,
                    "category": "Electronics",
                    "stock_quantity": 50,
                },
                {
                    "name": "Smartphone",
                    "description": "Latest smartphone model",
                    "price": 699.99,
                    "category": "Electronics",
                    "stock_quantity": 100,
                },
                {
                    "name": "T-Shirt",
                    "description": "Cotton t-shirt",
                    "price": 19.99,
                    "category": "Clothing",
                    "stock_quantity": 200,
                },
                {
                    "name": "Jeans",
                    "description": "Comfortable jeans",
                    "price": 49.99,
                    "category": "Clothing",
                    "stock_quantity": 150,
                },
                {
                    "name": "Python Programming Book",
                    "description": "Learn Python programming",
                    "price": 39.99,
                    "category": "Books",
                    "stock_quantity": 75,
                },
                {
                    "name": "Garden Hose",
                    "description": "50ft garden hose",
                    "price": 29.99,
                    "category": "Home & Garden",
                    "stock_quantity": 30,
                },
                {
                    "name": "Basketball",
                    "description": "Official size basketball",
                    "price": 24.99,
                    "category": "Sports",
                    "stock_quantity": 60,
                },
                {
                    "name": "Yoga Mat",
                    "description": "Non-slip yoga mat",
                    "price": 34.99,
                    "category": "Sports",
                    "stock_quantity": 40,
                },
            ]

            for prod_data in products_data:
                session.execute(
                    text("""
                    INSERT INTO products (name, description, price, category, stock_quantity, is_active)
                    VALUES (:name, :description, :price, :category, :stock_quantity, :is_active)
                """),
                    {**prod_data, "is_active": True},
                )

            # Create dummy orders
            orders_data = [
                {
                    "user_id": 1,
                    "order_number": "ORD-001",
                    "total_amount": 1019.98,
                    "status": "completed",
                },
                {
                    "user_id": 2,
                    "order_number": "ORD-002",
                    "total_amount": 69.98,
                    "status": "pending",
                },
                {
                    "user_id": 3,
                    "order_number": "ORD-003",
                    "total_amount": 149.97,
                    "status": "shipped",
                },
                {
                    "user_id": 1,
                    "order_number": "ORD-004",
                    "total_amount": 39.99,
                    "status": "completed",
                },
                {
                    "user_id": 4,
                    "order_number": "ORD-005",
                    "total_amount": 89.98,
                    "status": "pending",
                },
            ]

            for order_data in orders_data:
                session.execute(
                    text("""
                    INSERT INTO orders (user_id, order_number, total_amount, status)
                    VALUES (:user_id, :order_number, :total_amount, :status)
                """),
                    order_data,
                )

            # Create dummy order items
            order_items_data = [
                {
                    "order_id": 1,
                    "product_id": 1,
                    "quantity": 1,
                    "unit_price": 999.99,
                    "total_price": 999.99,
                },
                {
                    "order_id": 1,
                    "product_id": 3,
                    "quantity": 1,
                    "unit_price": 19.99,
                    "total_price": 19.99,
                },
                {
                    "order_id": 2,
                    "product_id": 2,
                    "quantity": 1,
                    "unit_price": 699.99,
                    "total_price": 699.99,
                },
                {
                    "order_id": 3,
                    "product_id": 4,
                    "quantity": 3,
                    "unit_price": 49.99,
                    "total_price": 149.97,
                },
                {
                    "order_id": 4,
                    "product_id": 5,
                    "quantity": 1,
                    "unit_price": 39.99,
                    "total_price": 39.99,
                },
                {
                    "order_id": 5,
                    "product_id": 6,
                    "quantity": 1,
                    "unit_price": 29.99,
                    "total_price": 29.99,
                },
                {
                    "order_id": 5,
                    "product_id": 7,
                    "quantity": 2,
                    "unit_price": 24.99,
                    "total_price": 49.98,
                },
            ]

            for item_data in order_items_data:
                session.execute(
                    text("""
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
                    VALUES (:order_id, :product_id, :quantity, :unit_price, :total_price)
                """),
                    item_data,
                )

            session.commit()

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_session(self):
        """Get a database session."""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.SessionLocal()

    def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> list:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query string
            params: Optional parameters for the query

        Returns:
            List of result rows
        """
        if not self.engine:
            raise RuntimeError("Database not initialized. Call init_db() first.")

        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return [dict(row._mapping) for row in result]

    def get_table_info(self, table_name: str) -> list:
        """
        Get information about a table structure.

        Args:
            table_name: Name of the table

        Returns:
            List of column information
        """
        query = f"""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """
        return self.execute_query(query)

    def get_sample_data(self, table_name: str, limit: int = 5) -> list:
        """
        Get sample data from a table.

        Args:
            table_name: Name of the table
            limit: Number of rows to return

        Returns:
            List of sample rows
        """
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(query)

    def drop_db(self) -> None:
        """Drop the test database and clean up resources."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.SessionLocal = None

        # Drop the database using admin connection
        try:
            # Connect to postgres database to drop our test database
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database="postgres",
            )
            conn.autocommit = True

            with conn.cursor() as cursor:
                # Terminate all connections to the database
                cursor.execute(f"""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = '{self.db_name}' AND pid <> pg_backend_pid()
                """)

                # Drop the database
                cursor.execute(f"DROP DATABASE IF EXISTS {self.db_name}")
                print(f"✅ Dropped database: {self.db_name}")

            conn.close()
        except Exception as e:
            print(f"⚠️  Warning: Could not drop database {self.db_name}: {e}")

    def create_db(self) -> None:
        """Create the test database if it doesn't exist."""
        try:
            # Connect to postgres database (default) to create our test database
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database="postgres",
            )
            conn.autocommit = True

            with conn.cursor() as cursor:
                # Check if database exists
                cursor.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s", (self.db_name,)
                )
                exists = cursor.fetchone()

                if not exists:
                    cursor.execute(f"CREATE DATABASE {self.db_name}")
                    print(f"✅ Created database: {self.db_name}")
                else:
                    print(f"ℹ️  Database {self.db_name} already exists")

            conn.close()
        except Exception as e:
            print(f"❌ Error creating database {self.db_name}: {e}")
            raise

    def get_db_name(self) -> str:
        """Get the name of the test database."""
        return self.db_name

    def get_connection_string(self) -> str:
        """Get the connection string for the test database."""
        return self.connection_string

    def __enter__(self):
        """Context manager entry."""
        # Create database first, then initialize
        self.create_db()
        self.init_db()
        self.populate_dummy_data()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.drop_db()


# Convenience functions for common operations
def create_test_db(db_name: Optional[str] = None) -> TestDatabaseManager:
    """
    Create and initialize a test database.

    Args:
        db_name: Optional name for the test database

    Returns:
        TestDatabaseManager instance
    """
    db_manager = TestDatabaseManager(db_name)
    db_manager.create_db()
    db_manager.init_db()
    return db_manager


def create_test_db_with_data(db_name: Optional[str] = None) -> TestDatabaseManager:
    """
    Create, initialize, and populate a test database with dummy data.

    Args:
        db_name: Optional name for the test database

    Returns:
        TestDatabaseManager instance
    """
    db_manager = TestDatabaseManager(db_name)
    db_manager.create_db()
    db_manager.init_db()
    db_manager.populate_dummy_data()
    return db_manager
