#!/bin/sh
# wait-for-db.sh

set -e

host="$1"
shift
port="$1"
shift
cmd="$@"

# First use wait-for-it to check basic port availability
./wait-for-it.sh "$host:$port" --timeout=60 --strict -- \
  sh -c "
    # Now verify PostgreSQL is really ready
    until PGPASSWORD=\$POSTGRES_PASSWORD psql -h '$host' -p '$port' -U 'chatuser' -d 'auth_service_db' -c '\q'; do
      echo >&2 'Postgres is up but not yet accepting connections - sleeping'
      sleep 2
    done
    echo >&2 'PostgreSQL is fully ready - executing command'
    exec $cmd
  "