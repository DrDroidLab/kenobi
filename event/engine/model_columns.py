from functools import lru_cache
from typing import Dict

from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from django.db.models import Value, F, Exists, OuterRef, Subquery
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import TruncSecond, Cast
from google.protobuf.wrappers_pb2 import UInt64Value

from accounts.models import Account, get_request_account
from event.base.column import Column, AnnotatedColumn, AttributeColumn, AttributeColumnV2
from event.base.filter_token_op import LiteralArrayColumnTokenFilterOp
from event.base.literal import event_key_type_to_literal_type, literal_type_is_groupable, \
    literal_type_aggregation_functions
from event.models import AlertMonitorTransactionMapping, MonitorTransactionEventMapping, MonitorTransaction, \
    EntityInstanceEventMapping
from protos.event.engine_options_pb2 import AttributeOption, AttributeOptionV2
from protos.event.literal_pb2 import LiteralType, IdLiteral
from protos.event.metric_pb2 import AggregationFunction
from protos.event.monitor_pb2 import MonitorTransaction as MonitorTransactionProto

transaction_status_options = {
    MonitorTransactionProto.MonitorTransactionStatus.PRIMARY_RECEIVED: 'Active',
    MonitorTransactionProto.MonitorTransactionStatus.SECONDARY_RECEIVED: 'Finished',
}


def transaction_status_options_cb(account, obj):
    return transaction_status_options


def get_enum_id_column_option_cb(proto_enum):
    def _enum_id_options(account, obj):
        return {v: k for k, v in proto_enum.items() if v != 0}

    return _enum_id_options


def get_id_option_cb(account_scope_cb):
    def _id_options(account, obj):
        if obj is not None:
            return {obj.id: obj.name}
        return {elem['id']: elem['name'] for elem in account_scope_cb(account).values('id', 'name')}

    return _id_options


def get_event_attribute_options(path, display_name, account, obj):
    if obj:
        qs = account.eventkey_set.filter(event_type=obj)
    else:
        qs = account.eventkey_set.all()

    qs = qs.select_related(
        'event_type'
    ).values('id', 'name', 'type', 'event_type__id', 'event_type__name')

    attribute_options: [AttributeOption] = []

    for q in qs:
        literal_type = event_key_type_to_literal_type(q['type'])
        attribute_options.append(
            AttributeOption(
                name=q['name'], path=path, type=literal_type,
                column_context=[
                    AttributeOption.ColumnContext(
                        alias='event_type_id',
                        id=IdLiteral(
                            long=UInt64Value(value=q['event_type__id']),
                            type=IdLiteral.Type.LONG
                        )
                    )
                ],
                is_groupable=literal_type_is_groupable(literal_type),
                aggregation_functions=literal_type_aggregation_functions(literal_type),
            )
        )

    return attribute_options


def get_monitor_attribute_options_cb(key='primary_key'):
    def get_monitor_attribute_options(path, display_name, account, obj):
        if obj:
            qs = account.monitor_set.filter(id=obj.id)
        else:
            qs = account.monitor_set.exclude(is_active=False)

        key_event_type_id = f'{key}__event_type__id'
        key_event_type_name = f'{key}__event_type__name'

        qs = qs.select_related(key, f'{key}__event_type').values(
            'id', 'name', key,
            key_event_type_id,
            key_event_type_name,
        )

        attribute_options: [AttributeOption] = []
        for monitor in qs:
            event_keys_qs = account.eventkey_set.filter(
                event_type=monitor[key_event_type_id]
            ).values(
                'id',
                'name',
                'type'
            )
            path_alias = f"{monitor[key_event_type_name]} ({display_name})"

            for ek in event_keys_qs:
                literal_type = event_key_type_to_literal_type(ek['type'])
                attribute_options.append(
                    AttributeOption(
                        name=ek['name'], path=path, type=literal_type,
                        path_alias=path_alias,
                        column_context=[
                            AttributeOption.ColumnContext(
                                alias='monitor_id',
                                id=IdLiteral(
                                    long=UInt64Value(value=monitor['id']),
                                    type=IdLiteral.Type.LONG
                                )
                            )
                        ],
                        is_groupable=literal_type_is_groupable(literal_type),
                        aggregation_functions=literal_type_aggregation_functions(literal_type),
                    )
                )
        return attribute_options

    return get_monitor_attribute_options


def get_monitor_attribute_options_v2(account, obj):
    if obj:
        qs = account.monitor_set.filter(id=obj.id)
    else:
        qs = account.monitor_set.exclude(is_active=False)

    attribute_options: [AttributeOptionV2] = []
    attribute_options_dict = {}
    for key in ['primary_key', 'secondary_key']:

        key_event_type_id = f'{key}__event_type__id'
        key_event_type_name = f'{key}__event_type__name'

        eqs = qs.select_related(key, f'{key}__event_type').values(
            'id', 'name', key,
            key_event_type_id,
            key_event_type_name,
        )

        for monitor in eqs:
            event_keys_qs = account.eventkey_set.filter(
                event_type=monitor[key_event_type_id]
            ).values(
                'id',
                'name',
                'type'
            )

            path = "monitor__{}__event_type".format(key)

            for ek in event_keys_qs:
                literal_type = event_key_type_to_literal_type(ek['type'])
                if f"{ek['name']}##{literal_type}" not in attribute_options_dict:
                    attribute_options_dict[f"{ek['name']}##{literal_type}"] = []
                attribute_options_dict[f"{ek['name']}##{literal_type}"].append(path)

    for key, value in attribute_options_dict.items():
        paths = list(set(value))
        name = key.split("##")[0]
        literal_type = int(key.split("##")[1])
        attribute_options.append(
            AttributeOptionV2(
                name=name,
                path=paths,
                type=literal_type,
            )
        )
    return attribute_options


def get_entity_attribute_options_v2(account, obj):
    if obj:
        qs = account.entityeventkeymapping_set.filter(entity_id=obj.id)
    else:
        qs = account.entityeventkeymapping_set.exclude(is_active=False)

    attribute_options: [AttributeOptionV2] = []
    attribute_options_dict = {}
    qs = qs.select_related('event_key__event_type').values('event_key__event_type__id')
    for q in qs:
        event_type_id = q["event_key__event_type__id"]

        event_keys_qs = account.eventkey_set.filter(event_type=event_type_id).values('id', 'name', 'type')

        path = str(event_type_id)
        for ek in event_keys_qs:
            literal_type = event_key_type_to_literal_type(ek['type'])
            if f"{ek['name']}##{literal_type}" not in attribute_options_dict:
                attribute_options_dict[f"{ek['name']}##{literal_type}"] = []
            attribute_options_dict[f"{ek['name']}##{literal_type}"].append(path)

    for key, value in attribute_options_dict.items():
        paths = list(set(value))
        name = key.split("##")[0]
        literal_type = int(key.split("##")[1])
        attribute_options.append(
            AttributeOptionV2(
                name=name,
                path=paths,
                type=literal_type,
            )
        )
    return attribute_options


@lru_cache(maxsize=256)
def get_event_type_name_from_id(account_id, event_type_id):
    return Account(id=account_id).eventtype_set.filter(id=event_type_id).values_list('name', flat=True)[0]


@lru_cache(maxsize=256)
def get_monitor_name_from_id(account_id, monitor_id):
    return Account(id=account_id).monitor_set.filter(id=monitor_id).values_list('name', flat=True)[0]


@lru_cache(maxsize=256)
def get_entity_name_from_id(account_id, entity_id):
    return Account(id=account_id).entity_set.filter(id=entity_id).values_list('name', flat=True)[0]


def resolve_transaction_status_options(transaction_status):
    return transaction_status_options[transaction_status]


def get_resolve_column_id_cb(get_obj_name_from_id_cb):
    def _resolve_column_id(column_id):
        account = get_request_account()
        return get_obj_name_from_id_cb(account.id, column_id)

    return _resolve_column_id


event_columns = {
    'event_type_id': Column(
        name='event_type_id',
        display_name='Event Type',
        type=LiteralType.ID,
        id_options_cb=get_id_option_cb(
            lambda account: account.eventtype_set
        ),
        is_groupable=True,
        is_orderable=False,
        is_filterable=True,
        aggregation_functions=[AggregationFunction.COUNT],
        id_label_resolver_cb=get_resolve_column_id_cb(get_event_type_name_from_id),
    ),
    'timestamp_in_seconds': AnnotatedColumn(
        name='timestamp_in_seconds',
        annotation_relation=TruncSecond('timestamp'),
        type=LiteralType.TIMESTAMP,
        display_name='Timestamp (Seconds)',
        is_groupable=False,
        is_filterable=True,
        is_orderable=True,
        aggregation_functions=[AggregationFunction.MIN, AggregationFunction.MAX],
    ),
    'timestamp': Column(
        name='timestamp',
        type=LiteralType.TIMESTAMP,
        display_name='Timestamp',
        is_groupable=False,
        is_orderable=True,
        is_filterable=False,
        aggregation_functions=[AggregationFunction.MIN, AggregationFunction.MAX],
    ),
    'monitor_transaction': AnnotatedColumn(
        name='monitor_transaction',
        display_name='Monitor Transaction',
        type=LiteralType.STRING,
        annotation_relation=ArrayAgg(
            'monitortransactioneventmapping__monitor_transaction__transaction',
            default=Value([])
        ),
        token_filter_op=LiteralArrayColumnTokenFilterOp(),
        is_groupable=False,
        is_filterable=True,
        is_orderable=False,
    ),
    'event_attribute': AttributeColumn(
        name='event_attribute',
        annotation_relation=F('processed_kvs'),
        display_name='Event Attribute',
        attribute_options_cb=get_event_attribute_options,
        attribute_field='processed_kvs',
        is_filterable=True
    )
}

events_clickhouse_columns = {
    'event_type_id': Column(
        name='event_type_id',
        display_name='Event Type',
        type=LiteralType.ID,
        id_options_cb=get_id_option_cb(
            lambda account: account.eventtype_set
        ),
        is_groupable=True,
        is_orderable=False,
        is_filterable=True,
        aggregation_functions=[AggregationFunction.COUNT],
        id_label_resolver_cb=get_resolve_column_id_cb(get_event_type_name_from_id),
    ),
    'timestamp_in_seconds': AnnotatedColumn(
        name='timestamp_in_seconds',
        annotation_relation=TruncSecond('timestamp'),
        type=LiteralType.TIMESTAMP,
        display_name='Timestamp (Seconds)',
        is_groupable=False,
        is_orderable=True,
        is_filterable=True,
        aggregation_functions=[AggregationFunction.MIN, AggregationFunction.MAX],
    ),
    'timestamp': Column(
        name='timestamp',
        type=LiteralType.TIMESTAMP,
        display_name='Timestamp',
        is_groupable=False,
        is_orderable=True,
        is_filterable=False,
        aggregation_functions=[AggregationFunction.MIN, AggregationFunction.MAX],
    ),
    'event_attribute': AttributeColumn(
        name='event_attribute',
        annotation_relation=F('processed_kvs'),
        display_name='Event Attribute',
        attribute_options_cb=get_event_attribute_options,
        attribute_field='processed_kvs',
        is_filterable=True
    )
}

monitor_transaction_columns = {
    'monitor_id': Column(
        name='monitor_id',
        type=LiteralType.ID,
        display_name='Monitor',
        id_options_cb=get_id_option_cb(
            lambda account: account.monitor_set.exclude(is_active=False)
        ),
        is_groupable=True,
        is_orderable=False,
        is_filterable=True,
        aggregation_functions=[AggregationFunction.COUNT],
        id_label_resolver_cb=get_resolve_column_id_cb(get_monitor_name_from_id),
    ),
    'transaction': Column(
        name='transaction',
        type=LiteralType.STRING,
        display_name='Transaction Value',
        is_groupable=False,
        is_orderable=False,
        is_filterable=True,
    ),
    'type': Column(
        name='type',
        type=LiteralType.ID,
        display_name='Transaction Status',
        id_options_cb=transaction_status_options_cb,
        is_groupable=True,
        is_orderable=False,
        is_filterable=True,
        aggregation_functions=[AggregationFunction.COUNT, AggregationFunction.COUNT_DISTINCT],
        id_label_resolver_cb=resolve_transaction_status_options,
    ),
    'transaction_time': AnnotatedColumn(
        name='transaction_time',
        annotation_relation=Cast(
            KeyTextTransform("transaction_time", "monitortransactionstats__stats"), models.FloatField()
        ),
        type=LiteralType.DOUBLE,
        display_name='Transaction Time',
        is_groupable=False,
        is_orderable=True,
        is_filterable=True,
        aggregation_functions=literal_type_aggregation_functions(LiteralType.DOUBLE),
    ),
    'created_at': Column(
        name='created_at',
        type=LiteralType.TIMESTAMP,
        display_name='Created At',
        is_groupable=False,
        is_orderable=True,
        is_filterable=False,
        aggregation_functions=[AggregationFunction.MIN, AggregationFunction.MAX],
    ),
    'has_alerts': AnnotatedColumn(
        name='has_alerts',
        annotation_relation=Exists(
            AlertMonitorTransactionMapping.objects.filter(
                monitor_transaction=OuterRef('pk')).filter(
                created_at__gte=OuterRef('created_at'))
        ),
        type=LiteralType.BOOLEAN,
        display_name='Alerted',
        is_groupable=True,
        is_orderable=False,
        is_filterable=True,
        aggregation_functions=literal_type_aggregation_functions(LiteralType.BOOLEAN),
    ),
    'primary_event_attribute': AttributeColumn(
        name='primary_event_attribute',
        annotation_relation=Subquery(
            MonitorTransactionEventMapping.objects.filter(
                monitor_transaction=OuterRef("pk")).filter(
                event__event_type=OuterRef(
                    "monitor__primary_key__event_type__id")).values(
                'event__processed_kvs').order_by(
                'event__timestamp')[:1]
        ),
        display_name='Primary Event',
        attribute_options_cb=get_monitor_attribute_options_cb(key='primary_key'),
        is_filterable=True
    ),
    'secondary_event_attribute': AttributeColumn(
        name='secondary_event_attribute',
        annotation_relation=Subquery(
            MonitorTransactionEventMapping.objects.filter(
                monitor_transaction=OuterRef("pk")).filter(
                event__event_type=OuterRef(
                    "monitor__secondary_key__event_type")).values(
                'event__processed_kvs').order_by(
                'event__timestamp')[:1]
        ),
        display_name='Secondary Event',
        attribute_options_cb=get_monitor_attribute_options_cb(key='secondary_key'),
        is_filterable=True
    ),
    'free_attribute_search_column': AttributeColumnV2(
        name='free_attribute_search_column',
        general_annotation_relation="Subquery(MonitorTransactionEventMapping.objects.filter(monitor_transaction=OuterRef('pk')).filter(event__event_type=OuterRef('{}')).values('event__processed_kvs').order_by('event__timestamp')[:1])",
        display_name='Attribute Search',
        associated_model_name='MonitorTransactionEventMapping',
        associated_model=MonitorTransactionEventMapping,
        attribute_options_cb_v2=get_monitor_attribute_options_v2,
        is_filterable=True
    )
}

entity_instance_columns = {
    'entity_id': Column(
        name='entity_id',
        type=LiteralType.ID,
        display_name='Entity',
        id_options_cb=get_id_option_cb(
            lambda account: account.entity_set.exclude(is_active=False)
        ),
        is_groupable=True,
        is_orderable=False,
        is_filterable=True,
        aggregation_functions=[AggregationFunction.COUNT],
        id_label_resolver_cb=get_resolve_column_id_cb(get_entity_name_from_id),
    ),
    'instance': Column(
        name='instance',
        type=LiteralType.STRING,
        display_name='Entity Instance Value',
        is_groupable=False,
        is_orderable=False,
        is_filterable=True,
    ),
    'has_alerts': AnnotatedColumn(
        name='has_alerts',
        annotation_relation=Exists(
            AlertMonitorTransactionMapping.objects.filter(
                monitor_transaction__entityinstancemonitortransactionmapping__entity_instance=OuterRef('pk')).filter(
                created_at__gte=OuterRef('created_at'))
        ),
        type=LiteralType.BOOLEAN,
        display_name='Alerted',
        is_groupable=True,
        is_orderable=False,
        aggregation_functions=literal_type_aggregation_functions(LiteralType.BOOLEAN),
        is_filterable=True,
    ),
    'free_attribute_search_column': AttributeColumnV2(
        name='free_attribute_search_column',
        general_annotation_relation="Subquery(EntityInstanceEventMapping.objects.filter(entity_instance=OuterRef('pk')).filter(event__event_type_id={}).values('event_processed_kvs').order_by('event_timestamp')[:1])",
        display_name='Attribute Search',
        associated_model_name='EntityInstanceEventMapping',
        associated_model=EntityInstanceEventMapping,
        attribute_options_cb_v2=get_entity_attribute_options_v2,
        is_filterable=True
    )
}


class ColumnOptions:
    def __init__(self, columns: Dict):
        self._columns = columns

    def options(self, account, obj=None):
        column_options = []
        attribute_options = []
        for column_name, column in self._columns.items():
            if column.is_filterable:
                if isinstance(column, Column):
                    column_options.append(column.get_options(account, obj))
                elif isinstance(column, AttributeColumn):
                    attribute_options.extend(column.get_options(account, obj))

        return column_options, attribute_options

    def options_v2(self, account, obj=None):
        column_options = []
        attribute_options_v2 = []
        for column_name, column in self._columns.items():
            if column.is_filterable:
                if isinstance(column, Column):
                    column_options.append(column.get_options(account, obj))
                elif isinstance(column, AttributeColumnV2):
                    attribute_options_v2.extend(column.get_options(account, obj))

        return column_options, attribute_options_v2
