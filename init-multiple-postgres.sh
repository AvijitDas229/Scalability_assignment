#!/bin/bash
set -e

echo "Creating multiple PostgreSQL databases: $POSTGRES_MULTIPLE_DATABASES"

# Loop through the comma-separated DB list and create them
for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
  echo "Creating database: $db"
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE $db;
    GRANT ALL PRIVILEGES ON DATABASE $db TO $POSTGRES_USER;
EOSQL
done
