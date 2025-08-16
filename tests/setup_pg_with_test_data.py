import subprocess
import time
import os
import psycopg2

def run_command(command, check=True, env=None):
    """
    Runs a shell command and prints the output.
    """
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, check=check, env=env)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

def setup_docker_postgres():
    """
    Creates a docker-compose.yml file and starts the PostgreSQL container.
    """
    print("--- Setting up Docker PostgreSQL ---")
    postgres_dir = "postgres"
    docker_compose_file = os.path.join(postgres_dir, "docker-compose.yml")

    # Create the directory
    run_command(["mkdir", "-p", postgres_dir])

    # Define the docker-compose content
    compose_content = """
services:
  pgdb:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_USER: dbmcptest
      POSTGRES_PASSWORD: dbmcptest
      POSTGRES_DB: dbmcptest
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
"""

    # Write the content to the file
    with open(docker_compose_file, "w") as f:
        f.write(compose_content)
    print(f"Created {docker_compose_file}")

    # Run docker-compose up
    os.chdir(postgres_dir)
    run_command(["docker-compose", "up", "-d"])
    os.chdir("..")

    # Verify the container is running
    print("\n--- Verifying container status ---")
    run_command(["docker", "ps", "--filter", "name=postgres-pgdb-1"])

    print("\n--- Waiting for PostgreSQL to be ready ---")
    time.sleep(15)  # Give the database time to start up

def verify_db_connection():
    """
    Connects to the database and runs a simple query.
    """
    print("\n--- Verifying database connection ---")
    conn = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="dbmcptest",
            user="dbmcptest",
            password="dbmcptest",
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        print("Successfully connected to the database and ran a simple query.")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        exit(1)
    finally:
        if conn:
            conn.close()

def setup_pagila_data():
    """
    Clones the pagila repository and loads the data using local psql.
    """
    print("\n--- Setting up Pagila test data ---")
    pagila_dir = "pagila"
    if not os.path.exists(pagila_dir):
        run_command(["git", "clone", "https://github.com/devrimgunduz/pagila.git"])

    # Load the schema and data
    os.chdir(pagila_dir)
    print("\nLoading pagila-schema.sql and pagila-data.sql...")
    
    # Set environment variables for local psql
    env = os.environ.copy()
    env.update({
        'PGHOST': 'localhost',
        'PGPORT': '5432',
        'PGUSER': 'dbmcptest',
        'PGDATABASE': 'dbmcptest'
    })
    
    # Use local psql commands with environment variables
    # Connect to the default database first to create the pagila database
    run_command(["psql", "-c", "CREATE DATABASE pagila;"], env=env)

    # Update environment to use pagila database
    env['PGDATABASE'] = 'pagila'
    
    # Load the schema
    run_command(["psql", "-f", "pagila-schema.sql"], env=env)
    
    # Load the data
    run_command(["psql", "-f", "pagila-data.sql"], env=env)

    os.chdir("..")

def verify_pagila_data():
    """
    Connects to the pagila database and verifies the film count.
    """
    print("\n--- Verifying pagila data ---")
    conn = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="pagila",
            user="dbmcptest",
            password="dbmcptest",
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM film;")
        count = cursor.fetchone()[0]
        print(f"SELECT count(*) FROM film; returned: {count}")

        if count == 1000:
            print("Success! The film table contains 1000 records.")
        else:
            print(f"Failure. Expected 1000 records, but found {count}.")
            exit(1)
    except Exception as e:
        print(f"Error connecting to pagila database: {e}")
        exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_docker_postgres()
    verify_db_connection()
    setup_pagila_data()
    verify_pagila_data()
    print("\nAll tasks completed successfully!")