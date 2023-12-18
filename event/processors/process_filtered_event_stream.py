from typing import Dict, List

from django.conf import settings

from accounts.models import Account
from connectors.engine.event_stream_processing_parser_engine import parse_filtered_event_stream
from event.clickhouse.model_helper import ingest_account_parser_failed_filtered_events
from event.processors.process_parsed_event_stream import process_parsed_events
from protos.kafka.event_stream_pb2 import FilteredEventStreamPayloadKey, FilteredEventStreamPayloadValue, StreamEvent
from prototype.kafka.processor import Processor
from prototype.kafka.producer import get_kafka_producer
from prototype.utils.utils import current_datetime, current_epoch_timestamp


def is_process_filtered_event_stream_async_enabled():
    if settings.EVENT_STREAM_PROCESSING:
        return settings.EVENT_STREAM_PROCESSING.get('process_filtered_event_stream_async', False)
    return False


def filtered_event_stream_producer():
    if settings.EVENT_STREAM_PROCESSING:
        return settings.EVENT_STREAM_PROCESSING.get('filtered_event_stream_producer', 'filtered_event_stream')
    return 'filtered_event_stream'


def process_account_filtered_event_stream(account: Account, filtered_event_stream_map: Dict):
    if is_process_filtered_event_stream_async_enabled():
        process_filtered_event_stream_async(account, filtered_event_stream_map)
    else:
        process_filtered_event_stream(account, filtered_event_stream_map)
    return


def process_filtered_event_stream_async(account: Account, filter_stream_map: dict):
    producer = get_kafka_producer(filtered_event_stream_producer())
    count = 0
    all_event_count = 0
    for filter_id, event_stream in filter_stream_map.items():
        all_event_count += len(event_stream)
        for event in event_stream:
            key = FilteredEventStreamPayloadKey()
            value = FilteredEventStreamPayloadValue(
                account_id=account.id,
                filter_id=filter_id,
                event=event,
            )
            producer.process(key, value)
            count += 1
    producer.flush()
    print(
        f"Kafka filtered_event_stream producer flush for account id:{account.id} produce count: {count} and event "
        f"count: {all_event_count} at utc time: {current_datetime()} epoch: {current_epoch_timestamp()}"
    )
    return count


class FilteredEventStreamProcessor(Processor):
    key_cls = FilteredEventStreamPayloadKey
    value_cls = FilteredEventStreamPayloadValue

    def process(self, keys: List[FilteredEventStreamPayloadKey], values: List[FilteredEventStreamPayloadValue]):
        account_filter_event_stream_map = {}
        for key, value in zip(keys, values):
            account_id = value.account_id.value
            filter_id = value.filter_id.value
            filtered_event: StreamEvent = value.event
            filter_stream_event_map = account_filter_event_stream_map.get(account_id, {})
            filtered_stream_event_list: [StreamEvent] = filter_stream_event_map.get(filter_id, [])
            filtered_stream_event_list.append(filtered_event)
            filter_stream_event_map[filter_id] = filtered_stream_event_list
            account_filter_event_stream_map[account_id] = filter_stream_event_map
        for account_id, filter_event_stream_map in account_filter_event_stream_map.items():
            try:
                account: Account = Account.objects.get(id=account_id)
                process_filtered_event_stream(account, filter_event_stream_map)
            except Account.DoesNotExist:
                print(f"Filtered Event Stream consume request failed. Account not found for id: {account_id}")
                continue
        return


def process_filtered_event_stream(account: Account, filter_event_stream_map):
    parsed_drd_events_list, parser_failed_filter_map = parse_filtered_event_stream(account, filter_event_stream_map)
    ingest_account_parser_failed_filtered_events(account.id, parser_failed_filter_map)
    process_parsed_events(account, parsed_drd_events_list)
    return
