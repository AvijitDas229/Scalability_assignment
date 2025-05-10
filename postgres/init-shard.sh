#!/bin/sh
set -e

until psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/init-sharding.sql
echo "Database initialization complete"


# Wait for PostgreSQL to be ready
until psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
# Execute initialization script
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/init-sharding.sql
echo "Database initialization complete"


# Only create the shard database
#psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<-EOSQL
#   CREATE DATABASE $POSTGRES_DB;
#    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO "$POSTGRES_USER";
#EOSQL