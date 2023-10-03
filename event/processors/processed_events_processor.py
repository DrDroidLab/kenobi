from typing import List

from django.conf import settings
from google.protobuf.wrappers_pb2 import UInt64Value

from accounts.models import Account
from event.clickhouse.model_helper import ingest_processed_events
from protos.kafka.base_pb2 import ProcessedIngestionEvent
from protos.kafka.processed_events_pb2 import ProcessedEventPayloadKey, ProcessedEventPayloadValue
from prototype.kafka.processor import Processor
from prototype.kafka.producer import get_kafka_producer


def is_produce_processed_events():
    if settings.PROCESSED_EVENT_PROCESSING:
        return settings.PROCESSED_EVENT_PROCESSING.get('async', False)
    return False


def processed_event_async_producer():
    if settings.PROCESSED_EVENT_PROCESSING:
        return settings.PROCESSED_EVENT_PROCESSING.get('producer', 'processed_events')
    return 'processed_events'


def produce_account_processed_events(
        account: Account, processed_events: List[ProcessedIngestionEvent]
):
    producer = get_kafka_producer(processed_event_async_producer())
    count = 0
    for event in processed_events:
        key = ProcessedEventPayloadKey()
        value = ProcessedEventPayloadValue(
            account_id=UInt64Value(value=account.id),
            event=event,
        )
        producer.process(key, value)
        count += 1
    producer.flush()

    return count


class ProcessedEventClickhouseIngestProcessor(Processor):
    key_cls = ProcessedEventPayloadKey
    value_cls = ProcessedEventPayloadValue

    def process(self, keys: List[ProcessedEventPayloadKey], values: List[ProcessedEventPayloadValue]):
        account_processed_events_dict = {}
        for key, value in zip(keys, values):
            account_id = value.account_id.value
            processed_event = value.event

            processed_events_list: List[ProcessedIngestionEvent] = account_processed_events_dict.get(account_id, [])
            processed_events_list.append(processed_event)
            account_processed_events_dict[account_id] = processed_events_list

        for account_id, processed_events_list in account_processed_events_dict.items():
            ingest_processed_events(processed_events_list)
            print(
                f"Kafka processed-events Consume Count : {len(processed_events_list)} for account_id: {account_id}")

        return
