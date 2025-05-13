#!/bin/bash
set -e

# Use localhost for self, or override with ENV
PGHOST="${POSTGRES_HOST:-localhost}"
PGPORT="${POSTGRES_PORT:-5432}"
PGUSER="${POSTGRES_USER:-postgres}"
PGPASSWORD="${POSTGRES_PASSWORD:-postgres}"

echo "Waiting for Postgres to be ready on $PGHOST:$PGPORT..."

export PGPASSWORD=$PGPASSWORD

# Wait until Postgres is ready
until pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" > /dev/null 2>&1; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - creating user and databases..."

# Connect to Postgres and configure
psql -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" <<-EOSQL
  ALTER USER postgres WITH PASSWORD 'postgres';

  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'chatuser') THEN
      CREATE ROLE chatuser WITH LOGIN PASSWORD 'avijit123';
    END IF;
  END
  \$\$;

  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'chat_service_db') THEN
      CREATE DATABASE chat_service_db;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'user_service_db') THEN
      CREATE DATABASE user_service_db;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'auth_service_db') THEN
      CREATE DATABASE auth_service_db;
    END IF;
  END
  \$\$;
EOSQL

# Grant chatuser access
for db in chat_service_db user_service_db auth_service_db; do
  psql -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$db" <<-EOSQL
    GRANT ALL PRIVILEGES ON DATABASE "$db" TO chatuser;
  EOSQL
done

echo "Setup complete."
