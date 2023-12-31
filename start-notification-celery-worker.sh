#!/usr/bin/env bash
set -x
set -o errexit
set -o nounset

sleep 10

QUEUE="${CELERY_QUEUE:-notification}"
WORKER_COUNT="${CELERY_WORKER_COUNT:-1}"

WORKER_MAX_TASKS_PER_CHILD="${CELERY_WORKER_MAX_TASKS_PER_CHILD:-10}"
WORKER_PREFETCH_MULTIPLIER="${CELERY_WORKER_PREFETCH_MULTIPLIER:-1}"

celery -A prototype worker --concurrency=$WORKER_COUNT -l INFO -Ofair -Q $QUEUE --max-tasks-per-child=$WORKER_MAX_TASKS_PER_CHILD --prefetch-multiplier=$WORKER_PREFETCH_MULTIPLIER