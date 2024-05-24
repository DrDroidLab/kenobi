#!/usr/bin/env bash

set -o errexit
set -o nounset

sleep 10

WORKER_COUNT="${GUNICORN_WORKER_COUNT:-5}"
WORKER_MAX_REQUEST="${GUNICORN_WORKER_MAX_REQUEST:-100000}"
WORKER_MAX_REQUEST_JITTER="${GUNICORN_WORKER_MAX_REQUEST_JITTER:-10000}"
WORKER_TIMEOUT="${GUNICORN_WORKER_TIMEOUT:-120}"

echo "Setting up DB..."
sh setup_db.sh

echo "Setting up Clickhouse DB..."
python setup_clickhouse.py

echo "Starting Server..."

python manage.py collectstatic --noinput
gunicorn prototype.wsgi --bind 0.0.0.0:8000 --workers $WORKER_COUNT --timeout $WORKER_TIMEOUT --max-requests $WORKER_MAX_REQUEST --max-requests-jitter $WORKER_MAX_REQUEST_JITTER &
nginx -g "daemon off;"

echo "Started Server..."
