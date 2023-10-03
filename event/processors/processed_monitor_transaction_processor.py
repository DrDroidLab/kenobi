from typing import List

from django.conf import settings
from google.protobuf.wrappers_pb2 import UInt64Value

from accounts.models import Account
from event.clickhouse.model_helper import ingest_processed_monitor_transactions
from protos.kafka.base_pb2 import ProcessedMonitorTransaction
from protos.kafka.processed_monitor_transactions_pb2 import ProcessedMonitorTransactionPayloadKey, \
    ProcessedMonitorTransactionPayloadValue
from prototype.kafka.processor import Processor
from prototype.kafka.producer import get_kafka_producer


def is_produce_processed_monitor_transactions():
    if settings.PROCESSED_MONITOR_TRANSACTION_PROCESSING:
        return settings.PROCESSED_MONITOR_TRANSACTION_PROCESSING.get('async', False)
    return False


def processed_monitor_transaction_async_producer():
    if settings.PROCESSED_MONITOR_TRANSACTION_PROCESSING:
        return settings.PROCESSED_MONITOR_TRANSACTION_PROCESSING.get('producer', 'processed_monitor_transactions')
    return 'processed_monitor_transactions'


def produce_account_processed_monitor_transactions(
        account: Account, processed_monitor_transactions: List[ProcessedMonitorTransaction]
):
    producer = get_kafka_producer(processed_monitor_transaction_async_producer())
    count = 0
    for processed_monitor_transaction in processed_monitor_transactions:
        key = ProcessedMonitorTransactionPayloadKey()
        value = ProcessedMonitorTransactionPayloadValue(
            account_id=UInt64Value(value=account.id),
            processed_monitor_transaction=processed_monitor_transaction,
        )
        producer.process(key, value)
        count += 1
    producer.flush()

    return count


class ProcessedMonitorTransactionClickhouseIngestProcessor(Processor):
    key_cls = ProcessedMonitorTransactionPayloadKey
    value_cls = ProcessedMonitorTransactionPayloadValue

    def process(self, keys: List[ProcessedMonitorTransactionPayloadKey],
                values: List[ProcessedMonitorTransactionPayloadValue]):
        account_processed_monitor_transactions_dict = {}
        for key, value in zip(keys, values):
            account_id = value.account_id.value
            processed_monitor_transactions = value.processed_monitor_transaction

            processed_monitor_transactions_list: List[
                ProcessedMonitorTransaction] = account_processed_monitor_transactions_dict.get(account_id, [])
            processed_monitor_transactions_list.append(processed_monitor_transactions)
            account_processed_monitor_transactions_dict[account_id] = processed_monitor_transactions_list

        for account_id, processed_monitor_transactions_list in account_processed_monitor_transactions_dict.items():
            ingest_processed_monitor_transactions(processed_monitor_transactions_list)
            print(f"Kafka processed-monitor-transactions Consume Count : {len(processed_monitor_transactions_list)} "
                  f"for account_id: {account_id}")
        return
