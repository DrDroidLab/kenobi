from datetime import datetime, timezone
from typing import List, Dict

from django.db.models import Q, F, Min
from google.protobuf.wrappers_pb2 import UInt64Value, StringValue, DoubleValue

from accounts.models import Account
from event.models import MonitorTransaction, MonitorTransactionStats, MonitorTransactionEventMapping, \
    EntityInstanceMonitorTransactionMapping
from event.processors.processed_monitor_transaction_processor import is_produce_processed_monitor_transactions, \
    produce_account_processed_monitor_transactions
from protos.event.monitor_pb2 import MonitorTransaction as MonitorTransactionProto, \
    MonitorTransactionStats as MonitorTransactionStatsProto
from protos.kafka.base_pb2 import ProcessedMonitorTransaction
from protos.kafka.raw_monitor_transactions_pb2 import RawMonitorTransactionPayloadKey, RawMonitorTransactionPayloadValue
from utils.proto_utils import proto_to_dict, dict_to_proto
from utils.tracer import tracer


def generate_raw_monitor_transactions(
        account: Account,
        event_key_id_set,
        processed_ingestion_event_list,
        event_key_dict_list,
        discovered_entity_instance_lists
):
    keys = []
    values = []

    account_monitors = list(account.monitor_set.filter(
        Q(primary_key_id__in=event_key_id_set) | Q(secondary_key_id__in=event_key_id_set)
    ).exclude(is_active=False).annotate(
        monitor_id=F('id')
    ).values(
        'monitor_id', 'primary_key_id', 'secondary_key_id'
    ))

    for monitor in account_monitors:
        monitor_id, primary_key_id, secondary_key_id = monitor['monitor_id'], monitor['primary_key_id'], monitor[
            'secondary_key_id']
        for idx, (processed_ingestion_event, event_key_dict, discovered_entity_instance_list) in enumerate(
                zip(processed_ingestion_event_list, event_key_dict_list, discovered_entity_instance_lists)
        ):
            event_keys = event_key_dict.keys()
            transaction_event_type = MonitorTransactionProto.MonitorTransactionEventType.UNKNOWN_MT_ET
            transaction: str = ''
            found = False
            if primary_key_id in event_keys:
                transaction_event_type = MonitorTransactionProto.MonitorTransactionEventType.PRIMARY
                transaction = str(event_key_dict[primary_key_id])
                found = True
            elif secondary_key_id in event_keys:
                transaction_event_type = MonitorTransactionProto.MonitorTransactionEventType.SECONDARY
                transaction = str(event_key_dict[secondary_key_id])
                found = True
            if found:
                key = RawMonitorTransactionPayloadKey(
                    account_id=UInt64Value(value=account.id),
                    monitor_id=UInt64Value(value=monitor_id),
                    transaction=StringValue(value=transaction),
                )
                value = RawMonitorTransactionPayloadValue(
                    account_id=UInt64Value(value=account.id),
                    monitor_id=UInt64Value(value=monitor_id),
                    transaction=StringValue(value=transaction),
                    event=processed_ingestion_event,
                    transaction_event_type=transaction_event_type,
                    discovered_entity_instances=discovered_entity_instance_list
                )
                keys.append(key)
                values.append(value)

    return keys, values


def process_raw_monitor_transactions(
        raw_monitor_transaction_payloads: List[RawMonitorTransactionPayloadValue],
):
    account_monitor_dict = {}
    count = 0
    for raw_monitor_transaction in raw_monitor_transaction_payloads:
        account_id = raw_monitor_transaction.account_id.value
        monitor_id = raw_monitor_transaction.monitor_id.value
        transaction = raw_monitor_transaction.transaction.value

        monitor_transaction_dict = account_monitor_dict.get(account_id, {})
        transaction_payloads_dict = monitor_transaction_dict.get(monitor_id, {})
        transaction_payload_list = transaction_payloads_dict.get(transaction, [])

        transaction_payload_list.append(raw_monitor_transaction)
        transaction_payloads_dict[transaction] = transaction_payload_list
        monitor_transaction_dict[monitor_id] = transaction_payloads_dict
        account_monitor_dict[account_id] = monitor_transaction_dict
        count += 1

    _process_account_monitor_dict(account_monitor_dict)
    print(
        f"Kafka raw-monitor-transactions Consume Count : {count}")

    return


def _process_account_monitor_dict(account_monitor_dict):
    for account_id, monitor_transaction_dict in account_monitor_dict.items():
        account_obj = Account(id=account_id)
        processed_account_monitor_transactions_protos = []
        for monitor_id, transaction_payloads_dict in monitor_transaction_dict.items():
            with tracer.trace('process.monitor_transaction') as span:
                span.set_tag('account_id', account_id)
                span.set_tag('monitor_id', monitor_id)
                span.set_tag('transaction_count', len(transaction_payloads_dict))
                try:
                    processed_monitor_transactions_protos = _process_raw_monitor_transactions_for_monitor_id(
                        account_obj, monitor_id,
                        transaction_payloads_dict
                    )
                    if processed_monitor_transactions_protos:
                        processed_account_monitor_transactions_protos.extend(processed_monitor_transactions_protos)
                except Exception as e:
                    span.set_traceback()
        if is_produce_processed_monitor_transactions():
            processed_monitor_transaction_publish_count = produce_account_processed_monitor_transactions(account_obj,
                                                                                                         processed_account_monitor_transactions_protos)
            print(
                f"Kafka processed-monitor-transactions Publish Count : {processed_monitor_transaction_publish_count} for account: {account_obj.id}")


def _process_raw_monitor_transactions_for_monitor_id(
        account: Account, monitor_id: int, transaction_payloads_dict: Dict[str, List[RawMonitorTransactionPayloadValue]]
):
    discovered_transactions_set = set(transaction_payloads_dict.keys())
    existing_db_transactions = list(account.monitortransaction_set.filter(
        monitor_id=monitor_id,
        transaction__in=discovered_transactions_set,
    ).values('id', 'transaction', 'type'))

    existing_transaction_set = set(
        [existing_transaction['transaction'] for existing_transaction in existing_db_transactions]
    )
    missing_transactions = set(discovered_transactions_set).difference(existing_transaction_set)
    missing_transaction_objs = [
        MonitorTransaction(
            account=account, monitor_id=monitor_id, transaction=missing_transaction,
            type=MonitorTransactionProto.MonitorTransactionStatus.PRIMARY_RECEIVED
        ) for missing_transaction in missing_transactions
    ]
    missing_db_transactions = list(MonitorTransaction.objects.bulk_create(
        missing_transaction_objs, batch_size=50,
    ))

    db_transactions = {
        **{
            existing_db_transaction['transaction']: MonitorTransaction(
                id=existing_db_transaction['id'],
                account=account, monitor_id=monitor_id, transaction=existing_db_transaction['transaction'],
                type=existing_db_transaction['type']
            )
            for existing_db_transaction in existing_db_transactions
        },
        **{
            missing_db_transaction.transaction: missing_db_transaction
            for missing_db_transaction in missing_db_transactions
        }
    }

    mtems = []
    update_db_transaction_type_set = set()
    eimtms = []
    db_transaction_id_set = set()
    processed_monitor_transactions_dict = {}
    for db_transaction_str, db_transaction in db_transactions.items():
        db_transaction_id = db_transaction.id
        db_transaction_id_set.add(db_transaction_id)
        payloads: List[RawMonitorTransactionPayloadValue] = transaction_payloads_dict[db_transaction_str]
        db_transaction_type = db_transaction.type
        is_db_transaction_type_updated = False
        entity_instance_dict = {}
        processed_monitor_transactions_list = processed_monitor_transactions_dict.get(db_transaction_id, [])
        for payload in payloads:
            mtems.append(MonitorTransactionEventMapping(
                account=account,
                monitor_transaction=db_transaction,
                event_id=payload.event.id.value,
                type=payload.transaction_event_type,
                event_timestamp=datetime.utcfromtimestamp(payload.event.timestamp / 1000).astimezone(timezone.utc),
            ))
            transaction_event_type = payload.transaction_event_type
            if transaction_event_type == MonitorTransactionProto.MonitorTransactionEventType.PRIMARY:
                if db_transaction_type == MonitorTransactionProto.MonitorTransactionStatus.UNKNOWN:
                    db_transaction_type = MonitorTransactionProto.MonitorTransactionStatus.PRIMARY_RECEIVED
                    is_db_transaction_type_updated = True
            elif transaction_event_type == MonitorTransactionProto.MonitorTransactionEventType.SECONDARY:
                if db_transaction.type != MonitorTransactionProto.MonitorTransactionStatus.SECONDARY_RECEIVED:
                    db_transaction_type = MonitorTransactionProto.MonitorTransactionStatus.SECONDARY_RECEIVED
                    is_db_transaction_type_updated = True
            if is_db_transaction_type_updated:
                db_transaction.type = db_transaction_type
                update_db_transaction_type_set.add(db_transaction)
            processed_monitor_transactions_list.append(
                {
                    'account_id': account.id,
                    'monitor_transaction': {
                        'id': db_transaction_id,
                        'transaction': db_transaction_str,
                        'monitor': {
                            'id': monitor_id
                        }
                    },
                    'monitor_transaction_status': db_transaction_type,
                    'ingestion_event': proto_to_dict(payload.event),
                    'monitor_transaction_event_type': transaction_event_type,
                    'transaction_time': None
                }
            )
            for discovered_entity in payload.discovered_entity_instances:
                if discovered_entity.entity_instance_id.value not in entity_instance_dict:
                    entity_instance_dict[discovered_entity.entity_instance_id.value] = {
                        'entity_instance_id': discovered_entity.entity_instance_id.value,
                        'entity_id': discovered_entity.entity_id.value,
                        'instance': discovered_entity.instance.value,
                    }
        for entity_instance_id, entity_instance in entity_instance_dict.items():
            eimtms.append(EntityInstanceMonitorTransactionMapping(
                account=account,
                **entity_instance,
                monitor_transaction=db_transaction,
                monitor_id=monitor_id,
                transaction=db_transaction_str
            ))
        processed_monitor_transactions_dict[db_transaction_id] = processed_monitor_transactions_list

    if update_db_transaction_type_set:
        account.monitortransaction_set.bulk_update(
            update_db_transaction_type_set, batch_size=100, fields=['type'],
        )
    if mtems:
        account.monitortransactioneventmapping_set.bulk_create(
            mtems, batch_size=100, ignore_conflicts=True
        )
    if eimtms:
        account.entityinstancemonitortransactionmapping_set.bulk_create(
            eimtms, batch_size=100, ignore_conflicts=True
        )
    monitor_transaction_event_timestamps = list(account.monitortransactioneventmapping_set.filter(
        monitor_transaction_id__in=db_transaction_id_set,
    ).values('monitor_transaction_id', 'type').annotate(
        min_event_timestamp=Min('event_timestamp')
    ))

    primary_timestamps = {
        monitor_transaction_event_timestamp['monitor_transaction_id']:
            monitor_transaction_event_timestamp['min_event_timestamp']
        for monitor_transaction_event_timestamp in monitor_transaction_event_timestamps
        if monitor_transaction_event_timestamp['type'] == MonitorTransactionProto.MonitorTransactionEventType.PRIMARY
    }

    secondary_timestamps = {
        monitor_transaction_event_timestamp['monitor_transaction_id']:
            monitor_transaction_event_timestamp['min_event_timestamp']
        for monitor_transaction_event_timestamp in monitor_transaction_event_timestamps
        if monitor_transaction_event_timestamp['type'] == MonitorTransactionProto.MonitorTransactionEventType.SECONDARY
    }

    monitor_transaction_id_stat_dict = {}
    for monitor_transaction_id, primary_timestamp in primary_timestamps.items():
        if monitor_transaction_id in secondary_timestamps:
            delta = secondary_timestamps[monitor_transaction_id] - primary_timestamps[monitor_transaction_id]
            monitor_transaction_id_stat_dict[monitor_transaction_id] = MonitorTransactionStats(
                account=account,
                monitor_transaction_id=monitor_transaction_id,
                stats=proto_to_dict(MonitorTransactionStatsProto(
                    transaction_time=DoubleValue(value=delta.total_seconds())
                ))
            )
            processed_monitor_transactions = processed_monitor_transactions_dict[monitor_transaction_id]
            for processed_monitor_transaction in processed_monitor_transactions:
                if processed_monitor_transaction['monitor_transaction_event_type'] == \
                        MonitorTransactionProto.MonitorTransactionEventType.SECONDARY:
                    processed_monitor_transaction['transaction_time'] = delta.total_seconds()

    existing_monitor_transaction_stats_ids = list(account.monitortransactionstats_set.filter(
        monitor_transaction_id__in=set(monitor_transaction_id_stat_dict.keys()),
    ).values('id', 'monitor_transaction_id'))

    existing_stats = []
    for existing_monitor_transaction_stats_id in existing_monitor_transaction_stats_ids:
        stat = monitor_transaction_id_stat_dict.pop(existing_monitor_transaction_stats_id['monitor_transaction_id'])
        stat.id = existing_monitor_transaction_stats_id['id']
        existing_stats.append(stat)

    new_stats = [id_stat for monitor_tranaction_id, id_stat in monitor_transaction_id_stat_dict.items()]

    if existing_stats:
        account.monitortransactionstats_set.bulk_update(existing_stats, batch_size=50, fields=['stats'])
    if new_stats:
        account.monitortransactionstats_set.bulk_create(new_stats, batch_size=50, ignore_conflicts=True)

    processed_monitor_transactions_protos: [ProcessedMonitorTransaction] = []
    for db_transaction_id, processed_monitor_transactions_list in processed_monitor_transactions_dict.items():
        for processed_monitor_transaction in processed_monitor_transactions_list:
            processed_monitor_transactions_protos.append(
                dict_to_proto(processed_monitor_transaction, ProcessedMonitorTransaction))
    return processed_monitor_transactions_protos
