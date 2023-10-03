from datetime import datetime, timezone
from typing import List

from django.conf import settings
from google.protobuf.wrappers_pb2 import UInt64Value, StringValue

from accounts.models import Account
from event.models import is_transactional_key_type, Event
from event.processors.cache import GLOBAL_EVENT_KEY_CACHE, GLOBAL_EVENT_TYPE_CACHE
from event.processors.process_entities import process_event_entities, get_discovered_entity_instance_lists
from event.processors.process_monitors import generate_raw_monitor_transactions, \
    process_raw_monitor_transactions
from event.processors.processed_events_processor import is_produce_processed_events, produce_account_processed_events
from event.processors.raw_monitor_transactions_processor import is_monitor_transaction_processing_async, \
    process_raw_monitor_transactions_async
from event.processors.utils import infer_key_type
from protos.event.base_pb2 import Event as EventProto
from protos.event.schema_pb2 import IngestionEvent
from protos.kafka.base_pb2 import ProcessedIngestionEvent
from protos.kafka.raw_monitor_transactions_pb2 import RawMonitorTransactionPayloadKey, RawMonitorTransactionPayloadValue
from utils.proto_utils import get_value, proto_to_dict


def is_entity_processing_enabled():
    if settings.ENTITY_PROCESSING_ENABLED:
        return settings.ENTITY_PROCESSING_ENABLED
    return False


def process_account_events(
        account: Account, events: List[IngestionEvent],
        source: EventProto.EventSource = EventProto.EventSource.SDK,
        is_generated: bool = False, evaluate_event_monitors: bool = True
):
    db_events = []
    event_key_dict_list = []

    event_type_cache = {}
    event_key_cache = {}
    event_key_id_set = set()

    processed_ingestion_event_list: List[ProcessedIngestionEvent] = []

    for event in events:
        if event.timestamp == 0:
            event.timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        event_name: str = event.name
        if not event_name:
            continue

        if event_name not in event_type_cache:
            db_event_type, _ = GLOBAL_EVENT_TYPE_CACHE.get_or_create(name=event_name, account_id=account.id)
            event_type_sources = set(db_event_type.event_sources)
            if source not in event_type_sources:
                event_type_sources.add(source)
                db_event_type.event_sources = list(event_type_sources)
                GLOBAL_EVENT_TYPE_CACHE.update(obj=db_event_type, update_fields=["event_sources"])
            event_type_cache[event_name] = db_event_type
        else:
            db_event_type = event_type_cache[event_name]

        kv_dict = {}
        db_key_dict = {}

        event_type_key_cache = event_key_cache.get(event_name, {})
        pkvs = []
        for kv in event.kvs:
            k = kv.key
            k_type = infer_key_type(kv.value)

            if k not in event_type_key_cache:
                db_key, _ = GLOBAL_EVENT_KEY_CACHE.get_or_create(
                    event_type_id=db_event_type.id, name=k, account_id=account.id,
                    defaults={'type': k_type}
                )
                event_type_key_cache[k] = db_key
            else:
                db_key = event_type_key_cache[k]

            value = get_value(kv.value)
            if is_transactional_key_type(k_type):
                db_key_dict[db_key.id] = value
                event_key_id_set.add(db_key.id)
            kv_dict[k] = value
            pkvs.append(ProcessedIngestionEvent.ProcessedKeyValue(
                id=UInt64Value(value=db_key.id),
                key=StringValue(value=k),
                value=kv.value
            ))
        event_key_dict_list.append(db_key_dict)

        event_key_cache[event_name] = event_type_key_cache

        processed_ingestion_event_list.append(
            ProcessedIngestionEvent(
                account_id=UInt64Value(value=account.id),
                event_type=db_event_type.proto_partial,
                kvs=pkvs,
                timestamp=event.timestamp,
                event_source=source,
            )
        )

        db_event = Event(
            account=account,
            event_type=db_event_type,
            event=proto_to_dict(event),
            processed_kvs=kv_dict,
            timestamp=datetime.utcfromtimestamp(event.timestamp / 1000).astimezone(timezone.utc),
            event_source=source,
            is_generated=is_generated
        )
        db_events.append(db_event)

    saved_events: List[Event] = Event.objects.bulk_create(db_events, batch_size=25)
    for idx, saved_event in enumerate(saved_events):
        processed_ingestion_event_list[idx].id.value = saved_event.id

    if not is_generated:
        if is_produce_processed_events():
            processed_event_publish_count = produce_account_processed_events(account, processed_ingestion_event_list)
            print(
                f"Kafka processed-events Publish Count : {processed_event_publish_count} for account: {account.id}")

        event_entity_instance_lists = process_event_entities(
            account, event_key_id_set, saved_events,
            event_key_dict_list
        )
        discovered_entity_instance_lists = get_discovered_entity_instance_lists(account.id, event_entity_instance_lists)

        if evaluate_event_monitors:
            monitor_keys, monitor_values = generate_raw_monitor_transactions(
                account, event_key_id_set,
                processed_ingestion_event_list,
                event_key_dict_list,
                discovered_entity_instance_lists
            )

            process_raw_monitor_transaction_payload(monitor_keys, monitor_values)

    return len(saved_events)


def process_raw_monitor_transaction_payload(
        keys: List[RawMonitorTransactionPayloadKey], values: List[RawMonitorTransactionPayloadValue]
):
    if is_monitor_transaction_processing_async():
        publish_count = process_raw_monitor_transactions_async(keys, values)
        print(
            f"Kafka raw-monitor-transactions Publish Count : {publish_count}")
    else:
        process_raw_monitor_transactions(values)
