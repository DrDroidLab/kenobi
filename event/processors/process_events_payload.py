from typing import List

from accounts.models import Account
from event.processors.process_events import process_account_events
from event.processors.raw_events_processor import is_event_processing_async, process_account_events_async
from event.processors.raw_monitor_transactions_processor import is_monitor_transaction_processing_async, \
    process_raw_monitor_transactions_async
from protos.event.base_pb2 import Event as EventProto
from protos.event.schema_pb2 import IngestionEventPayload
from protos.kafka.raw_monitor_transactions_pb2 import RawMonitorTransactionPayloadValue, RawMonitorTransactionPayloadKey


def process_account_events_payload(
        account: Account, payload: IngestionEventPayload,
        source: EventProto.EventSource = EventProto.EventSource.SDK,
        is_generated: bool = False, evaluate_event_monitors: bool = True
):
    events = payload.events
    if is_generated:
        process_account_events(account, events, source, is_generated, evaluate_event_monitors)
    if is_event_processing_async():
        publish_count = process_account_events_async(account, events, source)
        print(
            f"Kafka raw-events Publish Count : {publish_count} for account: {account.id} and events: {len(events)}")
    else:
        process_account_events(account, events, source, is_generated, evaluate_event_monitors)

    return len(events)
