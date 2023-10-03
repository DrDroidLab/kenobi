from datetime import datetime
import json
from datetime import timezone
from typing import List

from event.models import is_filterable_key_type
from event.clickhouse.models import Events, MonitorTransactions
from event.processors.utils import infer_key_type
from protos.event.schema_pb2 import KeyValue, IngestionEvent
from protos.kafka.base_pb2 import ProcessedIngestionEvent, ProcessedMonitorTransaction
from utils.proto_utils import get_value, proto_to_dict


def processed_kvs_to_kvs(processed_kvs: List[ProcessedIngestionEvent.ProcessedKeyValue]):
    return [KeyValue(key=kv.key.value, value=kv.value) for kv in processed_kvs]


def transform_pkvs(pkvs: List[ProcessedIngestionEvent.ProcessedKeyValue]):
    processed_kvs = {}
    kvs = []
    for pkv in pkvs:
        k = pkv.key.value
        k_type = infer_key_type(pkv.value)

        value = get_value(pkv.value)
        if is_filterable_key_type(k_type):
            processed_kvs[k] = value
        kvs.append(KeyValue(key=k, value=pkv.value))
    return processed_kvs, kvs


def ingest_processed_events(processed_events: List[ProcessedIngestionEvent]):
    events = []
    for processed_event in processed_events:
        event_name = processed_event.event_type.name
        event_timestamp = processed_event.timestamp

        processed_kvs, kvs = transform_pkvs(processed_event.kvs)
        ingested_event = IngestionEvent(
            name=event_name,
            timestamp=event_timestamp,
            kvs=kvs
        )
        events.append(
            Events(
                id=processed_event.id.value,
                account_id=processed_event.account_id.value,
                created_at=datetime.now(timezone.utc),
                timestamp=datetime.utcfromtimestamp(event_timestamp / 1000).astimezone(timezone.utc),
                event_type_id=processed_event.event_type.id,
                event_type_name=event_name,
                event_source=processed_event.event_source,
                processed_kvs=processed_kvs,
                ingested_event=json.dumps(proto_to_dict(ingested_event))
            )
        )

    if events:
        Events.objects.bulk_create(events, batch_size=1000)


def ingest_processed_monitor_transactions(processed_monitor_transactions: List[ProcessedMonitorTransaction]):
    monitor_transactions = []
    for processed_monitor_transaction in processed_monitor_transactions:
        monitor_transaction_id = processed_monitor_transaction.monitor_transaction.id.value
        transaction = processed_monitor_transaction.monitor_transaction.transaction.value
        monitor_id = processed_monitor_transaction.monitor_transaction.monitor.id
        status = processed_monitor_transaction.monitor_transaction_status

        ingestion_event: ProcessedIngestionEvent = processed_monitor_transaction.ingestion_event
        event_id = ingestion_event.id.value
        event_type_id = ingestion_event.event_type.id
        event_type_name = ingestion_event.event_type.name
        event_timestamp = ingestion_event.timestamp
        event_source = ingestion_event.event_source

        transaction_time = None
        if processed_monitor_transaction.transaction_time:
            transaction_time = processed_monitor_transaction.transaction_time.value

        processed_kvs, kvs = transform_pkvs(ingestion_event.kvs)
        ingested_event = IngestionEvent(
            name=event_type_name,
            timestamp=event_timestamp,
            kvs=kvs
        )

        monitor_transactions.append(
            MonitorTransactions(
                id=monitor_transaction_id,
                account_id=processed_monitor_transaction.account_id.value,
                monitor_id=monitor_id,
                transaction=transaction,
                status=status,
                transaction_time=transaction_time,
                event_id=event_id,
                monitor_transaction_event_type=processed_monitor_transaction.monitor_transaction_event_type,
                event_type_id=event_type_id,
                event_type_name=event_type_name,
                event_timestamp=datetime.utcfromtimestamp(event_timestamp / 1000).astimezone(timezone.utc),
                event_source=event_source,
                event_processed_kvs=processed_kvs,
                ingested_event=json.dumps(proto_to_dict(ingested_event)),
                created_at=datetime.now(timezone.utc),
            )
        )

    if monitor_transactions:
        MonitorTransactions.objects.bulk_create(monitor_transactions, batch_size=1000)
