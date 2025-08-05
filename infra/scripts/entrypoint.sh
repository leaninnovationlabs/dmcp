#!/bin/bash
set -e

# Function to run database migrations
run_migrations() {
    if [ "$SKIP_MIGRATIONS" = "true" ]; then
        echo "Skipping database migrations (SKIP_MIGRATIONS=true)"
        return 0
    fi
    
    echo "Running database migrations..."
    if [ -f "alembic.ini" ]; then
        alembic upgrade head
        echo "Database migrations completed successfully"
    else
        echo "No alembic.ini found, skipping migrations"
    fi
}

# Main execution
echo "Starting DBMCP application..."

# Run migrations
run_migrations

# Start the application
echo "Starting application with command: $@"
exec "$@"
