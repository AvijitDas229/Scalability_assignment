#!/bin/bash

# Wait for PostgreSQL and auth-service
./wait-for-it.sh postgres:5432 --timeout=60 --strict -- echo "PostgreSQL is ready"
./wait-for-it.sh auth-service:5000 --timeout=30 --strict -- echo "Auth service is ready"
./wait-for-it.sh postgres-shard0:5432 --timeout=60
./wait-for-it.sh postgres-shard1:5432 --timeout=60

# Initialize database
python -c "from app import app, db; with app.app_context(): db.create_all()"

# Start application with Gunicorn
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app