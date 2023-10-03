"""
# events table schema
set allow_experimental_object_type = 1;
create table events (
    id UInt64,
    account_id UInt64,
    created_at DateTime64(3, 'UTC') default now(),
    timestamp DateTime64(3, 'UTC') default now(),
    event_type_id UInt64,
    event_type_name VARCHAR(256),
    event_source UInt16,
    processed_kvs JSON,
    ingested_event  JSON,
)
engine = MergeTree()
PARTITION BY toDate(timestamp)
primary key (account_id, event_type_id, timestamp)
order by (account_id, event_type_id, timestamp)
TTL toDateTime(created_at) + INTERVAL 1 WEEK DELETE;
"""
from datetime import datetime, timezone
from typing import List
import logging
import json

from event.clickhouse.client import get_client
from event.clickhouse.tableproxy import TableProxy
from event.models import is_filterable_key_type
from event.processors.utils import infer_key_type
from protos.event.schema_pb2 import KeyValue, IngestionEvent
from protos.kafka.base_pb2 import ProcessedIngestionEvent
from utils.proto_utils import get_value, proto_to_dict
from utils.singleton import singleton, singleton_function

logger = logging.getLogger(__name__)

def processed_kvs_to_kvs(processed_kvs: List[ProcessedIngestionEvent.ProcessedKeyValue]):
    return [
        KeyValue(key=kv.key.value, value=kv.value) for kv in processed_kvs
    ]


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


@singleton
class EventsProxy(TableProxy):
    data_columns: List[str] = ['id', 'account_id', 'created_at', 'timestamp',
                               'event_type_id', 'event_type_name',
                               'event_source', 'processed_kvs', 'ingested_event']
    data_columns_types: List[str] = ['UInt64', 'UInt64', "DateTime64(3, 'UTC')",
                                     "DateTime64(3, 'UTC')", 'UInt64', 'String', 'UInt16',
                                     "Object('json')", "String"]
    table_name: str = 'events'

    def __init__(self):
        self.query_client = get_client()
        super().__init__(self.query_client)

    def _transform_processed_event(self, processed_event: ProcessedIngestionEvent):
        event_name = processed_event.event_type.name
        event_timestamp = processed_event.timestamp

        processed_kvs, kvs = transform_pkvs(processed_event.kvs)
        ingested_event = IngestionEvent(
            name=event_name,
            timestamp=event_timestamp,
            kvs=kvs
        )
        return [
            processed_event.id.value,
            processed_event.account_id.value,
            datetime.now(timezone.utc),
            datetime.utcfromtimestamp(event_timestamp / 1000).astimezone(timezone.utc),
            processed_event.event_type.id,
            event_name,
            processed_event.event_source,
            processed_kvs,
            json.dumps(proto_to_dict(ingested_event))
        ]

    def ingest_processed_events(self, processed_events: List[ProcessedIngestionEvent]):
        data = [self._transform_processed_event(processed_event) for processed_event in processed_events]
        self.insert_data(data)
        return

    def query_events(self, query: str):
        result = self.query_client.query(query)
        return result


@singleton_function
def get_events_proxy():
    return EventsProxy()
