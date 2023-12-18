import time
from datetime import timezone, timedelta

from django.db import models
from django.db.models import Q, F, Avg, FloatField
from django.db.models.functions import Cast
from django.utils.functional import cached_property
from google.protobuf.struct_pb2 import Struct
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.wrappers_pb2 import UInt64Value, BoolValue, DoubleValue, StringValue, Int64Value

from accounts.models import Account
from protos.event.alert_pb2 import AlertDetail as AlertDetailProto, AlertStats, AlertMonitorTransaction, \
    DelayedMonitorTransactionStats, AlertSummary as AlertSummaryProto, AlertEntityInstance
from protos.event.base_pb2 import EventKey as EventKeyProto, EventType as EventTypeProto, Event as EventProto, \
    EventTypePartial as EventTypePartialProto, EventTypeSummary, EventTypeStats, EventTypeDefinition, TimeRange
from protos.event.entity_pb2 import EntityPartial, EntityStats, EntitySummary, Entity as EntityProto, EntityDetail, \
    EntityEventKeyMapping as EntityEventKeyMappingProto, EntityInstancePartial, EntityInstanceStats, \
    EntityInstanceSummary, EntityInstanceDetail, EntityInstance as EntityInstanceProto, EntityTriggerDefinition, \
    EntityTrigger as EntityTriggerProto
from protos.event.literal_pb2 import Literal, LiteralType
from protos.event.monitor_pb2 import MonitorTransaction as MonitorTransactionProto, Monitor as MonitorProto, \
    MonitorPartial as MonitorPartialProto, MonitorDefinition, MonitorStats, MonitorEventTypeDetails, \
    MonitorTransactionStats as MonitorTransactionStatsProto, MonitorTransactionDetails
from protos.event.notification_pb2 import NotificationConfig, SlackConfiguration, EmailConfiguration
from protos.event.panel_pb2 import PanelV1
from protos.event.query_base_pb2 import Op, Filter
from protos.event.schema_pb2 import IngestionEvent
from protos.event.trigger_pb2 import TriggerPriority, Trigger as TriggerProto, TriggerDefinition, TriggerStats, \
    MissingEventTrigger, DelayedEventTrigger, TriggerSummary, BasicTriggerFilter
from prototype.aggregates import Percentile
from prototype.fields import ChoiceArrayField
from prototype.utils.queryset import filter_time_range
from utils.model_utils import generate_choices
from utils.proto_utils import dict_to_proto

TRANSACTIONAL_KEY_TYPES = {EventKeyProto.KeyType.STRING, EventKeyProto.KeyType.LONG, EventKeyProto.KeyType.DOUBLE}
FILTERABLE_KEY_TYPES = {EventKeyProto.KeyType.STRING, EventKeyProto.KeyType.LONG, EventKeyProto.KeyType.DOUBLE,
                        EventKeyProto.KeyType.BOOLEAN}


def is_transactional_key_type(event_key_type):
    return event_key_type in TRANSACTIONAL_KEY_TYPES


def is_filterable_key_type(event_key_type):
    return event_key_type in FILTERABLE_KEY_TYPES


def get_literal_for_event_key_type(event_key_type, value):
    if event_key_type == EventKeyProto.KeyType.LONG:
        return Literal(literal_type=LiteralType.LONG, long=Int64Value(value=value))
    elif event_key_type == EventKeyProto.KeyType.DOUBLE:
        return Literal(literal_type=LiteralType.DOUBLE, double=DoubleValue(value=value))
    elif event_key_type == EventKeyProto.KeyType.STRING:
        return Literal(literal_type=LiteralType.STRING, string=StringValue(value=value))
    elif event_key_type == EventKeyProto.KeyType.BOOLEAN:
        return Literal(literal_type=LiteralType.BOOLEAN, boolean=BoolValue(value=value))
    else:
        raise ValueError(f'Unknown event key type {event_key_type}')


def get_literal_array_for_event_key_type(event_key_type, value):
    if event_key_type == EventKeyProto.KeyType.LONG:
        return Literal(literal_type=LiteralType.LONG_ARRAY, long_array=value)
    elif event_key_type == EventKeyProto.KeyType.STRING:
        return Literal(literal_type=LiteralType.STRING_ARRAY, string_array=value)
    else:
        raise ValueError(f'Unknown event key type {event_key_type}')


def get_basic_monitor_trigger_filter_keys(scope, event_filters):
    result: [BasicTriggerFilter] = []
    event_type_id = event_filters.get('event__event_type_id', None)
    event_keys = scope.eventkey_set.filter(event_type_id=event_type_id).values('id', 'name', 'type')
    for k, v in event_filters.items():
        if k == 'event__event_type_id':
            continue

        filter_tokens = k.split('__')
        key_name = filter_tokens[2]

        suffix_op = None
        if len(filter_tokens) > 3:
            suffix_op = k.split('__')[3]

        for key in event_keys:
            if key_name == key['name']:
                if not suffix_op:
                    result.append(BasicTriggerFilter(event_key_id=key['id'], op=Op.EQ,
                                                     literal=get_literal_for_event_key_type(key['type'], v)))
                if suffix_op == 'in':
                    result.append(BasicTriggerFilter(event_key_id=key['id'], op=Op.IN,
                                                     literal=get_literal_array_for_event_key_type(key['type'], v)))
    return result


class EventType(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    event_sources = ChoiceArrayField(
        base_field=models.IntegerField(choices=generate_choices(EventProto.EventSource), null=True, blank=True),
        default=list, coerce=int
    )

    class Meta:
        unique_together = [['account', 'name']]

    def __str__(self):
        return f'{self.account_id}:{self.name}'

    @property
    def keys(self):
        return [key.proto_partial for key in self.eventkey_set.all()]

    @property
    def proto(self):
        return EventTypeProto(id=self.id, name=str(self.name), keys=self.keys, event_sources=list(self.event_sources))

    @property
    def proto_partial(self):
        return EventTypePartialProto(id=self.id, name=str(self.name))

    @staticmethod
    def proto_partial_from_sql(e_type_id, e_type_name):
        return EventTypePartialProto(id=e_type_id, name=e_type_name)

    def definition(self, tr: TimeRange = TimeRange()) -> EventTypeSummary:
        return EventTypeDefinition(event_type=self.proto)

    def summary(self, tr: TimeRange = TimeRange()) -> EventTypeSummary:
        return EventTypeSummary(event_type=self.proto_partial, stats=self.stats(tr))

    def monitor_and_keys_summary(self):
        return self.proto_partial, self.monitor_and_keys_stats()

    def stats(self, tr: TimeRange = TimeRange()):
        event_set = self.event_set
        if tr:
            event_set = filter_time_range(event_set, tr, 'created_at')

        event_keys = self.eventkey_set.values("id")
        keys = [k["id"] for k in event_keys]
        monitor_count = self.account.monitor_set.filter(
            Q(primary_key_id__in=event_keys) | Q(secondary_key_id__in=event_keys)).count()

        return EventTypeStats(keys_count=UInt64Value(value=len(keys)), event_count=UInt64Value(value=event_set.count()),
                              monitor_count=UInt64Value(value=monitor_count))

    def monitor_and_keys_stats(self):
        event_keys = self.eventkey_set.values("id")
        keys = [k["id"] for k in event_keys]
        monitor_count = self.account.monitor_set.filter(
            Q(primary_key_id__in=event_keys) | Q(secondary_key_id__in=event_keys)).count()

        return {'keys_count': len(keys), 'event_count': 0, 'monitor_count': monitor_count}


class EventKey(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, db_index=True)
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    type = models.IntegerField(null=True, blank=True, choices=generate_choices(EventKeyProto.KeyType),
                               default=EventKeyProto.KeyType.UNKNOWN, db_index=True)

    # type, scope pending

    class Meta:
        unique_together = [['account', 'event_type', 'name']]

    def __str__(self):
        return f'{self.event_type}:{self.name}'

    @property
    def proto_partial(self):
        return EventKeyProto(id=self.id, key=str(self.name), key_type=self.type)

    @property
    def proto(self):
        return EventKeyProto(id=self.id, key=str(self.name), key_type=self.type,
                             event_type=self.event_type.proto_partial)

    @property
    def proto_event_type_partial(self) -> EventTypePartialProto:
        return self.event_type.proto_partial


class Event(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, db_index=True)
    event = models.JSONField()
    processed_kvs = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    timestamp = models.DateTimeField(db_index=True)
    is_generated = models.BooleanField(default=False, null=True, blank=True)
    event_source = models.IntegerField(null=True, blank=True, choices=generate_choices(EventProto.EventSource),
                                       default=EventProto.EventSource.UNKNOWN, db_index=True)

    def __str__(self):
        return f'{self.event_type_id}:{self.id}'

    @cached_property
    def proto(self):
        ingested_event: IngestionEvent = dict_to_proto(self.event, IngestionEvent)
        proto = EventProto(
            id=self.id, event_type=self.event_type.proto_partial, kvs=ingested_event.kvs,
            timestamp=int(self.timestamp.replace(tzinfo=timezone.utc).timestamp()),
            event_source=self.event_source
        )
        return proto


class Monitor(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, db_index=True)
    primary_key = models.ForeignKey(EventKey, on_delete=models.CASCADE, db_index=True, related_name='primary_key')
    secondary_key = models.ForeignKey(EventKey, on_delete=models.CASCADE, db_index=True, related_name='secondary_key')
    is_active = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_generated = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        unique_together = [['account', 'name']]

    def __str__(self):
        return f'{self.account_id}:{self.name}'

    @property
    def proto_partial(self):
        return MonitorPartialProto(id=self.id, name=str(self.name))

    @cached_property
    def proto(self):
        return MonitorProto(id=self.id, name=str(self.name), primary_event_key=self.primary_key.proto,
                            secondary_event_key=self.secondary_key.proto, is_active=BoolValue(value=self.is_active))

    @property
    def proto_monitor_event_type_detail(self) -> MonitorEventTypeDetails:
        return MonitorEventTypeDetails(monitor=self.proto_partial,
                                       primary_event_type=self.primary_key.proto_event_type_partial,
                                       secondary_event_type=self.secondary_key.proto_event_type_partial)

    def definition(self, tr: TimeRange = TimeRange()):
        return MonitorDefinition(monitor=self.proto, stats=self.stats(tr))

    def stats(self, tr: TimeRange = TimeRange()):
        monitor_transactions = self.monitortransaction_set
        if tr:
            monitor_transactions = filter_time_range(monitor_transactions, tr, 'created_at')
        monitor_transactions_finished = monitor_transactions.filter(
            type=MonitorTransactionProto.MonitorTransactionStatus.SECONDARY_RECEIVED
        )

        monitor_transactions_aggregates = monitor_transactions_finished.annotate(
            transaction_time=(Cast(F('monitortransactionstats__stats__transaction_time'), FloatField()))
        ).aggregate(
            p95=Percentile('transaction_time', percentile=0.95),
            p99=Percentile('transaction_time', percentile=0.99),
            avg_delay=Avg(F('transaction_time'))
        )

        avg_delay = monitor_transactions_aggregates.get('avg_delay')
        if not avg_delay:
            avg_delay = 0

        p95 = monitor_transactions_aggregates.get('p95', timedelta(seconds=0))
        if not p95:
            p95 = 0
        p99 = monitor_transactions_aggregates.get('p99', timedelta(seconds=0))
        if not p99:
            p99 = 0

        return MonitorStats(
            transaction_count=UInt64Value(value=monitor_transactions.count()),
            finished_transaction_count=UInt64Value(value=monitor_transactions_finished.count()),
            transaction_avg_delay=DoubleValue(value=round(avg_delay, 3)),
            percentiles={'p95': round(p95, 3), 'p99': round(p99, 3)}
        )


class Trigger(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, db_index=True)
    monitor = models.ForeignKey(Monitor, null=True, blank=True, on_delete=models.CASCADE, db_index=True)
    type = models.IntegerField(choices=generate_choices(TriggerDefinition.Type), db_index=True)
    config = models.JSONField()
    generated_config = models.JSONField(null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True, choices=generate_choices(TriggerPriority),
                                   default=TriggerPriority.TP_4, db_index=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True, db_index=True)

    class Meta:
        unique_together = [['account', 'name']]

    def __str__(self):
        return f'{self.account}:{self.name}'

    @property
    def proto(self, definition=True, trigger_stats=False) -> TriggerProto:
        return TriggerProto(id=self.id, name=self.name, priority=self.priority,
                            monitor=self.monitor.proto if self.monitor else MonitorProto(),
                            definition=self.trigger_definition if definition else TriggerDefinition(),
                            stats=self.trigger_stats if trigger_stats else TriggerStats(),
                            is_active=BoolValue(value=self.is_active))

    @property
    def proto_summary(self) -> TriggerSummary:
        return TriggerSummary(id=self.id, name=self.name,
                              type=self.type,
                              monitor_details=self.monitor.proto_monitor_event_type_detail)

    @cached_property
    def trigger_definition(self) -> TriggerDefinition:
        basic_primary_monitor_trigger_filters = get_basic_monitor_trigger_filter_keys(self.account,
                                                                                      self.generated_config.get(
                                                                                          'primary_event_filters', {}))
        basic_secondary_monitor_trigger_filters = get_basic_monitor_trigger_filter_keys(self.account,
                                                                                        self.generated_config.get(
                                                                                            'secondary_event_filters',
                                                                                            {}))

        if self.type == TriggerDefinition.Type.MISSING_EVENT:
            return TriggerDefinition(type=self.type,
                                     missing_event_trigger=dict_to_proto(self.config, MissingEventTrigger),
                                     primary_event_filters=basic_primary_monitor_trigger_filters,
                                     secondary_event_filters=basic_secondary_monitor_trigger_filters)
        elif self.type == TriggerDefinition.Type.DELAYED_EVENT:
            return TriggerDefinition(type=self.type,
                                     delayed_event_trigger=dict_to_proto(self.config, DelayedEventTrigger),
                                     primary_event_filters=basic_primary_monitor_trigger_filters,
                                     secondary_event_filters=basic_secondary_monitor_trigger_filters)

    @cached_property
    def trigger_stats(self) -> TriggerStats:
        last_triggered_at = None
        if self.last_triggered_at:
            last_triggered_at = Timestamp()
            last_triggered_at.FromDatetime(self.last_triggered_at)

        ts = TriggerStats(
            last_triggered_at=last_triggered_at,
            alert_count=UInt64Value(value=self.alert_count),
        )
        return ts

    @cached_property
    def definition(self) -> TriggerDefinition:
        return dict_to_proto(self.trigger_rule, TriggerDefinition)


class Entity(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, db_index=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    event_key = models.ManyToManyField(
        EventKey,
        through='EntityEventKeyMapping',
        related_name='entity_event_keys'
    )

    entity_monitors = models.ManyToManyField(
        Monitor,
        through='EntityMonitorMapping',
        related_name='entity_monitors'
    )

    type = models.IntegerField(null=True, blank=True, choices=generate_choices(EntityProto.Type),
                               default=EntityProto.Type.DEFAULT, db_index=True)
    is_generated = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        unique_together = ('account', 'name', 'type')

    def __str__(self):
        return f'{self.name}'

    @property
    def proto_partial(self):
        return EntityPartial(id=UInt64Value(value=self.id), name=StringValue(value=self.name))

    @property
    def proto(self) -> EntityProto:
        #     TODO(mohit.agarwal) need to add created_at and updated at fields here
        return EntityProto(
            id=UInt64Value(value=self.id),
            name=StringValue(value=str(self.name)),
            is_active=BoolValue(value=bool(self.is_active)),
        )

    @property
    def stats(self) -> EntityStats:
        return EntityStats(
            new_instance_count=UInt64Value(value=getattr(self, 'new_instance_count', 0)),
            active_instance_count=UInt64Value(value=getattr(self, 'active_instance_count', 0)),
            event_count=UInt64Value(value=getattr(self, 'event_count', 0)),
            transaction_count=UInt64Value(value=getattr(self, 'transaction_count', 0)),
        )

    @property
    def summary(self) -> EntitySummary:
        return EntitySummary(
            entity=self.proto,
            stats=None
        )

    @property
    def detail(self) -> EntityDetail:
        return EntityDetail(
            entity=self.proto,
            stats=self.stats,
            entity_event_key_mappings=[ekm.proto for ekm in self.entityeventkeymapping_set.all()],
        )

    @property
    def detail_without_stats(self) -> EntityDetail:
        return EntityDetail(
            entity=self.proto,
            entity_event_key_mappings=[ekm.proto for ekm in self.entityeventkeymapping_set.all()],
        )


class EntityTrigger(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, db_index=True)
    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.CASCADE, db_index=True)
    type = models.IntegerField(choices=generate_choices(EntityTriggerDefinition.TriggerType), db_index=True)
    rule_type = models.IntegerField(choices=generate_choices(EntityTriggerDefinition.EntityTriggerRuleType),
                                    db_index=True)
    config = models.JSONField()
    generated_config = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True, db_index=True)

    def __str__(self):
        return f'{self.account}:{self.name}'

    @property
    def proto(self) -> EntityTriggerProto:
        return EntityTriggerProto(id=self.id, entity_id=self.entity.id, name=self.name,
                                  is_active=BoolValue(value=self.is_active), entity_name=self.entity.name,
                                  definition=EntityTriggerDefinition(type=self.type,
                                                                     trigger_rule_config=self.trigger_rule_config,
                                                                     rule_type=self.rule_type),
                                  filter=dict_to_proto(self.generated_config, Filter))

    @cached_property
    def trigger_rule_config(self) -> EntityTriggerDefinition.TriggerRuleConfig:
        return EntityTriggerDefinition.TriggerRuleConfig(event_id=int(self.config.get('event_id', -1)),
                                                         event_name=self.config.get('event_name', ''),
                                                         time_interval=int(self.config.get('time_interval', 0)),
                                                         threshold_count=int(self.config.get('threshold_count', 0)))


class EntityEventKeyMapping(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    event_key = models.ForeignKey(EventKey, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, null=True, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['account', 'entity', 'event_key']]

    @property
    def proto(self):
        return EntityEventKeyMappingProto(
            id=UInt64Value(value=self.id),
            event_key=self.event_key.proto_partial,
            is_active=BoolValue(value=bool(self.is_active)),
        )


class Alert(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    trigger = models.ForeignKey(Trigger, on_delete=models.CASCADE, db_index=True, null=True)
    entity_trigger = models.ForeignKey(EntityTrigger, on_delete=models.CASCADE, db_index=True, null=True)
    triggered_at = models.DateTimeField(auto_now_add=True, db_index=True)
    stats = models.JSONField(null=True)

    def __str__(self):
        if self.trigger:
            return f'{self.trigger}:{self.triggered_at}'
        else:
            return f'{self.entity_trigger}:{self.triggered_at}'

    @cached_property
    def triggered_at_timestamp(self):
        timestamp = Timestamp()
        timestamp.FromDatetime(self.triggered_at)
        return timestamp

    @property
    def proto_details(self) -> AlertDetailProto:
        if self.trigger:
            return AlertDetailProto(id=self.id, trigger=self.trigger.proto,
                                    triggered_at=self.triggered_at_timestamp, stats=self.alert_stats)
        elif self.entity_trigger:
            return AlertDetailProto(id=self.id, entity_trigger=self.entity_trigger.proto,
                                    triggered_at=self.triggered_at_timestamp, stats=self.alert_stats)
        else:
            return AlertDetailProto(id=self.id)

    @property
    def proto_summary(self) -> AlertSummaryProto:
        if self.trigger:
            return AlertSummaryProto(id=self.id, trigger=self.trigger.proto_summary,
                                     triggered_at=int(self.triggered_at.replace(tzinfo=timezone.utc).timestamp()))
        elif self.entity_trigger:
            return AlertSummaryProto(id=self.id, entity_trigger=self.entity_trigger.proto,
                                     triggered_at=int(self.triggered_at.replace(tzinfo=timezone.utc).timestamp()))
        else:
            return AlertSummaryProto(id=self.id)

    @cached_property
    def alert_stats(self) -> AlertStats:
        if self.stats:
            return dict_to_proto(self.stats, AlertStats)
        return AlertStats()


class EntityInstance(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    instance = models.TextField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    alert = models.ManyToManyField(
        Alert,
        through='AlertEntityInstanceMapping',
        related_name='entity_alerts'
    )

    class Meta:
        unique_together = [['account', 'entity', 'instance']]

    @property
    def proto_partial(self) -> EntityInstancePartial:
        return EntityInstancePartial(
            id=UInt64Value(value=self.id),
            instance=StringValue(value=self.instance),
        )

    @property
    def proto(self) -> EntityInstanceProto:
        return EntityInstanceProto(
            id=UInt64Value(value=self.id),
            entity=self.entity.proto_partial,
            instance=StringValue(value=self.instance),
        )

    @property
    def stats(self) -> EntityInstanceStats:
        alert_id_trigger_name_mapping = AlertEntityInstanceMapping.objects.filter(
            entity_instance=self).values('alert_id', 'alert__entity_trigger__name')
        return EntityInstanceStats(
            event_count=UInt64Value(value=getattr(self, 'event_count', 0)),
            transaction_count=UInt64Value(value=getattr(self, 'transaction_count', 0)),
            alerts=list(EntityInstanceStats.EntityAlert(alert_id=x['alert_id'],
                                                        entity_trigger_name=x['alert__entity_trigger__name']) for x in
                        list(alert_id_trigger_name_mapping))
        )

    @property
    def summary(self) -> EntityInstanceSummary:
        return EntityInstanceSummary(
            entity_instance=self.proto_partial,
            stats=self.stats,
        )

    @property
    def detail(self) -> EntityInstanceDetail:
        return EntityInstanceDetail(
            entity_instance=self.proto,
            stats=self.stats,
        )


class AlertEntityInstanceMapping(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, db_index=True)
    entity_instance = models.ForeignKey(EntityInstance, on_delete=models.CASCADE, db_index=True)
    type = models.IntegerField(null=True, blank=True,
                               choices=generate_choices(AlertEntityInstance.Type),
                               default=AlertEntityInstance.Type.UNKNOWN,
                               db_index=True)
    stats = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = [['account', 'alert', 'entity_instance']]

    @property
    def proto(self) -> AlertEntityInstance:
        if self.type == AlertEntityInstance.Type.PER_EVENT:
            return AlertEntityInstance(type=self.type,
                                       alert_id=self.alert_id,
                                       entity_instance=self.entity_instance.proto)
        elif self.type == AlertEntityInstance.Type.AGGREGATED_EVENTS:
            return AlertEntityInstance(type=self.type,
                                       alert_id=self.alert_id,
                                       entity_instance=self.entity_instance.proto)

    @property
    def miniproto(self) -> AlertEntityInstance:
        if self.type == AlertEntityInstance.Type.PER_EVENT:
            return AlertEntityInstance(type=self.type,
                                       alert_id=self.alert_id,
                                       trigger_name=self.alert.entity_trigger.name)
        return None


class EntityInstanceEventMapping(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    entity_instance = models.ForeignKey(EntityInstance, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    event_key = models.ForeignKey(EventKey, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    instance = models.TextField(db_index=True)
    event_processed_kvs = models.JSONField(null=True, blank=True)
    event_timestamp = models.DateTimeField(null=True, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = [['account', 'entity_instance', 'event']]


class MonitorTransaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE, db_index=True)
    transaction = models.TextField(db_index=True)
    type = models.IntegerField(null=True, blank=True,
                               choices=generate_choices(MonitorTransactionProto.MonitorTransactionStatus),
                               default=MonitorTransactionProto.MonitorTransactionStatus.UNKNOWN,
                               db_index=True)

    alert = models.ManyToManyField(
        Alert,
        through='AlertMonitorTransactionMapping',
        related_name='alerts'
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True, db_index=True)

    class Meta:
        unique_together = [['account', 'monitor', 'transaction']]

    @property
    def proto(self):
        return MonitorTransactionProto(
            id=self.id, transaction=str(self.transaction),
            monitor=self.monitor.proto_partial,
            created_at=int(self.created_at.replace(tzinfo=timezone.utc).timestamp()),
            status=self.type,
            has_alerts=BoolValue(value=getattr(self, 'has_alerts', False)),
            transaction_age=DoubleValue(
                value=round(time.time() - self.created_at.replace(tzinfo=timezone.utc).timestamp(), 3))
        )

    @property
    def proto_for_export(self):
        return MonitorTransactionProto(
            id=self.id, transaction=str(self.transaction),
            monitor=self.monitor.proto_partial,
            created_at=int(self.created_at.replace(tzinfo=timezone.utc).timestamp()),
            status=self.type,
            has_alerts=BoolValue(value=getattr(self, 'has_alerts', False)),
            transaction_time=DoubleValue(value=self.transaction_time),
            transaction_age=DoubleValue(
                value=round(time.time() - self.created_at.replace(tzinfo=timezone.utc).timestamp(), 3))
        )

    @property
    def details_proto(self):
        if self.stats:
            return MonitorTransactionDetails(
                monitor_transaction=self.proto,
                stats=dict_to_proto(self.stats, MonitorTransactionStatsProto)
            )
        else:
            return MonitorTransactionDetails(
                monitor_transaction=self.proto,
                stats=MonitorTransactionStatsProto()
            )


class MonitorTransactionStats(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    monitor_transaction = models.ForeignKey(MonitorTransaction, on_delete=models.CASCADE, db_index=True)
    stats = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True, db_index=True)

    class Meta:
        unique_together = [['account', 'monitor_transaction']]

    @property
    def proto(self):
        return MonitorTransactionDetails(
            monitor_transaction=self.monitor_transaction.proto,
            stats=dict_to_proto(self.stats, MonitorTransactionStatsProto)
        )


class MonitorTransactionEventMapping(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    monitor_transaction = models.ForeignKey(MonitorTransaction, on_delete=models.CASCADE, db_index=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, db_index=True)
    type = models.IntegerField(null=True, blank=True,
                               choices=generate_choices(MonitorTransactionProto.MonitorTransactionEventType),
                               default=MonitorTransactionProto.MonitorTransactionEventType.UNKNOWN_MT_ET,
                               db_index=True)
    event_timestamp = models.DateTimeField(null=True, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = [['account', 'event', 'monitor_transaction']]


class AlertMonitorTransactionMapping(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, db_index=True)
    monitor_transaction = models.ForeignKey(MonitorTransaction, on_delete=models.CASCADE, db_index=True)
    type = models.IntegerField(null=True, blank=True,
                               choices=generate_choices(AlertMonitorTransaction.Type),
                               default=AlertMonitorTransaction.Type.UNKNOWN,
                               db_index=True)
    stats = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = [['account', 'alert', 'monitor_transaction']]

    @property
    def proto(self) -> AlertMonitorTransaction:
        if self.type == AlertMonitorTransaction.Type.MISSED_TRANSACTION:
            return AlertMonitorTransaction(type=self.type,
                                           alert_id=self.alert_id,
                                           monitor_transaction=self.monitor_transaction.proto)
        elif self.type == AlertMonitorTransaction.Type.DELAYED_TRANSACTION:
            return AlertMonitorTransaction(type=self.type,
                                           alert_id=self.alert_id,
                                           monitor_transaction=self.monitor_transaction.proto,
                                           delayed_monitor_transaction_stats=dict_to_proto(self.stats,
                                                                                           DelayedMonitorTransactionStats))

    @property
    def miniproto(self) -> AlertMonitorTransaction:
        if self.type == AlertMonitorTransaction.Type.MISSED_TRANSACTION:
            return AlertMonitorTransaction(type=self.type,
                                           alert_id=self.alert_id,
                                           trigger_name=self.alert.trigger.name)
        elif self.type == AlertMonitorTransaction.Type.DELAYED_TRANSACTION:
            return AlertMonitorTransaction(type=self.type,
                                           alert_id=self.alert_id,
                                           trigger_name=self.alert.trigger.name)


class Notification(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    channel = models.IntegerField(choices=generate_choices(NotificationConfig.Channel), db_index=True)
    config = models.JSONField(null=True, blank=True)
    trigger = models.ManyToManyField(
        Trigger,
        through='TriggerNotificationConfigMapping',
        related_name='triggers'
    )
    entity_trigger = models.ManyToManyField(
        EntityTrigger,
        through='EntityTriggerNotificationConfigMapping',
        related_name='entity_triggers'
    )

    class Meta:
        unique_together = [['account', 'config']]

    def __str__(self):
        return f'{self.account}:{self.config}'

    @property
    def proto(self) -> NotificationConfig:
        if self.channel == NotificationConfig.Channel.SLACK:
            return NotificationConfig(channel=self.channel,
                                      slack_configuration=dict_to_proto(self.config, SlackConfiguration))
        elif self.channel == NotificationConfig.Channel.EMAIL:
            return NotificationConfig(channel=self.channel,
                                      email_configuration=dict_to_proto(self.config, EmailConfiguration))


class TriggerNotificationConfigMapping(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    trigger = models.ForeignKey(Trigger, on_delete=models.CASCADE, db_index=True)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = [['account', 'trigger', 'notification']]


class EntityTriggerNotificationConfigMapping(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    entity_trigger = models.ForeignKey(EntityTrigger, on_delete=models.CASCADE, db_index=True)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = [['account', 'entity_trigger', 'notification']]


class Panel(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.TextField(null=True, blank=True, default="")
    config = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['account', 'name']]

    def __str__(self):
        return f'{self.account}:{self.name}'

    @property
    def proto(self):
        c: Struct = Struct()
        c.update(self.config)
        return PanelV1(id=self.id, name=self.name, config=c)


class EntityInstanceMonitorTransactionMapping(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    entity_instance = models.ForeignKey(EntityInstance, on_delete=models.CASCADE)
    monitor_transaction = models.ForeignKey(MonitorTransaction, on_delete=models.CASCADE)

    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    instance = models.TextField(db_index=True)
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE)
    transaction = models.TextField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = [['account', 'entity_instance', 'monitor_transaction']]


class EntityMonitorMapping(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    is_generated = models.BooleanField(default=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = [['account', 'entity', 'monitor']]
