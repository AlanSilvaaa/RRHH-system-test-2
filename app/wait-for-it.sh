#!/bin/sh

# wait-for-it.sh
# Usage: ./wait-for-it.sh host port [-t timeout] [-- command args]
# Example: ./wait-for-it.sh mysql 3306 -- echo "MySQL is up"

HOST=$1
PORT=$2
shift 2
TIMEOUT=30

while ! nc -z $HOST $PORT; do
  echo "Waiting for $HOST:$PORT..."
  sleep 1
  TIMEOUT=$((TIMEOUT-1))
  if [ $TIMEOUT -eq 0 ]; then
    echo "Timeout waiting for $HOST:$PORT"
    exit 1
  fi
done

echo "$HOST:$PORT is up"

# Skip the `--` if it exists
if [ "$1" = "--" ]; then
  shift
fi

exec "$@"