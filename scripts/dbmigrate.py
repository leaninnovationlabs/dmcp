#!/usr/bin/env python3
"""
Database management script for DBMCP.

This script provides convenient commands for managing the database schema
using Alembic migrations.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main function to handle database management commands."""
    if len(sys.argv) < 2:
        print("""
Database Management Script for DBMCP

Usage: python manage_db.py <command>

Commands:
    init        - Initialize the database (create tables)
    upgrade     - Apply all pending migrations
    downgrade   - Downgrade to previous migration
    revision    - Create a new migration
    status      - Show current migration status
    history     - Show migration history
    reset       - Reset database (drop all tables and recreate)
    help        - Show this help message

Examples:
    python manage_db.py init
    python manage_db.py upgrade
    python manage_db.py revision -m "Add new table"
    python manage_db.py status
""")
        return

    command = sys.argv[1].lower()
    
    if command == "help":
        print("""
Database Management Script for DBMCP

Usage: python manage_db.py <command>

Commands:
    init        - Initialize the database (create tables)
    upgrade     - Apply all pending migrations
    downgrade   - Downgrade to previous migration
    revision    - Create a new migration
    status      - Show current migration status
    history     - Show migration history
    reset       - Reset database (drop all tables and recreate)
    help        - Show this help message

Examples:
    python manage_db.py init
    python manage_db.py upgrade
    python manage_db.py revision -m "Add new table"
    python manage_db.py status
""")
        return
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    if command == "init":
        print("🚀 Initializing database...")
        if run_command("alembic upgrade head", "Applying initial migration"):
            print("✅ Database initialized successfully!")
            print("📊 Tables created: datasources, queries")
        else:
            print("❌ Database initialization failed")
            sys.exit(1)
    
    elif command == "upgrade":
        if run_command("alembic upgrade head", "Applying migrations"):
            print("✅ Database upgraded successfully!")
        else:
            print("❌ Database upgrade failed")
            sys.exit(1)
    
    elif command == "downgrade":
        if len(sys.argv) < 3:
            print("❌ Please specify a revision to downgrade to")
            print("Example: python manage_db.py downgrade -1")
            sys.exit(1)
        revision = sys.argv[2]
        if run_command(f"alembic downgrade {revision}", f"Downgrading to revision {revision}"):
            print("✅ Database downgraded successfully!")
        else:
            print("❌ Database downgrade failed")
            sys.exit(1)
    
    elif command == "revision":
        if len(sys.argv) < 3:
            print("❌ Please provide a message for the migration")
            print("Example: python manage_db.py revision -m 'Add new column'")
            sys.exit(1)
        message = " ".join(sys.argv[2:])
        if run_command(f'alembic revision --autogenerate -m "{message}"', "Creating new migration"):
            print("✅ Migration created successfully!")
            print("💡 Review the generated migration file before applying")
        else:
            print("❌ Migration creation failed")
            sys.exit(1)
    
    elif command == "status":
        if run_command("alembic current", "Checking migration status"):
            print("📋 Current migration status:")
            subprocess.run("alembic history --verbose", shell=True)
        else:
            print("❌ Failed to get migration status")
            sys.exit(1)
    
    elif command == "history":
        if run_command("alembic history --verbose", "Showing migration history"):
            pass
        else:
            print("❌ Failed to get migration history")
            sys.exit(1)
    
    elif command == "reset":
        print("⚠️  WARNING: This will delete all data and recreate the database!")
        response = input("Are you sure you want to continue? (y/N): ")
        if response.lower() != 'y':
            print("❌ Reset cancelled")
            return
        
        print("🗑️  Resetting database...")
        # Drop all tables (this is a simple approach for SQLite)
        db_file = Path("dbmcp.db")
        if db_file.exists():
            db_file.unlink()
            print("🗑️  Removed existing database file")
        
        if run_command("alembic upgrade head", "Recreating database schema"):
            print("✅ Database reset successfully!")
        else:
            print("❌ Database reset failed")
            sys.exit(1)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python manage_db.py help' for available commands")
        sys.exit(1)


if __name__ == "__main__":
    main() 