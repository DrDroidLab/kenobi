#!/usr/bin/env bash
set -x
set -o errexit
set -o nounset

sleep 20

CONSUMER="${KAFKA_CONSUMER:-raw_events}"
CONSUMER_GROUP="${KAFKA_CONSUMER_GROUP:-raw_events_consumer_group}"

python manage.py run_kafka_consumer --group "$CONSUMER_GROUP" --consumer "$CONSUMER"