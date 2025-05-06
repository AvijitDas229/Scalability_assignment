#!/bin/bash
##set -e

# Connect to the default 'postgres' database to create other databases
##psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<-EOSQL
##    CREATE DATABASE auth_service_db;
##    CREATE DATABASE user_service_db;
##    GRANT ALL PRIVILEGES ON DATABASE auth_service_db TO "$POSTGRES_USER";
##    GRANT ALL PRIVILEGES ON DATABASE user_service_db TO "$POSTGRES_USER";
##EOSQL

