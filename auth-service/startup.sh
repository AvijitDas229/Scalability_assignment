#!/bin/bash

# Wait for PostgreSQL
./wait-for-it.sh postgres:5432 --timeout=60 --strict -- echo "PostgreSQL is ready"
./wait-for-db.sh postgres 5432 -- python app.py
# Initialize database
python -c "
from app import app, db
with app.app_context():
    db.drop_all()  # Add this line to clear existing schema
    db.create_all()
"

# Start application with Gunicorn
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app