#!/bin/bash
# Wait for all dependencies
./wait-for-it.sh postgres:5432 -t 60
./wait-for-it.sh auth-service:5000 -t 30
./wait-for-it.sh user-service:5000 -t 30
exec python app.py