#!/usr/bin/env bash

set -o errexit
set -o nounset

rm -f './celerybeat.pid'
celery -A prototype beat -l INFO