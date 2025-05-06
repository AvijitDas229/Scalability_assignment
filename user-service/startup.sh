#!/bin/bash

# Wait for PostgreSQL
./wait-for-it.sh postgres:5432 --timeout=60 --strict -- echo "PostgreSQL is ready"

# Initialize database (with retries)
for i in {1..5}; do
    python init-db.py && break || sleep 15
done

# Start application
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app