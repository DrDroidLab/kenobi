import logging

from django.conf import settings
from django.db import transaction as dj_transaction
from django.db.models import Avg, Count, F
from google.protobuf.wrappers_pb2 import UInt64Value, StringValue

from accounts.models import Account
from event.cache import GLOBAL_PANEL_CACHE
from event.clickhouse.models import MonitorTransactions, Events
from event.models import Entity, EntityEventKeyMapping, EntityMonitorMapping, Monitor
from event.monitors_crud import create_monitors
from management.models import PeriodicTaskStatus
from management.tasks_crud import get_task_run_for_task_account_status
from protos.event.entity_pb2 import EntityPartial, Entity as EntityProto, WorkflowView
from protos.event.panel_pb2 import FunnelPanel, PanelV1, PanelData
from protos.event.monitor_pb2 import MonitorTransaction as MonitorTransactionProto
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


def entity_funnels_get(scope: Account, dtr: DateTimeRange, entity_funnel_name: str, filter_key_name=None,
                       filter_value=None):
    if not scope:
        raise EntityFunnelCrudIncorrectPayloadException(f'Incorrect Panel Payload: Missing Account')
    account_id = scope.id
    if not entity_funnel_name:
        raise EntityFunnelCrudIncorrectPayloadException(f'Incorrect Panel Payload: Missing Entity Funnel Name')

    try:
        db_entity_funnel = db_get_funnel_entity(scope,
                                                funnel_entity=EntityPartial(name=StringValue(value=entity_funnel_name)),
                                                is_active=True)
    except (EntityFunnelCrudIncorrectPayloadException, EntityFunnelCrudNotFoundException):
        raise EntityFunnelCrudNotFoundException(
            f'Incorrect Panel Payload: Active Entity with name {entity_funnel_name} does not exist')

    entity_monitor = scope.entitymonitormapping_set.filter(entity=db_entity_funnel, is_active=True).order_by(
        'created_at')
    entity_monitor = entity_monitor.prefetch_related('monitor').values('monitor_id',
                                                                       'monitor__primary_key__name',
                                                                       'monitor__primary_key__event_type_id',
                                                                       'monitor__primary_key__event_type__name',
                                                                       'monitor__secondary_key__event_type_id',
                                                                       'monitor__secondary_key__event_type__name')
    if not entity_monitor:
        raise EntityFunnelCrudIncorrectPayloadException(
            f'Incorrect Panel Payload: Entity Funnel Monitors not found for {entity_funnel_name}')

    if dtr.time_geq < db_entity_funnel.created_at:
        back_fill_job_config = getattr(settings, 'BACK_FILL_JOB_CONFIG', {})
        if back_fill_job_config and 'monitor_transaction' in back_fill_job_config and \
                back_fill_job_config['monitor_transaction'].get('enabled', False):
            entity_monitor_ids = [monitor['monitor_id'] for monitor in entity_monitor]
            kwargs = {'monitor_id__in': entity_monitor_ids}
            fargs = {'kwargs': kwargs}
            status_list = [PeriodicTaskStatus.FAILED, PeriodicTaskStatus.RUNNING, PeriodicTaskStatus.SCHEDULED]
            running_back_fill_tasks = get_task_run_for_task_account_status(
                task_name='back_fill_monitor_transaction_task',
                task_fargs=fargs,
                account=scope,
                status_list=status_list)
            if running_back_fill_tasks:
                raise EntityFunnelCrudIncorrectPayloadException(
                    f'Back Fill Monitor Transaction Tasks are running for {entity_funnel_name}')
        else:
            raise EntityFunnelCrudNotFoundException(
                f'Incorrect Panel Payload: Time Range is less than Entity Funnel Creation Time')
    data = []
    links = []
    node_map = {}
    edge_map = {}
    unique_transactions_set = None
    for idx, monitor in enumerate(entity_monitor):
        if idx <= 0:
            unique_transactions_set = MonitorTransactions.objects.filter(account_id=account_id).filter(
                monitor_id=monitor['monitor_id']).filter(
                event_type_id=monitor['monitor__primary_key__event_type_id'])
            unique_transactions_set = filter_dtr(unique_transactions_set, dtr, 'event_timestamp')
            if filter_key_name and filter_value:
                unique_transactions_set = unique_transactions_set.annotate(
                    event_attribute=F('event_processed_kvs__{}'.format(filter_key_name)))
                unique_transactions_set = unique_transactions_set.filter(event_attribute=filter_value)
            unique_transactions_set = unique_transactions_set.values_list('transaction', flat=True).distinct()
        else:
            unique_transactions_set = MonitorTransactions.objects.filter(account_id=account_id).filter(
                monitor_id=monitor['monitor_id']).filter(
                event_type_id=monitor['monitor__primary_key__event_type_id']).filter(
                transaction__in=unique_transactions_set)
            unique_transactions_set = unique_transactions_set.values_list('transaction', flat=True).distinct()

        monitor_transactions = MonitorTransactions.objects.filter(account_id=account_id).filter(
            event_timestamp__gte=dtr.time_geq).filter(monitor_id=monitor['monitor_id']).filter(
            monitor_transaction_event_type=MonitorTransactionProto.MonitorTransactionEventType.PRIMARY).filter(
            transaction__in=unique_transactions_set).values('monitor_id').annotate(
            transaction_count=Count('transaction', distinct=True))

        monitor_transactions_finished = MonitorTransactions.objects.filter(account_id=account_id).filter(
            event_timestamp__gte=dtr.time_geq).filter(monitor_id=monitor['monitor_id']).filter(
            monitor_transaction_event_type=MonitorTransactionProto.MonitorTransactionEventType.SECONDARY).filter(
            transaction__in=unique_transactions_set).values('monitor_id').annotate(
            avg_duration=Avg('transaction_time')).annotate(
            completed_transaction_count=Count('transaction', distinct=True))

        primary_node_transaction_count = monitor_transactions[0]['transaction_count'] if monitor_transactions else 0
        secondary_node_transaction_count = monitor_transactions_finished[0].get('completed_transaction_count', 0) if \
            monitor_transactions_finished else 0
        avg_duration = monitor_transactions_finished[0].get('avg_duration', 0) if monitor_transactions_finished else 0

        primary_conn_types = mid_node_conn_types
        secondary_conn_types = mid_node_conn_types
        if len(data) == 0:
            primary_conn_types = start_node_conn_types
        elif idx >= len(entity_monitor) - 1:
            secondary_conn_types = end_node_conn_types

        primary_node = WorkflowView.Node(
            node_id=UInt64Value(value=monitor['monitor__primary_key__event_type_id']),
            label=StringValue(value=monitor['monitor__primary_key__event_type__name']),
            connection_types=primary_conn_types,
            metrics=[
                WorkflowView.Node.NodeMetric(name=StringValue(value="Count"),
                                             value=StringValue(value=str(primary_node_transaction_count)),
                                             metric_status=WorkflowView.MetricStatus.GREEN)
            ]
        )

        secondary_node = WorkflowView.Node(
            node_id=UInt64Value(value=monitor['monitor__secondary_key__event_type_id']),
            label=StringValue(value=monitor['monitor__secondary_key__event_type__name']),
            connection_types=secondary_conn_types,
            metrics=[
                WorkflowView.Node.NodeMetric(name=StringValue(value="Count"),
                                             value=StringValue(value=str(secondary_node_transaction_count)),
                                             metric_status=WorkflowView.MetricStatus.GREEN)
            ]
        )

        if primary_node.node_id.value not in node_map:
            node_map[primary_node.node_id.value] = primary_node
            data.append(primary_node)
        if secondary_node.node_id.value not in node_map:
            node_map[secondary_node.node_id.value] = secondary_node
            data.append(secondary_node)

        edge = "{}-{}".format(primary_node.node_id.value, secondary_node.node_id.value)

        drop_percent = 0
        if primary_node_transaction_count > 0:
            drop_percent = round(((primary_node_transaction_count - secondary_node_transaction_count) * 100 /
                                  primary_node_transaction_count), 2)

        if edge and edge not in edge_map:
            edge_map[edge] = True
        links.append(
            WorkflowView.Edge(
                start_node_id=UInt64Value(value=primary_node.node_id.value),
                end_node_id=UInt64Value(value=secondary_node.node_id.value),
                metrics=[
                    WorkflowView.Edge.EdgeMetric(name=StringValue(value="Drop"),
                                                 value=StringValue(value="{}%".format(str(drop_percent))),
                                                 metric_status=WorkflowView.MetricStatus.GREEN),
                    WorkflowView.Edge.EdgeMetric(name=StringValue(value="Avg Time"),
                                                 value=StringValue(value="{} sec".format(str(avg_duration))),
                                                 metric_status=WorkflowView.MetricStatus.GREEN)
                ],
            )
        )

    return WorkflowView(nodes=data, edges=links)


def entity_funnels_drop_off_get(scope: Account, dtr: DateTimeRange, entity_funnel_name: str, event_key_name,
                                start_event_type_id, end_event_type_id, filter_key_name=None, filter_value=None):
    if not scope:
        raise EntityFunnelCrudIncorrectPayloadException(f'Incorrect Panel Payload: Missing Account')
    account_id = scope.id
    if not entity_funnel_name:
        raise EntityFunnelCrudIncorrectPayloadException(f'Incorrect Panel Payload: Missing Entity Funnel Name')

    try:
        db_entity_funnel = db_get_funnel_entity(scope,
                                                funnel_entity=EntityPartial(name=StringValue(value=entity_funnel_name)),
                                                is_active=True)
    except (EntityFunnelCrudIncorrectPayloadException, EntityFunnelCrudNotFoundException):
        raise EntityFunnelCrudNotFoundException(
            f'Incorrect Panel Payload: Active Entity with name {entity_funnel_name} does not exist')

    entity_monitor = scope.entitymonitormapping_set.filter(entity=db_entity_funnel, is_active=True)
    entity_monitor = entity_monitor.prefetch_related('monitor').values('monitor_id',
                                                                       'monitor__primary_key__name',
                                                                       'monitor__primary_key__event_type_id',
                                                                       'monitor__primary_key__event_type__name',
                                                                       'monitor__secondary_key__event_type_id',
                                                                       'monitor__secondary_key__event_type__name')
    if not entity_monitor:
        raise EntityFunnelCrudIncorrectPayloadException(
            f'Incorrect Panel Payload: Entity Funnel Monitors not found for {entity_funnel_name}')

    if dtr.time_geq < db_entity_funnel.created_at:
        back_fill_job_config = getattr(settings, 'BACK_FILL_JOB_CONFIG', {})
        if back_fill_job_config and 'monitor_transaction' in back_fill_job_config and \
                back_fill_job_config['monitor_transaction'].get('enabled', False):
            entity_monitor_ids = [monitor['monitor_id'] for monitor in entity_monitor]
            kwargs = {'monitor_id__in': entity_monitor_ids}
            fargs = {'kwargs': kwargs}
            status_list = [PeriodicTaskStatus.FAILED, PeriodicTaskStatus.RUNNING, PeriodicTaskStatus.SCHEDULED]
            running_back_fill_tasks = get_task_run_for_task_account_status(
                task_name='back_fill_monitor_transaction_task',
                task_fargs=fargs,
                account=scope,
                status_list=status_list)
            if running_back_fill_tasks:
                raise EntityFunnelCrudIncorrectPayloadException(
                    f'Back Fill Monitor Transaction Tasks are running for {entity_funnel_name}')
        else:
            raise EntityFunnelCrudNotFoundException(
                f'Incorrect Payload: Time Range is less than Entity Funnel Creation Time')

    selected_drop_off_monitor = None
    for monitor in entity_monitor:
        if monitor['monitor__primary_key__event_type_id'] == start_event_type_id and \
                monitor['monitor__secondary_key__event_type_id'] == end_event_type_id:
            selected_drop_off_monitor = monitor
            break
    if not selected_drop_off_monitor:
        raise EntityFunnelCrudIncorrectPayloadException(
            f'Incorrect Panel Payload: Drop Off Monitor not found for {entity_funnel_name}')
    unique_transactions_set = None
    for idx, monitor in enumerate(entity_monitor):
        if idx <= 0:
            unique_transactions_set = MonitorTransactions.objects.filter(account_id=account_id).filter(
                monitor_id=monitor['monitor_id']).filter(
                event_type_id=monitor['monitor__primary_key__event_type_id'])
            unique_transactions_set = filter_dtr(unique_transactions_set, dtr, 'event_timestamp')
            if filter_key_name and filter_value:
                unique_transactions_set = unique_transactions_set.annotate(
                    event_attribute=F('event_processed_kvs__{}'.format(filter_key_name)))
                unique_transactions_set = unique_transactions_set.filter(event_attribute=filter_value)
            unique_transactions_set = unique_transactions_set.values_list('transaction', flat=True).distinct()
        else:
            unique_transactions_set = MonitorTransactions.objects.filter(account_id=account_id).filter(
                monitor_id=monitor['monitor_id']).filter(
                event_type_id=monitor['monitor__primary_key__event_type_id']).filter(
                transaction__in=unique_transactions_set)
            unique_transactions_set = unique_transactions_set.values_list('transaction', flat=True).distinct()

        if monitor['monitor_id'] == selected_drop_off_monitor['monitor_id']:
            break

    monitor_transactions_finished = MonitorTransactions.objects.filter(account_id=account_id).filter(
        monitor_id=selected_drop_off_monitor['monitor_id']).filter(
        event_type_id=selected_drop_off_monitor['monitor__secondary_key__event_type_id']).filter(
        transaction__in=unique_transactions_set).values_list('transaction', flat=True).distinct()

    start_event_type_event_count = unique_transactions_set.count()
    dropped_funnel_records = list(unique_transactions_set.difference(monitor_transactions_finished))
    if not dropped_funnel_records:
        return None
    else:
        dropped_funnel_records_str = ', '.join(f"'{x}'" for x in list(dropped_funnel_records))
        grouped_by_eventType_dropped_records = f"SELECT id, processed_kvs.{event_key_name} as p_e_id, " \
                                               f"event_type_id, event_type_name, ROW_NUMBER() OVER " \
                                               f"(PARTITION BY processed_kvs.{event_key_name} ORDER BY timestamp DESC) " \
                                               f"AS outer_row_num FROM (SELECT id, processed_kvs.{event_key_name}, " \
                                               f"event_type_id, event_type_name, timestamp FROM " \
                                               f"(SELECT id, processed_kvs.{event_key_name}, event_type_id, " \
                                               f"event_type_name, timestamp, ROW_NUMBER() OVER " \
                                               f"(PARTITION BY processed_kvs.{event_key_name}, event_type_name " \
                                               f"ORDER BY timestamp DESC) AS row_num FROM events where " \
                                               f"processed_kvs.{event_key_name} in ({dropped_funnel_records_str}) " \
                                               f"and timestamp >= '{dtr.to_tr_str()[0]}' and account_id = {account_id}) " \
                                               f"WHERE row_num = 1)"
        funnel_event_type_distribution = {}
        qs = Events.objects.raw(grouped_by_eventType_dropped_records)
        row = 0
        end_of_rows = False
        while row < len(qs):
            if end_of_rows:
                break
            curr_pkv_event_types = []
            start_event_type_id_found = False
            current_record_id = qs[row].p_e_id
            for i in range(row, len(qs)):
                if qs[i].p_e_id != current_record_id:
                    row = i
                    break
                if not start_event_type_id_found:
                    curr_pkv_event_types.append(qs[i].event_type_name)
                if qs[i].event_type_id == start_event_type_id:
                    start_event_type_id_found = True
                    if len(curr_pkv_event_types) > 0:
                        curr_pkv_event_types.reverse()
                        ev_type_key = curr_pkv_event_types[0]
                        if len(curr_pkv_event_types) > 1:
                            ev_type_key = ' -> '.join([str(ev_type) for ev_type in curr_pkv_event_types])
                        if ev_type_key in funnel_event_type_distribution:
                            funnel_event_type_distribution[ev_type_key] += 1
                        else:
                            funnel_event_type_distribution[ev_type_key] = 1
                if i >= len(qs) - 1:
                    end_of_rows = True
                    break
        return funnel_event_type_distribution, start_event_type_event_count


def entity_funnels_drop_off_download(scope: Account, dtr: DateTimeRange, entity_funnel_name: str, event_key_name,
                                     start_event_type_id, end_event_type_id, filter_key_name=None, filter_value=None):
    if not scope:
        raise EntityFunnelCrudIncorrectPayloadException(f'Incorrect Panel Payload: Missing Account')
    account_id = scope.id
    if not entity_funnel_name:
        raise EntityFunnelCrudIncorrectPayloadException(f'Incorrect Panel Payload: Missing Entity Funnel Name')

    try:
        db_entity_funnel = db_get_funnel_entity(scope,
                                                funnel_entity=EntityPartial(name=StringValue(value=entity_funnel_name)),
                                                is_active=True)
    except (EntityFunnelCrudIncorrectPayloadException, EntityFunnelCrudNotFoundException):
        raise EntityFunnelCrudNotFoundException(
            f'Incorrect Panel Payload: Active Entity with name {entity_funnel_name} does not exist')

    entity_monitor = scope.entitymonitormapping_set.filter(entity=db_entity_funnel, is_active=True)
    entity_monitor = entity_monitor.prefetch_related('monitor').values('monitor_id',
                                                                       'monitor__primary_key__name',
                                                                       'monitor__primary_key__event_type_id',
                                                                       'monitor__primary_key__event_type__name',
                                                                       'monitor__secondary_key__event_type_id',
                                                                       'monitor__secondary_key__event_type__name')
    if not entity_monitor:
        raise EntityFunnelCrudIncorrectPayloadException(
            f'Incorrect Panel Payload: Entity Funnel Monitors not found for {entity_funnel_name}')

    if dtr.time_geq < db_entity_funnel.created_at:
        back_fill_job_config = getattr(settings, 'BACK_FILL_JOB_CONFIG', {})
        if back_fill_job_config and 'monitor_transaction' in back_fill_job_config and \
                back_fill_job_config['monitor_transaction'].get('enabled', False):
            entity_monitor_ids = [monitor['monitor_id'] for monitor in entity_monitor]
            kwargs = {'monitor_id__in': entity_monitor_ids}
            fargs = {'kwargs': kwargs}
            status_list = [PeriodicTaskStatus.FAILED, PeriodicTaskStatus.RUNNING, PeriodicTaskStatus.SCHEDULED]
            running_back_fill_tasks = get_task_run_for_task_account_status(
                task_name='back_fill_monitor_transaction_task',
                task_fargs=fargs,
                account=scope,
                status_list=status_list)
            if running_back_fill_tasks:
                raise EntityFunnelCrudIncorrectPayloadException(
                    f'Back Fill Monitor Transaction Tasks are running for {entity_funnel_name}')
        else:
            raise EntityFunnelCrudNotFoundException(
                f'Incorrect Payload: Time Range is less than Entity Funnel Creation Time')

    selected_drop_off_monitor = None
    for monitor in entity_monitor:
        if monitor['monitor__primary_key__event_type_id'] == start_event_type_id and \
                monitor['monitor__secondary_key__event_type_id'] == end_event_type_id:
            selected_drop_off_monitor = monitor
            break
    if not selected_drop_off_monitor:
        raise EntityFunnelCrudIncorrectPayloadException(
            f'Incorrect Panel Payload: Drop Off Monitor not found for {entity_funnel_name}')
    unique_transactions_set = None
    for idx, monitor in enumerate(entity_monitor):
        if idx <= 0:
            unique_transactions_set = MonitorTransactions.objects.filter(account_id=account_id).filter(
                monitor_id=monitor['monitor_id']).filter(
                event_type_id=monitor['monitor__primary_key__event_type_id'])
            unique_transactions_set = filter_dtr(unique_transactions_set, dtr, 'event_timestamp')
            if filter_key_name and filter_value:
                unique_transactions_set = unique_transactions_set.annotate(
                    event_attribute=F('event_processed_kvs__{}'.format(filter_key_name)))
                unique_transactions_set = unique_transactions_set.filter(event_attribute=filter_value)
            unique_transactions_set = unique_transactions_set.values_list('transaction', flat=True).distinct()
        else:
            unique_transactions_set = MonitorTransactions.objects.filter(account_id=account_id).filter(
                monitor_id=monitor['monitor_id']).filter(
                event_type_id=monitor['monitor__primary_key__event_type_id']).filter(
                transaction__in=unique_transactions_set)
            unique_transactions_set = unique_transactions_set.values_list('transaction', flat=True).distinct()

        if monitor['monitor_id'] == selected_drop_off_monitor['monitor_id']:
            break

    monitor_transactions_finished = MonitorTransactions.objects.filter(account_id=account_id).filter(
        monitor_id=selected_drop_off_monitor['monitor_id']).filter(
        event_type_id=selected_drop_off_monitor['monitor__secondary_key__event_type_id']).filter(
        transaction__in=unique_transactions_set).values_list('transaction', flat=True).distinct()

    dropped_funnel_records = list(unique_transactions_set.difference(monitor_transactions_finished))
    if not dropped_funnel_records:
        return None
    else:
        dropped_funnel_records_str = ', '.join(f"'{x}'" for x in list(dropped_funnel_records))
        grouped_by_eventType_dropped_records = f"SELECT id, processed_kvs.{event_key_name} as p_e_id, " \
                                               f"event_type_id, event_type_name, ROW_NUMBER() OVER " \
                                               f"(PARTITION BY processed_kvs.{event_key_name} ORDER BY timestamp DESC) " \
                                               f"AS outer_row_num FROM (SELECT id, processed_kvs.{event_key_name}, " \
                                               f"event_type_id, event_type_name, timestamp FROM " \
                                               f"(SELECT id, processed_kvs.{event_key_name}, event_type_id, " \
                                               f"event_type_name, timestamp, ROW_NUMBER() OVER " \
                                               f"(PARTITION BY processed_kvs.{event_key_name}, event_type_name " \
                                               f"ORDER BY timestamp DESC) AS row_num FROM events where " \
                                               f"processed_kvs.{event_key_name} in ({dropped_funnel_records_str}) " \
                                               f"and timestamp >= '{dtr.to_tr_str()[0]}' and account_id = {account_id}) " \
                                               f"WHERE row_num = 1)"
        qs = Events.objects.raw(grouped_by_eventType_dropped_records)
        csv_data = [[event_key_name, 'path']]
        row = 0
        end_of_rows = False
        while row < len(qs):
            if end_of_rows:
                break
            curr_pkv_event_types = []
            start_event_type_id_found = False
            current_record_id = qs[row].p_e_id
            for i in range(row, len(qs)):
                if qs[i].p_e_id != current_record_id:
                    row = i
                    break
                if not start_event_type_id_found:
                    curr_pkv_event_types.append(qs[i].event_type_name)
                if qs[i].event_type_id == start_event_type_id:
                    start_event_type_id_found = True
                    if len(curr_pkv_event_types) > 0:
                        curr_pkv_event_types.reverse()
                        ev_type_key = curr_pkv_event_types[0]
                        if len(curr_pkv_event_types) > 1:
                            ev_type_key = ' -> '.join([str(ev_type) for ev_type in curr_pkv_event_types])
                        csv_data.append([current_record_id, ev_type_key])
                if i >= len(qs) - 1:
                    end_of_rows = True
                    break
        return csv_data
