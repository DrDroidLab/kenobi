from django.conf import settings

from accounts.models import Account
from protos.kafka.raw_events_pb2 import RawEventPayloadValue, RawEventPayloadKey
from prototype.kafka.producer import get_kafka_producer
from prototype.utils.utils import current_datetime, current_epoch_timestamp


def is_process_parsed_event_stream_async_enabled():
    if settings.EVENT_STREAM_PROCESSING:
        return settings.EVENT_STREAM_PROCESSING.get('process_parsed_event_stream_async', False)
    return False


def parsed_event_stream_producer():
    if settings.EVENT_STREAM_PROCESSING:
        return settings.EVENT_STREAM_PROCESSING.get('parsed_event_stream_producer', 'parsed_event_stream')
    return 'parsed_event_stream'


def process_parsed_events(account: Account, parsed_drd_events: [RawEventPayloadValue]):
    if not is_process_parsed_event_stream_async_enabled():
        print(f"Parsed event stream processing is not enabled")
        return
    producer = get_kafka_producer(parsed_event_stream_producer())
    count = 0
    for value in parsed_drd_events:
        key = RawEventPayloadKey()
        producer.process(key, value)
        count += 1
    producer.flush()
    print(f"Kafka parsed_event_stream producer flush for account id: {account.id} with publish count: {count} and "
          f"parsed event count: {len(parsed_drd_events)} at utc time: {current_datetime()} and epoch: {current_epoch_timestamp()}")
    return
