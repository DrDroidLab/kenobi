#!/usr/bin/env bash

# if any of the commands in your code fails for any reason, the entire script fails
set -o errexit
# fail exit if one of your pipe command fails
set -o pipefail
# exits if any of your variables is not set
set -o nounset

sleep 10

echo "${POSTGRES_HOST} ${POSTGRES_PORT}"

postgres_ready() {
python << END
import sys

import psycopg2

try:
    psycopg2.connect(
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${POSTGRES_HOST}",
        port="${POSTGRES_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
}
until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'

if postgres_ready;
then
  echo "Running migrations for new db"
  python manage.py migrate

  echo "Creating superuser"
  sh scripts/user_creation.sh
else
  echo "DB still not ready"
fi

python setup_clickhouse.py
