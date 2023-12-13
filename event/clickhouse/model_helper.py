import logging
import uuid
from datetime import datetime
import json
from datetime import timezone
from json import JSONDecodeError
from typing import List

import pytz

from event.models import is_filterable_key_type
from event.clickhouse.models import Events, MonitorTransactions, RawEventStreamData, FilterFailedRawEventStreamData, \
    DrdEventDefinitionFailedParsedEventData, ParserFailedRawEventStreamData, FilterParsedEventData
from event.processors.utils import infer_key_type
from protos.event.schema_pb2 import KeyValue, IngestionEvent
from protos.kafka.base_pb2 import ProcessedIngestionEvent, ProcessedMonitorTransaction
from protos.kafka.event_stream_pb2 import StreamEvent
from prototype.utils.utils import current_milli_time
from utils.proto_utils import get_value, proto_to_dict

logger = logging.getLogger(__name__)


def get_data_type(input_string: str) -> StreamEvent.Type:
    try:
        if json.loads(input_string):
            return StreamEvent.Type.JSON
        else:
            return StreamEvent.Type.STRING
    except json.JSONDecodeError:
        return StreamEvent.Type.STRING


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
        try:
            Events.objects.bulk_create(events, batch_size=1000)
        except Exception as e:
            logger.error(f"Exception occurred while ingesting events with error: {e}")


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
        try:
            MonitorTransactions.objects.bulk_create(monitor_transactions, batch_size=1000)
        except Exception as e:
            logger.error(f"Exception occurred while ingesting monitor transactions with error: {e}")


def ingest_account_raw_event_stream(account_id, raw_event_stream: List[StreamEvent]):
    db_raw_events = []
    for stream_event in raw_event_stream:
        if stream_event.recorded_ingestion_timestamp is None or not stream_event.recorded_ingestion_timestamp:
            stream_event.recorded_ingestion_timestamp = current_milli_time()
        recorded_ingestion_timestamp = stream_event.recorded_ingestion_timestamp
        timestamp = datetime.utcfromtimestamp(int(recorded_ingestion_timestamp / 1000)).replace(tzinfo=pytz.utc)
        data = stream_event.event.value
        if stream_event.type is None:
            data_type = get_data_type(data)
        else:
            data_type = stream_event.type
        db_raw_events.append(
            RawEventStreamData(
                id=uuid.uuid4(),
                account_id=account_id,
                created_at=datetime.now(timezone.utc),
                timestamp=timestamp,
                event_source=stream_event.event_source,
                data=data,
                type=data_type,
            )
        )

    if db_raw_events:
        try:
            saved_raw_events = RawEventStreamData.objects.bulk_create(db_raw_events, batch_size=1000)
            return saved_raw_events
        except Exception as e:
            logger.error(f"Exception occurred while ingesting raw events with error: {e}")
    return None


def ingest_account_filter_failed_raw_event_stream(account_id, filter_failed_raw_event_stream: List[StreamEvent]):
    db_raw_events = []
    for stream_event in filter_failed_raw_event_stream:
        recorded_ingestion_timestamp = stream_event.recorded_ingestion_timestamp
        timestamp = datetime.utcfromtimestamp(int(recorded_ingestion_timestamp / 1000)).replace(tzinfo=pytz.utc)
        data = stream_event.event.value
        if stream_event.type is None:
            data_type = get_data_type(data)
        else:
            data_type = stream_event.type
        db_raw_events.append(
            RawEventStreamData(
                id=uuid.UUID(stream_event.uuid_str.value),
                account_id=account_id,
                created_at=datetime.now(timezone.utc),
                timestamp=timestamp,
                event_source=stream_event.event_source,
                data=data,
                type=data_type,
            )
        )

    if db_raw_events:
        try:
            FilterFailedRawEventStreamData.objects.bulk_create(db_raw_events, batch_size=1000)
        except Exception as e:
            logger.error(f"Exception occurred while ingesting filter failed raw events with error: {e}")


def ingest_account_drd_event_definition_failed_parsed_events(account_id, parser_drd_event_definition_failed_map: {}):
    db_parsed_events = []
    for parser_id, parsed_events in parser_drd_event_definition_failed_map.items():
        for event in parsed_events:
            if not isinstance(event, dict):
                if isinstance(event, str):
                    try:
                        json.loads(event)
                        db_event_str = event
                    except JSONDecodeError:
                        print(f"Received Invalid parsed event: {event} for parser id: {parser_id}")
                        continue
                else:
                    print(f"Received Invalid parsed event: {event} for parser id: {parser_id}")
                    continue
            else:
                db_event_str = json.dumps(event)
            recorded_ingestion_timestamp = event.get('$drd_recorded_ingestion_timestamp', current_milli_time())
            timestamp = datetime.utcfromtimestamp(int(recorded_ingestion_timestamp / 1000)).replace(tzinfo=pytz.utc)
            event_source = event.get('$drd_event_source', 0)
            raw_id = uuid.UUID(event.get('$drd_raw_event_id', uuid.uuid4().hex))
            db_parsed_events.append(
                DrdEventDefinitionFailedParsedEventData(
                    id=raw_id,
                    account_id=account_id,
                    parser_id=parser_id,
                    created_at=datetime.now(timezone.utc),
                    timestamp=timestamp,
                    event_source=event_source,
                    parsed_event=db_event_str,
                )
            )

    if db_parsed_events:
        try:
            DrdEventDefinitionFailedParsedEventData.objects.bulk_create(db_parsed_events, batch_size=1000)
        except Exception as e:
            logger.error(
                f"Exception occurred while ingesting drd event definition failed parsed events with error: {e}")


def ingest_account_parser_failed_filtered_events(account_id, filter_parser_failed_map: {}):
    db_filtered_events = []
    for filter_id, filtered_event_stream in filter_parser_failed_map.items():
        for stream_event in filtered_event_stream:
            recorded_ingestion_timestamp = stream_event.recorded_ingestion_timestamp
            timestamp = datetime.utcfromtimestamp(int(recorded_ingestion_timestamp / 1000)).replace(tzinfo=pytz.utc)
            filtered_event = stream_event.event.value
            db_filtered_events.append(
                ParserFailedRawEventStreamData(
                    id=uuid.UUID(stream_event.uuid_str.value),
                    account_id=account_id,
                    filter_id=filter_id,
                    created_at=datetime.now(timezone.utc),
                    timestamp=timestamp,
                    event_source=stream_event.event_source,
                    filtered_event_data=filtered_event,
                )
            )

    if db_filtered_events:
        try:
            ParserFailedRawEventStreamData.objects.bulk_create(db_filtered_events, batch_size=1000)
        except Exception as e:
            logger.error(f"Exception occurred while ingesting parser failed filtered events with error: {e}")


def ingest_account_filter_parsed_events(account_id, filter_id, filter_parsed_map):
    db_filter_parsed_events = []
    for parser_id, parsed_events in filter_parsed_map.items():
        for raw_event_payload in parsed_events:
            event_source = raw_event_payload.event_source
            event: IngestionEvent = raw_event_payload.event
            event_dict = proto_to_dict(event)
            db_event_str = json.dumps(event_dict)
            recorded_ingestion_timestamp = event.timestamp
            timestamp = datetime.utcfromtimestamp(int(recorded_ingestion_timestamp / 1000)).replace(tzinfo=pytz.utc)
            kvs = event.kvs
            raw_id = uuid.uuid4().hex
            if kvs:
                for kv in kvs:
                    if kv.key == '$drd_raw_event_id':
                        raw_id = uuid.UUID(kv.value.string_value)
                        break
            db_filter_parsed_events.append(
                FilterParsedEventData(
                    id=raw_id,
                    account_id=account_id,
                    filter_id=filter_id,
                    parser_id=parser_id,
                    created_at=datetime.now(timezone.utc),
                    timestamp=timestamp,
                    event_source=event_source,
                    parsed_drd_event=db_event_str,
                )
            )

    if db_filter_parsed_events:
        try:
            FilterParsedEventData.objects.bulk_create(db_filter_parsed_events, batch_size=1000)
        except Exception as e:
            logger.error(f"Exception occurred while ingesting filter parsed events with error: {e}")
