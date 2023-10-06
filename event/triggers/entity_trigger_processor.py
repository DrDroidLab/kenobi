import datetime
import statistics
from typing import Dict, List

from django.db.models import ExpressionWrapper, F, fields, Subquery, OuterRef
from google.protobuf.wrappers_pb2 import UInt32Value, DoubleValue, UInt64Value

from accounts.models import Account
from event.models import MonitorTransaction, Alert, AlertMonitorTransactionMapping, MonitorTransactionEventMapping, \
    EntityInstanceEventMapping, Event, AlertEntityInstanceMapping
from event.triggers.trigger_processor import TriggerProcessor
from protos.event.alert_pb2 import AlertStats, AlertMonitorTransaction, DelayedMonitorTransactionStats, \
    AlertEntityInstance
from protos.event.entity_pb2 import EntityTriggerDefinition
from protos.event.monitor_pb2 import MonitorTransaction as MonitorTransactionProto
from protos.event.options_pb2 import TriggerOption
from protos.event.query_base_pb2 import OpDescription, Op, Filter
from protos.event.trigger_pb2 import TriggerDefinition, DelayedEventTrigger, MissingEventTrigger, \
    BasicTriggerFilterOptions, DelayedEventTriggerOptions
from utils.proto_utils import proto_to_dict, dict_to_proto

from event.engine.query_engine import global_event_search_engine

_BASIC_TRIGGER_FILTER_OP_DESCRIPTIONS = [
    OpDescription(op=Op.EQ, label='=', is_unary=False)
]


def process_last_event_entity_trigger(scope, entity_instance_mapping_list, config_event_id):
    alert_data = []
    for instance_mapping in entity_instance_mapping_list:
        event_name = instance_mapping.event_key.event_type.name
        event_key_name = instance_mapping.event_key.name
        entity_instance_id = instance_mapping.entity_instance_id
        later_event_mappings = (EntityInstanceEventMapping.objects.using('replica1').filter(account_id=scope.id,
                                                                            entity_instance_id=entity_instance_id,
                                                                            event_timestamp__gt=instance_mapping.event_timestamp)
                                .exclude(event_key__event_type_id=config_event_id))
        if not later_event_mappings or len(later_event_mappings) == 0:
            alert_data.append({"entity_instance_value": instance_mapping.entity_instance.instance, "entity_instance_id": instance_mapping.entity_instance.id, "event_key_name": event_key_name,
                               "event_timestamp": int(instance_mapping.event_timestamp.timestamp()), "event_name": event_name})
    return alert_data


def process_event_count_entity_trigger(scope, entity_instance_mapping_list, config_event_id, config_time_interval_sec, config_threshold_count):
    alert_data = []
    for instance_mapping in entity_instance_mapping_list:
        event_name = instance_mapping.event_key.event_type.name
        event_key_name = instance_mapping.event_key.name
        entity_instance_id = instance_mapping.entity_instance_id
        later_event_mappings = EntityInstanceEventMapping.objects.using('replica1').filter(account_id=scope.id,
                                                                            entity_instance_id=entity_instance_id,
                                                                            event_timestamp__lt=instance_mapping.event_timestamp,
                                                                          event_timestamp__gt=(instance_mapping.event_timestamp - datetime.timedelta(seconds=config_time_interval_sec)),
                                                                          event_key__event_type_id=config_event_id)
        if len(later_event_mappings) > config_threshold_count - 1:
            alert_data.append({"entity_instance_value": instance_mapping.entity_instance.instance, "entity_instance_id": instance_mapping.entity_instance.id, "event_key_name": event_key_name,
                               "event_timestamp": int(instance_mapping.event_timestamp.timestamp()), "event_name": event_name})
    return alert_data


def process_event_occurrence_entity_trigger(entity_instance_mapping_list):
    alert_data = []
    for instance_mapping in entity_instance_mapping_list:
        event_name = instance_mapping.event_key.event_type.name
        event_key_name = instance_mapping.event_key.name
        alert_data.append({"entity_instance_value": instance_mapping.entity_instance.instance, "entity_instance_id": instance_mapping.entity_instance.id, "event_key_name": event_key_name,
                               "event_timestamp": int(instance_mapping.event_timestamp.timestamp()), "event_name": event_name})
    return alert_data


class PerEventTriggerProcessor(TriggerProcessor):

    @classmethod
    def get_default_config(cls):
        return MissingEventTrigger(transaction_time_threshold=DoubleValue(value=10.0))

    @classmethod
    def evaluate_triggers(cls, scope, trigger, time_lower_bound, time_upper_bound) -> [Alert]:
        if type(scope) is not Account:
            raise ValueError(f'{scope} needs to be Account')

        generated_alerts: [Alert] = []
        trigger_id = trigger['id']
        trigger_name = trigger['name']
        entity_id = trigger['entity_id']
        config_time_interval_sec = int(trigger['config'].get('time_interval', 0))
        config_event_id = trigger['config'].get('event_id')
        config_threshold_count = int(trigger['config'].get('threshold_count', 0))
        trigger_rule_type = trigger['rule_type']
        filter_config = trigger['generated_config']

        if trigger_rule_type in [EntityTriggerDefinition.EntityTriggerRuleType.LAST_EVENT]:
            last_event_check_start_time = time_upper_bound
            last_event_check_end_time = time_lower_bound
            check_interval_entity_instance_mapping_list = EntityInstanceEventMapping.objects.using('replica1').filter(account_id=scope.id, entity_id=entity_id,
                                                                                                    event_key__event_type_id=config_event_id,
                                                                                                    event_timestamp__range=[
                                                                                                        last_event_check_start_time,
                                                                                                        last_event_check_end_time])
            filter_events = global_event_search_engine.process_query_with_filter(Event.objects.using('replica1').filter(account=scope, timestamp__range=[
                                                                                                        last_event_check_start_time,
                                                                                                        last_event_check_end_time]), dict_to_proto(filter_config, Filter))
            check_interval_entity_instance_mapping_list = check_interval_entity_instance_mapping_list.filter(event__in=filter_events)

            last_event_alerts = process_last_event_entity_trigger(scope, check_interval_entity_instance_mapping_list, config_event_id)
            for alert_data in last_event_alerts:
                saved_alert = Alert.objects.create(account=scope, entity_trigger_id=trigger_id, stats=alert_data)

                AlertEntityInstanceMapping.objects.get_or_create(account=scope,
                                                                     alert=saved_alert,
                                                                     entity_instance_id=alert_data.get('entity_instance_id'),
                                                                     type=AlertEntityInstance.Type.PER_EVENT)
                generated_alerts.append(saved_alert)

        if trigger_rule_type in [EntityTriggerDefinition.EntityTriggerRuleType.EVENT_COUNT]:
            last_event_check_start_time = time_upper_bound
            last_event_check_end_time = time_lower_bound
            check_interval_entity_instance_mapping_list = EntityInstanceEventMapping.objects.using('replica1').filter(account_id=scope.id,
                                                                                                    entity_id=entity_id,
                                                                                                    event_key__event_type_id=config_event_id,
                                                                                                    event_timestamp__range=[
                                                                                                        last_event_check_start_time,
                                                                                                        last_event_check_end_time])
            filter_events = global_event_search_engine.process_query_with_filter(
                Event.objects.using('replica1').filter(account=scope, timestamp__range=[
                            last_event_check_start_time,
                            last_event_check_end_time]), dict_to_proto(filter_config, Filter))
            check_interval_entity_instance_mapping_list = check_interval_entity_instance_mapping_list.filter(event__in=filter_events)
            event_count_alerts = process_event_count_entity_trigger(scope, check_interval_entity_instance_mapping_list, config_event_id, config_time_interval_sec, config_threshold_count)
            for alert_data in event_count_alerts:
                saved_alert = Alert.objects.create(account=scope, entity_trigger_id=trigger_id, stats=alert_data)

                AlertEntityInstanceMapping.objects.get_or_create(account=scope,
                                                                 alert=saved_alert,
                                                                 entity_instance_id=alert_data.get(
                                                                     'entity_instance_id'),
                                                                 type=AlertEntityInstance.Type.PER_EVENT)
                generated_alerts.append(saved_alert)

        if trigger_rule_type in [EntityTriggerDefinition.EntityTriggerRuleType.EVENT_OCCURS]:
            check_interval_entity_instance_mapping_list = EntityInstanceEventMapping.objects.using('replica1').filter(account_id=scope.id, entity_id=entity_id,
                                                                                                    event_key__event_type_id=config_event_id,
                                                                                                    event_timestamp__range=[
                                                                                                        time_upper_bound,
                                                                                                        time_lower_bound])
            filter_events = global_event_search_engine.process_query_with_filter(
                Event.objects.using('replica1').filter(account=scope, timestamp__range=[
                        time_upper_bound,
                        time_lower_bound]), dict_to_proto(filter_config, Filter))
            check_interval_entity_instance_mapping_list = check_interval_entity_instance_mapping_list.filter(event__in=filter_events)
            event_occurrence_alerts = process_event_occurrence_entity_trigger(check_interval_entity_instance_mapping_list)
            for alert_data in event_occurrence_alerts:
                saved_alert = Alert.objects.create(account=scope, entity_trigger_id=trigger_id, stats=alert_data)

                AlertEntityInstanceMapping.objects.get_or_create(account=scope,
                                                                 alert=saved_alert,
                                                                 entity_instance_id=alert_data.get(
                                                                     'entity_instance_id'),
                                                                 type=AlertEntityInstance.Type.PER_EVENT)
                generated_alerts.append(saved_alert)

        return generated_alerts


per_event_trigger_processor = PerEventTriggerProcessor()


class TriggerProcessorFacade:

    def __init__(self):
        self._map = {}

    def register(self, trigger_type: TriggerDefinition.Type, typed_trigger_processor: TriggerProcessor):
        self._map[trigger_type] = typed_trigger_processor

    def process_triggers(self, scope, trigger, time_lower_bound, time_upper_bound) -> [Alert]:
        return self._map[trigger["type"]].evaluate_triggers(scope, trigger, time_lower_bound, time_upper_bound)


trigger_processor = TriggerProcessorFacade()
trigger_processor.register(EntityTriggerDefinition.TriggerType.PER_EVENT, PerEventTriggerProcessor())


def process_trigger(scope, trigger, time_lower_bound, time_upper_bound) -> [Alert]:
    return trigger_processor.process_triggers(scope, trigger, time_lower_bound, time_upper_bound)
