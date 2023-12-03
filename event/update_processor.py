import copy
from typing import List, Callable, Dict

from django.conf import settings
from django.db import transaction as dj_transaction, IntegrityError
from google.protobuf.message import Message

from event.models import Entity, EntityEventKeyMapping, Trigger, TriggerNotificationConfigMapping, Monitor, \
    EntityMonitorMapping
from event.monitors_triggers_crud import process_trigger_filters
from event.notification.notifications_crud import create_db_notifications
from protos.event.entity_pb2 import UpdateEntityOp, UpdateEntityFunnelOp
from protos.event.monitor_pb2 import UpdateMonitorOp
from protos.event.trigger_pb2 import UpdateTriggerOp, TriggerDefinition
from utils.proto_utils import proto_to_dict


def msg_getter(field_name):
    def getter(msg):
        return getattr(msg, field_name, None)

    getter.__name__ = f'{field_name}_getter'
    return getter


class UpdateProcessorError(ValueError):
    pass


class UpdateProcessorMixin:
    update_op_cls = None

    def __init__(self, *args, **kwargs):
        if self.update_op_cls is None:
            raise Exception("update_op_cls must be set")
        op_enum = self.update_op_cls.DESCRIPTOR.enum_types_by_name['Op']
        self._op_name_dict: Dict[int, Callable] = {
            op.number: op.name.lower() for op in op_enum.values if op.number > 0
        }
        self._op_display_str_dict: Dict[int, Callable] = {
            op.number: op.name.replace('_', ' ').capitalize() for op in op_enum.values if op.number > 0
        }
        self._op_fn_dict: Dict[int, Callable] = {
            op.number: getattr(self, op.name.lower(), None) for op in op_enum.values if op.number > 0
        }
        self._op_msg_field_getter_dict: Dict[int, Callable] = {
            op.number: msg_getter(op.name.lower()) for op in op_enum.values if op.number > 0
        }

    def update(self, elem, update_ops: List[Message]):
        clone_elem = copy.deepcopy(elem)

        with dj_transaction.atomic():
            for update_op in update_ops:
                op = update_op.op
                op_fn = self._op_fn_dict.get(op, None)
                if op_fn is None:
                    raise Exception(f"Unknown op: {op}")
                op_name: str = self._op_name_dict.get(op, '')
                msg_field_getter = self._op_msg_field_getter_dict.get(op, None)
                update_op_msg = msg_field_getter(update_op)
                try:
                    elem = op_fn(elem, update_op_msg)
                except Exception as ex:
                    raise UpdateProcessorError(
                        f"{self._op_display_str_dict.get(op)} error for: {clone_elem.name} - {ex}"
                    )


class EntityUpdateProcessor(UpdateProcessorMixin):
    update_op_cls = UpdateEntityOp

    @staticmethod
    def update_entity_name(elem: Entity, update_op: UpdateEntityOp.UpdateEntityName) -> Entity:
        if not update_op.name.value:
            raise Exception(f"New entity name missing for update entity name op")

        if update_op.name.value == elem.name:
            return elem
        elem.name = update_op.name.value
        try:
            elem.save(update_fields=['name'])
        except IntegrityError as ex:
            raise Exception(f"Entity name {update_op.name.value} already exists")
        return elem

    @staticmethod
    def update_entity_status(elem: Entity, update_op: UpdateEntityOp.UpdateEntityStatus) -> Entity:
        elem.is_active = update_op.is_active.value
        elem.save(update_fields=['is_active'])
        return elem

    @staticmethod
    def update_entity_event_key_mapping_status(elem: Entity,
                                               update_op: UpdateEntityOp.UpdateEntityEventKeyMappingStatus) -> Entity:
        if not update_op.entity_event_key_mapping_id.value:
            raise Exception(f"Entity event key mapping id missing for update key status op")

        entity_event_key_mapping_id: int = update_op.entity_event_key_mapping_id.value

        qs = elem.entityeventkeymapping_set.filter(id=entity_event_key_mapping_id)
        if not qs.exists():
            raise Exception(f"Entity event key mapping id {entity_event_key_mapping_id} not found")

        entity_event_key_mapping: EntityEventKeyMapping = qs.first()
        entity_event_key_mapping.is_active = update_op.is_active.value
        entity_event_key_mapping.save(update_fields=['is_active'])

        return elem

    @staticmethod
    def add_entity_event_key_mappings(elem: Entity, update_op: UpdateEntityOp.AddEntityEventKeyMappings) -> Entity:
        event_key_ids: List[int] = update_op.event_key_ids
        if not event_key_ids:
            raise Exception(f"Event key ids missing for add entity event key mapping op")

        if len(event_key_ids) != elem.account.eventkey_set.filter(id__in=event_key_ids).count():
            raise Exception(f"Invalid event key ids for add entity event key mapping op")

        eekms = [
            EntityEventKeyMapping(
                account=elem.account, entity=elem, event_key_id=event_key_id
            ) for event_key_id in event_key_ids
        ]

        if eekms:
            EntityEventKeyMapping.objects.bulk_create(
                eekms,
                ignore_conflicts=True,
                batch_size=25
            )

        return elem

    @staticmethod
    def remove_entity_event_key_mappings(elem: Entity,
                                         update_op: UpdateEntityOp.RemoveEntityEventKeyMappings) -> Entity:
        entity_event_key_mapping_ids: List[int] = update_op.entity_event_key_mapping_ids
        if not entity_event_key_mapping_ids:
            raise Exception(f"Entity event key mapping missing for remove entity event key mapping op")

        qs = elem.entityeventkeymapping_set.filter(id__in=entity_event_key_mapping_ids)
        if len(entity_event_key_mapping_ids) != qs.count():
            raise Exception(f"Invalid entity event key mapping for remove entity event key mapping op")
        qs.delete()
        return elem


class MonitorUpdateProcessor(UpdateProcessorMixin):
    update_op_cls = UpdateMonitorOp

    @staticmethod
    def update_monitor_name(elem: Monitor, update_op: UpdateMonitorOp.UpdateMonitorName) -> Monitor:
        if not update_op.name.value:
            raise Exception(f"New monitor name missing for update monitor name op")

        if update_op.name.value == elem.name:
            return elem
        if elem.account.monitor_set.filter(name=update_op.name.value).exists():
            raise Exception(f"Monitor with name {update_op.name.value} already exists")
        elem.name = update_op.name.value
        elem.save(update_fields=['name'])
        return elem

    @staticmethod
    def update_monitor_primary_key(elem: Monitor, update_op: UpdateMonitorOp.UpdateMonitorPrimaryKey) -> Monitor:
        if update_op.primary_event_key.id == elem.primary_key.id:
            return elem
        raise Exception(f"Monitor primary key cannot be updated")

    @staticmethod
    def update_monitor_secondary_key(elem: Monitor, update_op: UpdateMonitorOp.UpdateMonitorSecondaryKey) -> Monitor:
        if update_op.secondary_event_key.id == elem.secondary_key.id:
            return elem
        raise Exception(f"Monitor secondary key cannot be updated")

    @staticmethod
    def update_monitor_status(elem: Monitor, update_op: UpdateMonitorOp.UpdateMonitorStatus) -> Monitor:
        elem.is_active = update_op.is_active.value
        elem.save(update_fields=['is_active'])
        return elem

    @staticmethod
    def update_monitor_is_generated(elem: Monitor, update_op: UpdateMonitorOp.UpdateMonitorIsGenerated) -> Monitor:
        elem.is_generated = update_op.is_generated.value
        elem.save(update_fields=['is_generated'])
        return elem


class MonitorTriggerUpdateProcessor(UpdateProcessorMixin):
    update_op_cls = UpdateTriggerOp

    @staticmethod
    def update_trigger_name(elem: Trigger, update_op: UpdateTriggerOp.UpdateTriggerName) -> Trigger:
        if not update_op.name.value:
            raise Exception(f"New trigger name missing for update trigger name op")

        if update_op.name.value == elem.name:
            return elem
        elem.name = update_op.name.value
        elem.save(update_fields=['name'])
        return elem

    @staticmethod
    def update_trigger_status(elem: Trigger, update_op: UpdateTriggerOp.UpdateTriggerStatus) -> Trigger:
        elem.is_active = update_op.is_active.value
        elem.save(update_fields=['is_active'])
        return elem

    @staticmethod
    def update_trigger_priority(elem: Trigger, update_op: UpdateTriggerOp.UpdateTriggerPriority) -> Trigger:

        elem.priority = update_op.priority
        elem.save(update_fields=['priority'])
        return elem

    @staticmethod
    def update_trigger_definition(elem: Trigger, update_op: UpdateTriggerOp.UpdateTriggerDefinition) -> Trigger:
        trigger_definition = update_op.definition
        td_which_one_of = trigger_definition.WhichOneof('trigger')
        if trigger_definition.type == TriggerDefinition.Type.MISSING_EVENT and td_which_one_of == 'missing_event_trigger':
            if trigger_definition.missing_event_trigger.transaction_time_threshold.value <= 0:
                raise Exception(f"Invalid missing event trigger config")
            trigger_config = proto_to_dict(trigger_definition.missing_event_trigger)
        elif trigger_definition.type == TriggerDefinition.Type.DELAYED_EVENT and td_which_one_of == 'delayed_event_trigger':
            if trigger_definition.delayed_event_trigger.trigger_threshold.value < 0 or \
                    trigger_definition.delayed_event_trigger.transaction_time_threshold.value <= 0 or \
                    trigger_definition.delayed_event_trigger.resolution.value < \
                    settings.DELAYED_EVENT_TRIGGER_RESOLUTION_WINDOW_LOWER_BOUND_IN_SEC:
                raise Exception(f"Invalid delayed aggregated event trigger config")
            elif trigger_definition.delayed_event_trigger.transaction_time_threshold.value >= \
                    trigger_definition.delayed_event_trigger.resolution.value:
                raise Exception(f"Delayed aggregated event trigger transaction time cannot be >= to resolution window")
            trigger_config = proto_to_dict(trigger_definition.delayed_event_trigger)
        else:
            raise Exception(f"Invalid trigger definition")

        try:
            primary_event_filters = process_trigger_filters(elem.account, trigger_definition.primary_event_filters,
                                                            elem.monitor.primary_key.event_type_id)
            secondary_event_filters = process_trigger_filters(elem.account, trigger_definition.secondary_event_filters,
                                                              elem.monitor.secondary_key.event_type_id)
        except ValueError:
            raise Exception(f"Received invalid event filter keys")

        generated_config = {'primary_event_filters': primary_event_filters,
                            'secondary_event_filters': secondary_event_filters}

        elem.type = trigger_definition.type
        elem.config = trigger_config
        elem.generated_config = generated_config
        elem.save(update_fields=['type', 'config', 'generated_config'])
        return elem

    @staticmethod
    def update_trigger_notifications(elem: Trigger, update_op: UpdateTriggerOp.UpdateTriggerNotifications) -> Trigger:
        notifications = update_op.notifications

        db_notifications = create_db_notifications(elem.account, notifications)
        elem.account.triggernotificationconfigmapping_set.filter(trigger=elem).delete()
        for db_n in db_notifications:
            TriggerNotificationConfigMapping.objects.update_or_create(account=elem.account, trigger=elem,
                                                                      notification=db_n)
        return elem


class EntityFunnelUpdateProcessor(UpdateProcessorMixin):
    update_op_cls = UpdateEntityFunnelOp

    @staticmethod
    def update_entity_funnel_name(elem: Entity, update_op: UpdateEntityFunnelOp.UpdateEntityFunnelName) -> Entity:
        if not update_op.name.value:
            raise Exception(f"New entity name missing for update entity funnel name op")

        if update_op.name.value == elem.name:
            return elem
        elem.name = update_op.name.value
        try:
            elem.save(update_fields=['name'])
        except IntegrityError as ex:
            raise Exception(f"Entity name {update_op.name.value} already exists")
        return elem

    @staticmethod
    def update_entity_funnel_status(elem: Entity, update_op: UpdateEntityFunnelOp.UpdateEntityFunnelStatus) -> Entity:
        elem.is_active = update_op.is_active.value
        elem.save(update_fields=['is_active'])
        return elem

    @staticmethod
    def update_entity_funnel_monitor_mapping_status(elem: Entity,
                                                    update_op: UpdateEntityFunnelOp.UpdateEntityFunnelMonitorMappingStatus) -> Entity:
        if not update_op.entity_funnel_monitor_mapping_id.value:
            raise Exception(f"Entity funnel monitor mapping id missing for update key status op")

        entity_funnel_monitor_mapping_id: int = update_op.entity_event_key_mapping_id.value

        qs = elem.entitymonitormapping_set.filter(id=entity_funnel_monitor_mapping_id)
        if not qs.exists():
            raise Exception(f"Entity monitor mapping id {entity_funnel_monitor_mapping_id} not found")

        entity_funnel_monitor_mapping: EntityMonitorMapping = qs.first()
        entity_funnel_monitor_mapping.is_active = update_op.is_active.value
        entity_funnel_monitor_mapping.save(update_fields=['is_active'])

        monitor = entity_funnel_monitor_mapping.monitor
        if not elem.entitymonitormapping_set.filter(monitor=monitor).exclude(entity=elem).exists():
            if monitor.is_generated:
                monitor.is_active = False
                monitor.save(update_fields=['is_active'])

        return elem

    @staticmethod
    def add_entity_funnel_monitor_mappings(elem: Entity,
                                           update_op: UpdateEntityFunnelOp.AddEntityFunnelMonitorMappings) -> Entity:
        monitor_ids: List[int] = update_op.monitor_ids
        if not monitor_ids:
            raise Exception(f"monitor ids missing for add entity event key mapping op")

        if len(monitor_ids) != elem.account.monitor_set.filter(id__in=monitor_ids).count():
            raise Exception(f"Invalid monitor ids for add entity funnel monitor mapping op")

        monitors = elem.account.monitor_set.filter(id__in=monitor_ids)
        for monitor in monitors:
            if not monitor.is_active:
                monitor.is_active = True
                update_fields = ['is_active']
                if not monitor.is_generated:
                    monitor.is_generated = True
                    update_fields.append('is_generated')
                monitor.save(update_fields=update_fields)

        emms = [
            EntityMonitorMapping(
                account=elem.account, entity=elem, monitor_id=monitor_id
            ) for monitor_id in monitor_ids
        ]

        if emms:
            EntityMonitorMapping.objects.bulk_create(
                emms,
                ignore_conflicts=True,
                batch_size=25
            )

        return elem

    @staticmethod
    def remove_entity_funnel_monitor_mappings(elem: Entity,
                                              update_op: UpdateEntityFunnelOp.RemoveEntityFunnelMonitorMappings) -> Entity:
        entity_monitor_mapping_ids: List[int] = update_op.entity_funnel_monitor_mapping_ids
        if not entity_monitor_mapping_ids:
            raise Exception(f"Entity funnel monitor mapping missing for remove entity event key mapping op")

        qs = elem.entitymonitormapping_set.filter(id__in=entity_monitor_mapping_ids)
        qs = qs.select_related('monitor')
        if len(entity_monitor_mapping_ids) != qs.count():
            raise Exception(f"Invalid entity funnel monitor mapping for remove entity monitor mapping op")

        for entity_monitor_mapping in qs:
            if entity_monitor_mapping.is_active:
                entity_monitor_mapping.is_active = False
                entity_monitor_mapping.save(update_fields=['is_active'])
            monitor = entity_monitor_mapping.monitor
            if not elem.account.entitymonitormapping_set.filter(monitor=monitor, is_active=True).exclude(
                    entity=elem).exists() and \
                    not elem.account.trigger_set.filter(monitor=monitor, is_active=True).exists() \
                    and monitor.is_generated:
                monitor.is_active = False
                monitor.save(update_fields=['is_active'])

        return elem


entity_update_processor = EntityUpdateProcessor()
monitor_update_processor = MonitorUpdateProcessor()
monitor_trigger_update_processor = MonitorTriggerUpdateProcessor()
entity_funnel_update_processor = EntityFunnelUpdateProcessor()