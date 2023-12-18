from typing import List

from django.conf import settings
from google.protobuf.wrappers_pb2 import UInt64Value

from accounts.models import Account
from event.clickhouse.model_helper import ingest_account_raw_event_stream
from event.processors.process_account_raw_event_stream import process_account_raw_event_stream
from protos.kafka.event_stream_pb2 import StreamEvent, RawEventStreamPayloadKey, RawEventStreamPayloadValue
from prototype.kafka.processor import Processor
from prototype.kafka.producer import get_kafka_producer
from prototype.utils.utils import current_datetime, current_epoch_timestamp


def is_process_event_stream_enabled():
    if settings.EVENT_STREAM_PROCESSING:
        return settings.EVENT_STREAM_PROCESSING.get('enabled', False)
    return False


def is_process_raw_event_stream_async_enabled():
    if settings.EVENT_STREAM_PROCESSING:
        return settings.EVENT_STREAM_PROCESSING.get('process_raw_event_stream_async', False)
    return False


def raw_event_stream_producer():
    if settings.EVENT_STREAM_PROCESSING:
        return settings.EVENT_STREAM_PROCESSING.get('raw_event_stream_producer', 'raw_event_stream')
    return 'raw_event_stream'


def process_raw_events_stream_payload(
        account: Account, raw_event_stream: List[StreamEvent],
):
    if not is_process_event_stream_enabled():
        print(f"Event stream processing is not enabled")
        return 0
    if is_process_raw_event_stream_async_enabled():
        process_raw_event_stream_async(account, raw_event_stream)
    else:
        process_raw_event_stream(account, raw_event_stream)
    return len(raw_event_stream)


def process_raw_event_stream_async(account: Account, raw_event_stream: List[StreamEvent]):
    producer = get_kafka_producer(raw_event_stream_producer())
    count = 0
    for event in raw_event_stream:
        key = RawEventStreamPayloadKey()
        value = RawEventStreamPayloadValue(
            account_id=UInt64Value(value=account.id),
            event=event,
        )
        producer.process(key, value)
        count += 1

    producer.flush()
    print(
        f"Kafka raw_event_stream producer flush for account id:{account.id} produce count: {count} and raw event "
        f"count: {len(raw_event_stream)} at utc time: {current_datetime()} epoch: {current_epoch_timestamp()}"
    )
    return


class RawEventStreamIngestProcessor(Processor):
    key_cls = RawEventStreamPayloadKey
    value_cls = RawEventStreamPayloadValue

    def process(self, keys: List[RawEventStreamPayloadKey], values: List[RawEventStreamPayloadValue]):
        account_processed_raw_event_stream = {}
        for key, value in zip(keys, values):
            account_id = value.account_id.value
            raw_stream_event: StreamEvent = value.event

            raw_event_stream_list: List[StreamEvent] = account_processed_raw_event_stream.get(account_id, [])
            raw_event_stream_list.append(raw_stream_event)
            account_processed_raw_event_stream[account_id] = raw_event_stream_list

        for account_id, raw_event_stream in account_processed_raw_event_stream.items():
            try:
                account: Account = Account.objects.get(id=account_id)
                process_raw_event_stream(account, raw_event_stream)
            except Account.DoesNotExist:
                print(f"Raw Event Stream consume request failed. Account not found for id: {account_id}")
                continue
        return


def process_raw_event_stream(account: Account, raw_event_stream: List[StreamEvent]):
    saved_raw_events = ingest_account_raw_event_stream(account.id, raw_event_stream)
    if not saved_raw_events:
        print(f"Unable to save raw events for account id: {account.id}")
        return
    for idx, saved_event in enumerate(saved_raw_events):
        raw_event_stream[idx].uuid_str.value = saved_event.id.hex
    process_account_raw_event_stream(account, raw_event_stream)
    return
