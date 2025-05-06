#!/bin/bash
set -e

# Only create the shard database if it doesn't already exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<-EOSQL
    DO
    \$\$
    BEGIN
        IF NOT EXISTS (
            SELECT FROM pg_database WHERE datname = '$POSTGRES_DB'
        ) THEN
            CREATE DATABASE $POSTGRES_DB;
        END IF;
    END
    \$\$;
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO "$POSTGRES_USER";
EOSQL

