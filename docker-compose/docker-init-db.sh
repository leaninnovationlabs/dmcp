#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create dmcpuser if it doesn't exist (for dmcp app)
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'dmcpuser') THEN
            CREATE USER dmcpuser WITH PASSWORD '12345';
        ELSE
            ALTER USER dmcpuser WITH PASSWORD '12345';
        END IF;
    END
    \$\$;
    
    -- Grant privileges to dmcpuser on dmcp database
    GRANT ALL PRIVILEGES ON DATABASE dmcp TO dmcpuser;
    ALTER DATABASE dmcp OWNER TO dmcpuser;
    
    -- Create wurfuser if it doesn't exist (for wurf app)
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'wurfuser') THEN
            CREATE USER wurfuser WITH PASSWORD '12345';
        ELSE
            ALTER USER wurfuser WITH PASSWORD '12345';
        END IF;
    END
    \$\$;
    
    -- Create ragdb database if it doesn't exist (for wurf app, owned by wurfuser)
    SELECT 'CREATE DATABASE ragdb'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ragdb')\gexec
    
    -- Grant privileges on ragdb to wurfuser
    GRANT ALL PRIVILEGES ON DATABASE ragdb TO wurfuser;
    ALTER DATABASE ragdb OWNER TO wurfuser;
EOSQL
