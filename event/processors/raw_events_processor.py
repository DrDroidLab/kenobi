from typing import List

from django.conf import settings
from google.protobuf.wrappers_pb2 import UInt64Value

from accounts.models import Account
from event.processors.process_events import process_account_events
from protos.event.base_pb2 import Event as EventProto
from protos.event.schema_pb2 import IngestionEvent
from protos.kafka.raw_events_pb2 import RawEventPayloadKey, RawEventPayloadValue
from prototype.kafka.processor import Processor
from prototype.kafka.producer import get_kafka_producer
from prototype.utils.utils import current_milli_time


def is_event_processing_async():
    if settings.RAW_EVENT_PROCESSING:
        return settings.RAW_EVENT_PROCESSING.get('async', False)
    return False


def event_processing_async_producer():
    if settings.RAW_EVENT_PROCESSING:
        return settings.RAW_EVENT_PROCESSING.get('producer', 'raw_events')
    return 'raw_events'


def process_account_events_async(
        account: Account, events: List[IngestionEvent],
        source: EventProto.EventSource = EventProto.EventSource.SDK
):
    producer = get_kafka_producer('raw_events')
    count = 0
    processing_time = current_milli_time()
    for event in events:
        event_name: str = event.name
        if not event_name:
            continue

        if not event.timestamp:
            event.timestamp = processing_time

        key = RawEventPayloadKey()
        value = RawEventPayloadValue(
            account_id=UInt64Value(value=account.id),
            event=event,
            event_source=source
        )
        producer.process(key, value)
        count += 1
    producer.flush()

    return count


class RawEventProcessor(Processor):
    key_cls = RawEventPayloadKey
    value_cls = RawEventPayloadValue

    def process(self, keys: List[RawEventPayloadKey], values: List[RawEventPayloadValue]):
        account_source_dict = {}
        for key, value in zip(keys, values):
            account = value.account_id.value
            source = value.event_source

            source_event_dict = account_source_dict.get(account, {})
            events = source_event_dict.get(source, [])
            if value.event:
                events.append(value.event)

            source_event_dict[source] = events
            account_source_dict[account] = source_event_dict

        for account, source_event_dict in account_source_dict.items():
            account_obj = Account(id=account)
            for source, events in source_event_dict.items():
                saved_count = process_account_events(account_obj, events, source)
                print(
                    f"Kafka raw-events Consumer Saved events Count : {saved_count} for account: {account_obj.id} and consumed events count: {len(events)}")

        return
