#!/usr/bin/env bash

set -o errexit
set -o nounset

sleep 20

rm -f './celerybeat.pid'
celery -A prototype beat -l INFO