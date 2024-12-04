from typing import List

from django.conf import settings
from google.protobuf.wrappers_pb2 import UInt64Value

from accounts.models import Account
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
