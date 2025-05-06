#!/bin/bash
set -e

# Create additional databases
for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
  psql -U "$POSTGRES_USER" -tc "SELECT 1 FROM pg_database WHERE datname = '$db'" | grep -q 1 || \
    psql -U "$POSTGRES_USER" -c "CREATE DATABASE $db"
done
