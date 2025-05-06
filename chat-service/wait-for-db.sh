#!/bin/sh
# Wait for both PostgreSQL AND dependent services
./wait-for-it.sh postgres:5432 --timeout=60 --strict -- \
  ./wait-for-it.sh auth-service:5000 --timeout=30 --strict -- \
  python app.py