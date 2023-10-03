from typing import Dict

from django.conf import settings

from event.models import Monitor, Trigger, EventKey, TriggerNotificationConfigMapping, is_filterable_key_type
from event.notification.notifications_crud import create_db_notifications
from protos.event.literal_pb2 import LiteralType
from protos.event.notification_pb2 import NotificationConfig
from protos.event.trigger_pb2 import Trigger as TriggerProto, TriggerPriority, TriggerDefinition, BasicTriggerFilter, \
    DelayedEventTrigger
from utils.proto_utils import proto_to_dict


class TriggerCrudException(ValueError):
    pass


def get_monitor(scope, trigger: TriggerProto) -> Monitor:
    try:
        if not trigger.monitor or not trigger.monitor.id:
            raise TriggerCrudException(f'Incorrect payload - Missing monitor id')
        else:
            monitor: Monitor = scope.monitor_set.get(id=trigger.monitor.id)
            return monitor
    except Monitor.DoesNotExist:
        raise TriggerCrudException(f'No monitor found with id {trigger.monitor.id}')


def create_monitor_triggers(scope, triggers: [TriggerProto], notifications: [NotificationConfig]) -> ([Trigger], str):
    db_triggers: [Trigger] = []
    for trigger in triggers:
        if not trigger.name or not trigger.definition or not trigger.definition.type:
            return [], 'Received invalid Trigger Config'

        trigger_name: str = trigger.name
        trigger_definition: TriggerDefinition = trigger.definition
        priority: TriggerPriority = trigger.priority
        try:
            monitor: Monitor = get_monitor(scope, trigger)
        except TriggerCrudException as tce:
            return [], str(tce)

        which_one_of = trigger_definition.WhichOneof('trigger')
        if trigger_definition.type == TriggerDefinition.Type.MISSING_EVENT and which_one_of == 'missing_event_trigger':

            if trigger_definition.missing_event_trigger.transaction_time_threshold.value <= 0:
                return [], 'Received invalid Missing Event Trigger Config'

            trigger_config = proto_to_dict(trigger_definition.missing_event_trigger)
        elif trigger_definition.type == TriggerDefinition.Type.DELAYED_EVENT and which_one_of == 'delayed_event_trigger':

            if trigger_definition.delayed_event_trigger.trigger_threshold.value < 0 or \
                    trigger_definition.delayed_event_trigger.transaction_time_threshold.value <= 0 or \
                    trigger_definition.delayed_event_trigger.resolution.value < \
                    settings.DELAYED_EVENT_TRIGGER_RESOLUTION_WINDOW_LOWER_BOUND_IN_SEC:
                return [], 'Received invalid Delayed Event Aggregated Trigger Config'

            if trigger_definition.delayed_event_trigger.transaction_time_threshold.value >= \
                    trigger_definition.delayed_event_trigger.resolution.value:
                return [], 'Transaction time cannot be greater than or equal to resolution window'

            if trigger_definition.delayed_event_trigger.type == DelayedEventTrigger.Type.UNKNOWN:
                if trigger_definition.delayed_event_trigger.skip_unfinished_transactions.value:
                    trigger_definition.delayed_event_trigger.type = DelayedEventTrigger.Type.DELAYED_EVENTS
                else:
                    trigger_definition.delayed_event_trigger.type = DelayedEventTrigger.Type.MISSING_AND_DELAYED_EVENTS
            trigger_config = proto_to_dict(trigger_definition.delayed_event_trigger)

        else:
            return [], 'Received invalid trigger definition'

        try:
            primary_event_filters = process_trigger_filters(scope, trigger_definition.primary_event_filters,
                                                            monitor.primary_key.event_type_id)
            secondary_event_filters = process_trigger_filters(scope, trigger_definition.secondary_event_filters,
                                                              monitor.secondary_key.event_type_id)
        except ValueError:
            return [], 'Received invalid event filter keys'

        generated_config = {'primary_event_filters': primary_event_filters,
                            'secondary_event_filters': secondary_event_filters}
        db_triggers.append(
            Trigger(name=trigger_name, type=trigger_definition.type, config=trigger_config, priority=priority,
                    generated_config=generated_config, monitor=monitor))

    duplicate_triggers = []
    created_trigger = []
    for db_t in db_triggers:
        trigger, created = Trigger.objects.get_or_create(account=scope,
                                                         name=db_t.name,
                                                         defaults={
                                                             'monitor': db_t.monitor,
                                                             'type': db_t.type,
                                                             'config': db_t.config,
                                                             'generated_config': db_t.generated_config,
                                                             'priority': db_t.priority,
                                                             "is_active": True
                                                         })
        if created:
            created_trigger.append(trigger)
        else:
            duplicate_triggers.append(trigger)

    map_notifications_for_triggers(scope, created_trigger, notifications)

    return duplicate_triggers, None


def process_trigger_filters(scope, filters: [BasicTriggerFilter], event_type_id) -> Dict:
    filter_map = {'event__event_type_id': event_type_id}
    for f in filters:
        try:
            event_key = scope.eventkey_set.get(id=f.event_key_id)
        except EventKey.DoesNotExist:
            raise ValueError('Event filter key does not exist')

        key = 'event__processed_kvs__' + event_key.name

        f_literal = f.literal
        if not is_filterable_key_type(event_key.type):
            raise ValueError('Invalid event key type encountered')

        if f_literal.literal_type == LiteralType.STRING:
            value = f.literal.string.value
        elif f_literal.literal_type == LiteralType.BOOLEAN:
            value = f.literal.boolean.value
        elif f_literal.literal_type == LiteralType.LONG:
            value = f.literal.long.value
        elif f_literal.literal_type == LiteralType.DOUBLE:
            value = f.literal.double.value
        elif f_literal.literal_type == LiteralType.STRING_ARRAY:
            key += "__in"
            value = [f'{string}' for string in f.literal.string_array]
        else:
            raise ValueError('Invalid key type encountered')

        filter_map[key] = value
    return filter_map


def map_notifications_for_triggers(scope, db_triggers: [Trigger], notifications: [NotificationConfig]):
    db_notifications = create_db_notifications(scope, notifications)
    for db_t in db_triggers:
        for db_n in db_notifications:
            TriggerNotificationConfigMapping.objects.update_or_create(account=scope, trigger=db_t, notification=db_n)
