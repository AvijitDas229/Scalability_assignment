#!/bin/bash
set -e

echo "Waiting for postgres to be ready..."

# Wait for the PostgreSQL server to accept connections
until pg_isready -h localhost -U chatuser -d postgres > /dev/null 2>&1; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - ensuring databases exist"

# Run SQL commands as chatuser on the default postgres database
psql -v ON_ERROR_STOP=1 --username=chatuser --dbname=postgres <<-EOSQL
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

echo "All required databases are ready."
