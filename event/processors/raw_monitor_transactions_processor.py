from typing import List

from django.conf import settings

from event.processors.process_monitors import process_raw_monitor_transactions
from protos.kafka.raw_monitor_transactions_pb2 import RawMonitorTransactionPayloadKey, RawMonitorTransactionPayloadValue
from prototype.kafka.processor import Processor
from prototype.kafka.producer import get_kafka_producer


def is_monitor_transaction_processing_async():
    if settings.RAW_MONITOR_TRANSACTION_PROCESSING:
        return settings.RAW_MONITOR_TRANSACTION_PROCESSING.get('async', False)
    return False


def monitor_transaction_processing_async_producer():
    if settings.RAW_MONITOR_TRANSACTION_PROCESSING:
        return settings.RAW_MONITOR_TRANSACTION_PROCESSING.get('producer', 'raw_monitor_transactions')
    return 'raw_monitor_transactions'


def process_raw_monitor_transactions_async(
        keys: List[RawMonitorTransactionPayloadKey], values: List[RawMonitorTransactionPayloadValue]
):
    producer = get_kafka_producer(monitor_transaction_processing_async_producer())
    count = 0
    for key, value in zip(keys, values):
        producer.process(key, value)
        count += 1
    producer.flush()

    return count


class RawMonitorTransactionProcessor(Processor):
    key_cls = RawMonitorTransactionPayloadKey
    value_cls = RawMonitorTransactionPayloadValue

    def process(self, keys: List[RawMonitorTransactionPayloadKey], values: List[RawMonitorTransactionPayloadValue]):
        return process_raw_monitor_transactions(values)
