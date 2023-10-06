#!/usr/bin/env bash

set -o errexit
set -o nounset

sleep 10

worker_ready() {
    celery -A prototype inspect ping
}

until worker_ready; do
  >&2 echo 'Celery workers not available'
  sleep 1
done
>&2 echo 'Celery workers is available'


WORKER_COUNT="${CELERY_WORKER_COUNT:-1}"

celery -A prototype flower --concurrency=$WORKER_COUNT