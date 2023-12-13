from typing import List

from django.conf import settings
from google.protobuf.wrappers_pb2 import UInt64Value

from accounts.models import Account
from connectors.engine.event_stream_processing_filter_engine import filter_event_stream
from event.clickhouse.model_helper import ingest_account_filter_failed_raw_event_stream
from event.processors.process_filtered_event_stream import process_account_filtered_event_stream
from protos.kafka.event_stream_pb2 import StreamEvent, RawEventStreamPayloadKey, RawEventStreamPayloadValue
from prototype.kafka.processor import Processor
from prototype.kafka.producer import get_kafka_producer
from prototype.utils.utils import current_datetime, current_epoch_timestamp


def is_process_account_event_stream_async_enabled():
    if settings.EVENT_STREAM_PROCESSING:
        return settings.EVENT_STREAM_PROCESSING.get('process_account_raw_event_stream_async', False)
    return False


def account_event_stream_producer():
    if settings.EVENT_STREAM_PROCESSING:
        return settings.EVENT_STREAM_PROCESSING.get('account_event_stream_producer', 'account_event_stream')
    return 'account_event_stream'


def process_account_raw_event_stream(account: Account, raw_event_stream: List[StreamEvent]):
    if is_process_account_event_stream_async_enabled():
        process_account_event_stream_async(account, raw_event_stream)
    else:
        process_account_event_stream(account, raw_event_stream)
    return


def process_account_event_stream_async(account: Account, event_stream: List[StreamEvent]):
    producer = get_kafka_producer(account_event_stream_producer())
    count = 0
    for event in event_stream:
        key = RawEventStreamPayloadKey()
        value = RawEventStreamPayloadValue(
            account_id=UInt64Value(value=account.id),
            event=event,
        )
        producer.process(key, value)
        count += 1

    producer.flush()
    print(
        f"Kafka account_event_stream producer flush for account id:{account.id} produce count: {count} and event "
        f"count: {len(event_stream)} at utc time: {current_datetime()} epoch: {current_epoch_timestamp()}"
    )
    return


class AccountRawEventStreamProcessor(Processor):
    key_cls = RawEventStreamPayloadKey
    value_cls = RawEventStreamPayloadValue

    def process(self, keys: List[RawEventStreamPayloadKey], values: List[RawEventStreamPayloadValue]):
        account_raw_event_stream_map = {}
        for key, value in zip(keys, values):
            account_id = value.account_id.value
            event: StreamEvent = value.event
            event_stream_list: [StreamEvent] = account_raw_event_stream_map.get(account_id, [])
            event_stream_list.append(event)
            account_raw_event_stream_map[account_id] = event_stream_list
        for account_id, event_stream in account_raw_event_stream_map.items():
            try:
                account: Account = Account.objects.get(id=account_id)
                process_account_event_stream(account, event_stream)
            except Account.DoesNotExist:
                print(f"Account Raw Event Stream consume request failed. Account not found for id: {account_id}")
                continue
        return


def process_account_event_stream(account: Account, event_stream: [StreamEvent]):
    filtered_event_stream_map, all_un_filtered_events = filter_event_stream(account, event_stream)
    ingest_account_filter_failed_raw_event_stream(account.id, all_un_filtered_events)
    process_account_filtered_event_stream(account, filtered_event_stream_map)
    return
