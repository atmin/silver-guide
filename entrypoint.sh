#!/bin/sh
echo "waiting for db..."
until python -c "import socket; socket.create_connection(('${DB_HOST}', ${DB_PORT:-3306}), timeout=2)" 2>/dev/null; do
  sleep 2
done
echo "db is up"
exec "$@"
