import logging

from django.conf import settings
from django.db import transaction as dj_transaction
from django.db.models import Avg, Count, F
from google.protobuf.wrappers_pb2 import UInt64Value, StringValue

from accounts.models import Account
from event.cache import GLOBAL_PANEL_CACHE
from event.models import Entity, EntityEventKeyMapping, EntityMonitorMapping, Monitor
from event.monitors_crud import create_monitors
from management.models import PeriodicTaskStatus
from management.tasks_crud import get_task_run_for_task_account_status
from protos.event.entity_pb2 import EntityPartial, Entity as EntityProto, WorkflowView
from protos.event.panel_pb2 import FunnelPanel, PanelV1, PanelData
from prototype.utils.timerange import DateTimeRange, filter_dtr
from utils.proto_utils import proto_to_dict

start_node_conn_types = [WorkflowView.NodeConnectionType.OUT]
mid_node_conn_types = [WorkflowView.NodeConnectionType.IN, WorkflowView.NodeConnectionType.OUT]
end_node_conn_types = [WorkflowView.NodeConnectionType.IN]

logger = logging.getLogger(__name__)


class EntityFunnelCrudIncorrectPayloadException(ValueError):
    pass


class EntityFunnelCrudNotFoundException(ValueError):
    pass


def save_entity_funnel_panel_config(scope, entity_funnel_panel: PanelV1):
    try:
        GLOBAL_PANEL_CACHE.create_or_update(account_id=scope.id, name=entity_funnel_panel.meta_info.name,
                                            panel=proto_to_dict(entity_funnel_panel))
        return True
    except Exception as e:
        logger.error(f'Error saving Entity Funnel Panel in Cache: {e}')
    return False


def db_get_funnel_entity(scope: Account, funnel_entity: EntityPartial, is_active=None) -> Entity:
    filters = {}
    if funnel_entity.id.value:
        filters['id'] = funnel_entity.id.value
    if funnel_entity.name.value:
        filters['name'] = funnel_entity.name.value
    if is_active:
        filters['is_active'] = is_active
    try:
        if not filters:
            raise EntityFunnelCrudIncorrectPayloadException(f'Incorrect payload - Missing entity funnel details')
        return scope.entity_set.get(**filters)
    except Entity.DoesNotExist:
        raise EntityFunnelCrudNotFoundException(f'No Entity Funnel found with details {funnel_entity}')


def check_if_entity_funnel_exists(scope, entity_id=None, entity_name=None, is_active=None) -> bool:
    filters = {}
    if entity_id:
        filters['id'] = entity_id
    if entity_name:
        filters['name'] = entity_name
    if is_active:
        filters['is_active'] = is_active
    try:
        return scope.entity_set.filter(**filters).exists()
    except Exception as e:
        raise EntityFunnelCrudNotFoundException(f'Entity Check Failed with details {e}')


def db_save_entity_funnel(scope, name, event_key_ids, event_key_tuples):
    created_monitors: [Monitor] = []
    updated_inactive_monitors = []
    with dj_transaction.atomic():
        e = Entity(
            account=scope,
            name=name,
            type=EntityProto.Type.FUNNEL,
            is_active=True,
            is_generated=True
        )
        e.save()

        ems: [EntityMonitorMapping] = []
        for pair in event_key_tuples:
            primary_event_key_id = pair[0]
            secondary_event_key_id = pair[1]

            monitor_name = 'system_generated_monitor_' + str(primary_event_key_id) + '_' + str(secondary_event_key_id)
            db_monitor, is_created, meta = create_monitors(scope, monitor_name, primary_event_key_id,
                                                           secondary_event_key_id,
                                                           is_generated=True)
            if not db_monitor and meta:
                raise EntityFunnelCrudIncorrectPayloadException(f'Error Creating Entity Funnel: {meta}')

            if is_created:
                if meta:
                    updated_inactive_monitors.append((db_monitor, meta))
                created_monitors.append(db_monitor)
            ems.append(
                EntityMonitorMapping(account=scope, entity=e, monitor=db_monitor, is_active=True, is_generated=True))

        if ems:
            EntityMonitorMapping.objects.bulk_create(ems, ignore_conflicts=True, batch_size=25)

        eekms: [EntityEventKeyMapping] = [EntityEventKeyMapping(account=scope, entity=e, event_key_id=event_key_id) for
                                          event_key_id in
                                          event_key_ids]

        if eekms:
            EntityEventKeyMapping.objects.bulk_create(
                eekms,
                ignore_conflicts=True,
                batch_size=25
            )
    return e, created_monitors, updated_inactive_monitors


def entity_funnels_create(scope, entity_funnel_panel: PanelV1) -> (Entity, str):
    if not entity_funnel_panel or not entity_funnel_panel.meta_info or not entity_funnel_panel.meta_info.name:
        return None, 'Incorrect Payload: Missing Entity Funnel Name'

    entity_funnel_name: str = entity_funnel_panel.meta_info.name
    if check_if_entity_funnel_exists(scope, entity_name=entity_funnel_name):
        return None, f'Incorrect Payload: Entity Funnel with name {entity_funnel_name} already exists'

    if not save_entity_funnel_panel_config(scope, entity_funnel_panel):
        return None, f'Incorrect Payload: Unable to save Entity Funnel Panel in Cache'

    entity_funnel_panel_data: PanelData = entity_funnel_panel.data
    which_one_of = entity_funnel_panel_data.WhichOneof('data')
    if not entity_funnel_panel_data.type == PanelData.PanelDataType.FUNNEL or not which_one_of == 'funnel':
        return None, f'Incorrect Payload: Panel Data Type is not Funnel'

    entity_funnel_config: FunnelPanel = entity_funnel_panel_data.funnel
    event_key_name = entity_funnel_config.event_key_name
    event_type_ids = entity_funnel_config.event_type_ids
    event_id_tuples = [(event_type_ids[i], event_type_ids[i + 1]) for i in range(len(event_type_ids) - 1)]
    if not event_type_ids or not event_key_name:
        return None, 'Incorrect Payload: Missing Entity Funnel Event Type Ids/Event Key'

    event_keys = scope.eventkey_set.filter(event_type__in=event_type_ids, name=event_key_name).values('id',
                                                                                                      'event_type_id')
    if event_keys.count() != len(event_type_ids):
        return None, f'Incorrect Payload: Invalid Entity Funnel Event Keys'

    event_key_tuples = []
    for pair in event_id_tuples:
        primary_event_key_id = next((x['id'] for x in event_keys if x['event_type_id'] == pair[0]), None)
        secondary_event_key_id = next((x['id'] for x in event_keys if x['event_type_id'] == pair[1]), None)
        if not primary_event_key_id or not secondary_event_key_id:
            return None, f'Incorrect Payload: Missing Entity Funnel DB Event Keys'
        event_key_tuples.append((primary_event_key_id, secondary_event_key_id))

    try:
        db_entity_funnel, created_monitors, updated_inactive_monitors = db_save_entity_funnel(scope, entity_funnel_name,
                                                                                              event_keys.values_list(
                                                                                                  'id', flat=True),
                                                                                              event_key_tuples)
        return db_entity_funnel, None
    except Exception as e:
        logger.error(f'Error Creating Entity Funnel: {e}')
        return None, f'Incorrect Payload: Unable to save Entity Funnel in DB'