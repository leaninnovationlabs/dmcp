#!/usr/bin/env python3
"""
Script to export all data from database tables as INSERT statements.

Usage:
    uv run scripts/export_database.py

The script will:
1. Connect to the database using hardcoded database URL
2. Read all data from all tables
3. Generate a SQL file with INSERT statements
"""

import json
import sys
from datetime import datetime
from typing import Any

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session


def escape_string(value: str) -> str:
    """Escape single quotes in SQL strings."""
    if value is None:
        return "NULL"
    return value.replace("'", "''")


def format_value(value: Any, column_type: str) -> str:
    """Format a value for SQL INSERT statement based on column type."""
    if value is None:
        return "NULL"

    # Handle JSON columns - PostgreSQL returns dict/list for JSON/JSONB
    # Check if column is JSON type or value is dict/list (likely JSON)
    is_json_column = "json" in column_type.lower()
    is_json_value = isinstance(value, (dict, list))
    
    if is_json_column or is_json_value:
        json_str = json.dumps(value, ensure_ascii=False)
        # Use ::jsonb cast for PostgreSQL JSONB columns, otherwise just string
        if is_json_column and "jsonb" in column_type.lower():
            return f"'{escape_string(json_str)}'::jsonb"
        elif is_json_column:
            return f"'{escape_string(json_str)}'::json"
        else:
            # Value is dict/list but column might be text - output as JSON string
            return f"'{escape_string(json_str)}'"

    # Handle datetime
    if isinstance(value, datetime):
        return f"'{value.isoformat()}'"

    # Handle strings
    if isinstance(value, str):
        return f"'{escape_string(value)}'"

    # Handle integers and floats
    if isinstance(value, (int, float)):
        return str(value)

    # Handle booleans
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"

    # Default: convert to string and escape
    return f"'{escape_string(str(value))}'"


def get_table_data(engine: Any, table_name: str) -> list[dict[str, Any]]:
    """Get all data from a table."""
    with Session(engine) as session:
        result = session.execute(text(f"SELECT * FROM {table_name}"))
        columns = result.keys()
        rows = []
        for row in result:
            rows.append(dict(zip(columns, row)))
        return rows


def get_table_columns(engine: Any, table_name: str) -> list[dict[str, Any]]:
    """Get column information for a table."""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return columns


def generate_insert_statements(engine: Any, table_name: str, output_file: Any) -> None:
    """Generate INSERT statements for a table."""
    try:
        # Get column information
        columns_info = get_table_columns(engine, table_name)
        column_names = [col["name"] for col in columns_info]
        column_types = {col["name"]: str(col["type"]) for col in columns_info}

        # Get all data
        rows = get_table_data(engine, table_name)

        if not rows:
            output_file.write(f"-- Table: {table_name} (empty)\n\n")
            return

        output_file.write(f"-- Table: {table_name}\n")
        output_file.write(f"-- {len(rows)} row(s)\n\n")

        # Generate INSERT statements
        for row in rows:
            values = []
            for col_name in column_names:
                value = row.get(col_name)
                col_type = column_types.get(col_name, "")
                formatted_value = format_value(value, col_type)
                values.append(formatted_value)

            columns_str = ", ".join([f'"{col}"' for col in column_names])
            values_str = ", ".join(values)

            output_file.write(f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({values_str});\n')

        output_file.write("\n")
        print(f"✓ Exported {len(rows)} row(s) from table '{table_name}'")

    except Exception as e:
        print(f"✗ Error exporting table '{table_name}': {e}", file=sys.stderr)
        output_file.write(f"-- Error exporting table {table_name}: {e}\n\n")


def main():
    """Main function to export database data."""
    # Hardcoded database URL
    database_url = "postgresql+asyncpg://dmcpuser:12345@localhost:5432/dmcp"

    # Convert async URL to sync URL for SQLAlchemy
    sync_url = database_url.replace("+asyncpg", "").replace("+aiosqlite", "").replace("+aiomysql", "")

    print(f"Connecting to database: {sync_url.split('@')[1] if '@' in sync_url else sync_url}")

    try:
        # Create engine
        engine = create_engine(sync_url, echo=False)

        # Get all table names
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        if not table_names:
            print("No tables found in the database", file=sys.stderr)
            sys.exit(1)

        print(f"Found {len(table_names)} table(s): {', '.join(table_names)}")

        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"database_export_{timestamp}.sql"

        # Generate INSERT statements
        with open(output_filename, "w", encoding="utf-8") as output_file:
            output_file.write(f"-- Database Export\n")
            output_file.write(f"-- Generated: {datetime.now().isoformat()}\n")
            output_file.write(f"-- Source Database: {sync_url.split('@')[1] if '@' in sync_url else sync_url}\n")
            output_file.write(f"-- Tables: {', '.join(table_names)}\n\n")
            output_file.write("-- Note: This file contains INSERT statements for all data.\n")
            output_file.write("-- Make sure to run this on an empty database or handle conflicts appropriately.\n\n")

            # Export each table
            for table_name in sorted(table_names):
                generate_insert_statements(engine, table_name, output_file)

        print(f"\n✓ Export complete! SQL file generated: {output_filename}")
        print(f"  You can now import this file into another database using:")
        print(f"  psql -d target_database -f {output_filename}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

