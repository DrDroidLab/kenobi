import datetime
import statistics
from typing import Dict, List

from django.db.models import ExpressionWrapper, F, fields, Subquery, OuterRef
from google.protobuf.wrappers_pb2 import UInt32Value, DoubleValue, UInt64Value

from accounts.models import Account
from event.models import MonitorTransaction, Alert, AlertMonitorTransactionMapping, MonitorTransactionEventMapping
from protos.event.alert_pb2 import AlertStats, AlertMonitorTransaction, DelayedMonitorTransactionStats
from protos.event.monitor_pb2 import MonitorTransaction as MonitorTransactionProto
from protos.event.options_pb2 import TriggerOption
from protos.event.query_base_pb2 import OpDescription, Op
from protos.event.trigger_pb2 import TriggerDefinition, DelayedEventTrigger, MissingEventTrigger, \
    BasicTriggerFilterOptions, DelayedEventTriggerOptions
from utils.proto_utils import proto_to_dict, dict_to_proto

_BASIC_TRIGGER_FILTER_OP_DESCRIPTIONS = [
    OpDescription(op=Op.EQ, label='=', is_unary=False)
]


def process_missing_event_monitor_transactions(scope, trigger, time_upper_bound, time_lower_bound,
                                               expected_transaction_time):
    delay_duration = ExpressionWrapper(F('secondary_event_timestamp') - F('primary_event_timestamp'),
                                       output_field=fields.DurationField())

    primary_filter = trigger["generated_config"].get('primary_event_filters', {})
    secondary_filter = trigger["generated_config"].get('secondary_event_filters', {})

    if not primary_filter or not secondary_filter:
        return {"monitor_transactions_qs": [],
                "missing_event_monitor_transactions_qs": [],
                "delayed_event_monitor_transactions_qs": []}

    monitor_transactions: [MonitorTransaction] = scope.monitortransaction_set.using('replica1').filter(
        monitor_id=trigger['monitor_id']).filter(created_at__range=[time_upper_bound, time_lower_bound]).annotate(
        primary_event_timestamp=Subquery(
            MonitorTransactionEventMapping.objects.using('replica1').filter(monitor_transaction=OuterRef("pk")).filter(
                **primary_filter).values('event__timestamp').order_by('event__timestamp')[:1]
        )
    ).filter(primary_event_timestamp__isnull=False)

    missing_event_monitor_transactions: [MonitorTransaction] = monitor_transactions.filter(
        type=MonitorTransactionProto.MonitorTransactionStatus.PRIMARY_RECEIVED)

    # handle cases where secondary event is received but not satisfying the secondary filters
    missing_filtered_event_monitor_transactions = []
    if secondary_filter:
        missing_filtered_event_monitor_transactions: [MonitorTransaction] = monitor_transactions.annotate(
            secondary_event_timestamp=Subquery(
                MonitorTransactionEventMapping.objects.using('replica1').filter(monitor_transaction=OuterRef("pk")).filter(
                    **secondary_filter).values('event__timestamp')[:1])
        ).filter(secondary_event_timestamp__isnull=True).filter(
            type=MonitorTransactionProto.MonitorTransactionStatus.SECONDARY_RECEIVED)

    delayed_event_monitor_transactions: [MonitorTransaction] = monitor_transactions.annotate(
        secondary_event_timestamp=Subquery(
            MonitorTransactionEventMapping.objects.using('replica1').filter(monitor_transaction=OuterRef("pk")).filter(
                **secondary_filter).values('event__timestamp')[:1])
    ).filter(secondary_event_timestamp__isnull=False).filter(
        type=MonitorTransactionProto.MonitorTransactionStatus.SECONDARY_RECEIVED).annotate(
        duration=delay_duration).filter(
        duration__gt=datetime.timedelta(seconds=expected_transaction_time))

    return {"monitor_transactions_qs": monitor_transactions,
            "missing_event_monitor_transactions_qs": missing_event_monitor_transactions,
            "missing_filtered_event_monitor_transactions_qs": missing_filtered_event_monitor_transactions,
            "delayed_event_monitor_transactions_qs": delayed_event_monitor_transactions}


def process_delayed_event_monitor_transactions(scope, trigger, time_upper_bound, time_lower_bound,
                                               expected_transaction_time,
                                               trigger_config_type: DelayedEventTrigger.Type):
    delay_duration = ExpressionWrapper(F('secondary_event_timestamp') - F('primary_event_timestamp'),
                                       output_field=fields.DurationField())

    primary_filter = trigger["generated_config"].get('primary_event_filters', {})
    secondary_filter = trigger["generated_config"].get('secondary_event_filters', {})

    if not primary_filter or not secondary_filter:
        return {"monitor_transactions_qs": [],
                "missing_event_monitor_transactions_qs": [],
                "delayed_event_monitor_transactions_qs": []}

    monitor_transactions: [MonitorTransaction] = scope.monitortransaction_set.using('replica1').filter(
        monitor_id=trigger['monitor_id']).filter(created_at__range=[time_upper_bound, time_lower_bound]).annotate(
        primary_event_timestamp=Subquery(
            MonitorTransactionEventMapping.objects.using('replica1').filter(monitor_transaction=OuterRef("pk")).filter(
                **primary_filter).values('event__timestamp').order_by('event__timestamp')[:1]
        )
    ).filter(primary_event_timestamp__isnull=False)

    missing_event_monitor_transactions: [MonitorTransaction] = monitor_transactions.filter(
        type=MonitorTransactionProto.MonitorTransactionStatus.PRIMARY_RECEIVED)

    delayed_event_monitor_transactions: [MonitorTransaction] = monitor_transactions.annotate(
        secondary_event_timestamp=Subquery(
            MonitorTransactionEventMapping.objects.filter(monitor_transaction=OuterRef("pk")).filter(
                **secondary_filter).values('event__timestamp')[:1])
    ).filter(secondary_event_timestamp__isnull=False).filter(
        type=MonitorTransactionProto.MonitorTransactionStatus.SECONDARY_RECEIVED).annotate(
        duration=delay_duration).filter(
        duration__gt=datetime.timedelta(seconds=expected_transaction_time))

    if trigger_config_type == DelayedEventTrigger.Type.DELAYED_EVENTS:
        missing_event_monitor_transactions = []

        monitor_transactions: [MonitorTransaction] = scope.monitortransaction_set.using('replica1').filter(
            monitor_id=trigger['monitor_id']).filter(created_at__range=[time_upper_bound, time_lower_bound]).filter(
            type=MonitorTransactionProto.MonitorTransactionStatus.SECONDARY_RECEIVED).annotate(
            primary_event_timestamp=Subquery(
                MonitorTransactionEventMapping.objects.using('replica1').filter(monitor_transaction=OuterRef("pk")).filter(
                    **primary_filter).values('event__timestamp').order_by('event__timestamp')[:1]
            )
        ).filter(primary_event_timestamp__isnull=False)

    elif trigger_config_type == DelayedEventTrigger.Type.MISSING_EVENTS:
        delayed_event_monitor_transactions: [MonitorTransaction] = []

    return {"monitor_transactions_qs": monitor_transactions,
            "missing_event_monitor_transactions_qs": missing_event_monitor_transactions,
            "delayed_event_monitor_transactions_qs": delayed_event_monitor_transactions}


class TriggerProcessorException(ValueError):
    pass


class TriggerProcessor:

    @classmethod
    def get_default_config(cls) -> Dict:
        pass

    @classmethod
    def evaluate_triggers(cls, scope, trigger, time_lower_bound, time_upper_bound) -> [Alert]:
        pass

    @classmethod
    def get_default_trigger_options(cls, scope) -> TriggerOption:
        pass

    # TODO: add contextual trigger options


class MissingEventTriggerProcessor(TriggerProcessor):

    @classmethod
    def get_default_config(cls):
        return MissingEventTrigger(transaction_time_threshold=DoubleValue(value=10.0))

    @classmethod
    def evaluate_triggers(cls, scope, trigger, time_lower_bound, time_upper_bound) -> [Alert]:
        if type(scope) is not Account:
            raise ValueError(f'{scope} needs to be Account')

        generated_alerts: [Alert] = []
        expected_transaction_time_sec = trigger['config'].get("transaction_time_threshold")

        qs_set = process_missing_event_monitor_transactions(scope, trigger, time_upper_bound, time_lower_bound,
                                                            expected_transaction_time_sec)

        for mt in qs_set["missing_event_monitor_transactions_qs"]:
            alert_stats = AlertStats(total_transaction_count=UInt64Value(value=1),
                                     missed_transaction_count=UInt64Value(value=1))

            saved_alert = Alert.objects.create(account=scope, trigger_id=trigger['id'],
                                               stats=proto_to_dict(alert_stats))

            AlertMonitorTransactionMapping.objects.get_or_create(account=scope,
                                                                 alert=saved_alert,
                                                                 monitor_transaction=mt,
                                                                 type=AlertMonitorTransaction.Type.MISSED_TRANSACTION)
            generated_alerts.append(saved_alert)

        for mt in qs_set["missing_filtered_event_monitor_transactions_qs"]:
            alert_stats = AlertStats(total_transaction_count=UInt64Value(value=1),
                                     missed_transaction_count=UInt64Value(value=1))

            saved_alert = Alert.objects.create(account=scope, trigger_id=trigger['id'],
                                               stats=proto_to_dict(alert_stats))

            AlertMonitorTransactionMapping.objects.get_or_create(account=scope,
                                                                 alert=saved_alert,
                                                                 monitor_transaction=mt,
                                                                 type=AlertMonitorTransaction.Type.MISSED_TRANSACTION)
            generated_alerts.append(saved_alert)

        for mt in qs_set["delayed_event_monitor_transactions_qs"]:
            alert_stats = AlertStats(total_transaction_count=UInt64Value(value=1),
                                     delayed_transaction_count=UInt64Value(value=1),
                                     median_delay=DoubleValue(
                                         value=mt.duration.total_seconds()))

            saved_alert = Alert.objects.create(account=scope, trigger_id=trigger['id'],
                                               stats=proto_to_dict(alert_stats))
            amt_stats = DelayedMonitorTransactionStats(
                delay_duration=DoubleValue(value=mt.duration.total_seconds()))

            AlertMonitorTransactionMapping.objects.get_or_create(account=scope,
                                                                 alert=saved_alert,
                                                                 monitor_transaction=mt,
                                                                 type=AlertMonitorTransaction.Type.DELAYED_TRANSACTION,
                                                                 stats=proto_to_dict(amt_stats))
            generated_alerts.append(saved_alert)
        return generated_alerts

    @classmethod
    def get_default_trigger_options(cls, scope) -> TriggerOption:
        if type(scope) is not Account:
            raise ValueError(f'{scope} needs to be Account')

        default_config = cls.get_default_config()
        return TriggerOption(
            trigger_type=TriggerDefinition.Type.MISSING_EVENT,
            default_missing_event_trigger_config=default_config,
            basic_trigger_filter_options=BasicTriggerFilterOptions(
                op_description=_BASIC_TRIGGER_FILTER_OP_DESCRIPTIONS
            )
        )


class DelayedEventTriggerProcessor(TriggerProcessor):
    @classmethod
    def get_default_config(cls):

        delayed_event_trigger_types = []
        for k, _ in DelayedEventTrigger.Type.items():
            delayed_event_trigger_types.append(k)

        return DelayedEventTriggerOptions(transaction_time_threshold=DoubleValue(value=10.0),
                                          trigger_threshold=DoubleValue(value=10.0),
                                          resolution=UInt32Value(value=60),
                                          type=delayed_event_trigger_types)

    @classmethod
    def evaluate_triggers(cls, scope, trigger, time_lower_bound, time_upper_bound) -> [Alert]:
        if type(scope) is not Account:
            raise ValueError(f'{scope} needs to be Account')

        generated_alerts: [Alert] = []

        trigger_config = dict_to_proto(trigger["config"], DelayedEventTrigger)
        expected_transaction_time_sec = trigger_config.transaction_time_threshold.value
        trigger_threshold = trigger_config.trigger_threshold.value
        delayed_event_trigger_type = trigger_config.type

        qs_set = process_delayed_event_monitor_transactions(scope, trigger, time_upper_bound, time_lower_bound,
                                                            expected_transaction_time_sec,
                                                            delayed_event_trigger_type)

        total_transaction_count = len(qs_set["monitor_transactions_qs"])
        missing_event_transactions = qs_set["missing_event_monitor_transactions_qs"]
        delayed_event_transactions = qs_set["delayed_event_monitor_transactions_qs"]

        if total_transaction_count > 0 and (
                (len(delayed_event_transactions) + len(missing_event_transactions)) / total_transaction_count) \
                * 100 >= trigger_threshold:

            saved_alert = Alert.objects.create(account=scope, trigger_id=trigger['id'])

            for mt in qs_set["missing_event_monitor_transactions_qs"]:
                AlertMonitorTransactionMapping.objects.create(account=scope, alert=saved_alert,
                                                              monitor_transaction=mt,
                                                              type=AlertMonitorTransaction.Type.MISSED_TRANSACTION)

            delay_duration_list = []
            for mt in qs_set["delayed_event_monitor_transactions_qs"]:
                delay_duration = mt.duration.total_seconds()
                delay_duration_list.append(delay_duration)
                amt_stats = DelayedMonitorTransactionStats(delay_duration=DoubleValue(value=delay_duration))
                AlertMonitorTransactionMapping.objects.create(account=scope, alert=saved_alert,
                                                              monitor_transaction=mt,
                                                              type=AlertMonitorTransaction.Type.DELAYED_TRANSACTION,
                                                              stats=proto_to_dict(amt_stats))

            if len(delay_duration_list) > 0:
                stats = AlertStats(total_transaction_count=UInt64Value(value=total_transaction_count),
                                   missed_transaction_count=UInt64Value(value=len(missing_event_transactions)),
                                   delayed_transaction_count=UInt64Value(value=len(delayed_event_transactions)),
                                   median_delay=DoubleValue(value=statistics.median(delay_duration_list)))
            else:
                stats = AlertStats(total_transaction_count=UInt64Value(value=total_transaction_count),
                                   missed_transaction_count=UInt64Value(value=len(missing_event_transactions)),
                                   delayed_transaction_count=UInt64Value(value=len(delayed_event_transactions)))

            Alert.objects.update_or_create(id=saved_alert.id, defaults={'stats': proto_to_dict(stats)})

            generated_alerts.append(saved_alert)

        return generated_alerts

    @classmethod
    def get_default_trigger_options(cls, scope) -> TriggerOption:
        if type(scope) is not Account:
            raise ValueError(f'{scope} needs to be Account')

        default_config = cls.get_default_config()
        return TriggerOption(
            trigger_type=TriggerDefinition.Type.DELAYED_EVENT,
            default_delayed_event_trigger_config=default_config,
            basic_trigger_filter_options=BasicTriggerFilterOptions(
                op_description=_BASIC_TRIGGER_FILTER_OP_DESCRIPTIONS
            )
        )


missing_event_trigger_processor = MissingEventTriggerProcessor()
delayed_event_trigger_processor = DelayedEventTriggerProcessor()


class TriggerProcessorFacade:

    def __init__(self):
        self._map = {}

    def register(self, trigger_type: TriggerDefinition.Type, typed_trigger_processor: TriggerProcessor):
        self._map[trigger_type] = typed_trigger_processor

    def process_triggers(self, scope, trigger, time_lower_bound, time_upper_bound) -> [Alert]:
        return self._map[trigger["type"]].evaluate_triggers(scope, trigger, time_lower_bound, time_upper_bound)

    def get_default_triggers_options(self, scope, trigger_type: TriggerDefinition.Type = None) -> List:
        if trigger_type:
            return self._map[trigger_type].get_default_trigger_options(scope)
        else:
            trigger_options: [TriggerOption] = []
            for key, value in self._map.items():
                trigger_options.append(value.get_default_trigger_options(scope))
            return trigger_options


trigger_processor = TriggerProcessorFacade()
trigger_processor.register(TriggerDefinition.Type.MISSING_EVENT, MissingEventTriggerProcessor())
trigger_processor.register(TriggerDefinition.Type.DELAYED_EVENT, DelayedEventTriggerProcessor())


def process_trigger(scope, trigger, time_lower_bound, time_upper_bound) -> [Alert]:
    return trigger_processor.process_triggers(scope, trigger, time_lower_bound, time_upper_bound)


def get_default_trigger_options(scope, trigger_type: TriggerDefinition.Type = None):
    return trigger_processor.get_default_triggers_options(scope, trigger_type)
