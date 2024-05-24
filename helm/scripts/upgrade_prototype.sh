#!/bin/bash
set -ex

namespace=${NAMESPACE:-deployment}

if [[ -z "${IMAGE}" ]]; then
  echo "No image defined. please define a version by setting IMAGE env var"
  exit 1
fi

if [[ -z "${IMAGE_WEB}" ]]; then
  echo "No web image defined. please define a version by setting IMAGE_WEB env var"
  exit 1
fi

image=${IMAGE}
imageWeb=${IMAGE_WEB}

helm upgrade prototype --install --namespace "$namespace" --values ./values/prototype-value.yaml --values ./values/clickhouse-value.yaml --set-json="image.repository=\"${image}\"" ./charts/prototype

helm upgrade notification-celery-worker --install --namespace "$namespace" --values ./values/celery-worker-value.yaml --values ./values/clickhouse-value.yaml --values ./values/notification-celery-worker-value.yaml --set-json="image.repository=\"${image}\"" ./charts/prototype

helm upgrade account-management-celery-worker --install --namespace "$namespace" --values ./values/celery-worker-value.yaml --values ./values/clickhouse-value.yaml --values ./values/account-management-celery-worker-value.yaml --set-json="image.repository=\"${image}\"" ./charts/prototype

helm upgrade celery-worker --install --namespace "$namespace" --values ./values/celery-worker-value.yaml --values ./values/clickhouse-value.yaml --set-json="image.repository=\"${image}\"" ./charts/prototype

helm upgrade celery-beat --install --namespace "$namespace" --values ./values/celery-beat-value.yaml --values ./values/clickhouse-value.yaml --set-json="image.repository=\"${image}\"" ./charts/prototype

helm upgrade --install raw-monitor-transactions-consumer --namespace "$namespace" \
  --values ./values/kafka-consumer-value.yaml \
  --values ./values/raw-monitor-transactions-consumer-value.yaml \
  --values ./values/clickhouse-value.yaml \
  --set-json="image.repository=\"${image}\"" ./charts/ingest

helm upgrade --install processed-monitor-transactions-clickhouse-consumer --namespace "$namespace" \
  --values ./values/kafka-consumer-value.yaml \
  --values ./values/processed-monitor-transactions-clickhouse-consumer-value.yaml \
  --values ./values/clickhouse-value.yaml \
  --set-json="image.repository=\"${image}\"" ./charts/ingest

helm upgrade raw-events-consumer --install --namespace "$namespace" \
  --values ./values/kafka-consumer-value.yaml \
  --values ./values/raw-events-consumer-value.yaml \
  --values ./values/clickhouse-value.yaml \
  --set-json="image.repository=\"${image}\"" ./charts/ingest

helm upgrade --install processed-events-clickhouse-consumer --namespace "$namespace" \
  --values ./values/kafka-consumer-value.yaml \
  --values ./values/processed-events-clickhouse-consumer-value.yaml \
  --values ./values/clickhouse-value.yaml \
  --set-json="image.repository=\"${image}\"" ./charts/ingest

helm upgrade ingest --install --namespace "$namespace" \
  --values ./values/ingest-value.yaml \
  --values ./values/clickhouse-value.yaml \
  --set-json="image.repository=\"${image}\"" ./charts/ingest

helm upgrade webvault --install --namespace "$namespace" --values ./values/webvault-value.yaml --set-json="image.repository=\"${imageWeb}\"" ./charts/webvault