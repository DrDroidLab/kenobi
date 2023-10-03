from django.db import transaction as dj_transaction
from django.db.models import Avg, Count, F
from google.protobuf.wrappers_pb2 import UInt64Value, StringValue

from accounts.models import Account
from event.cache import GLOBAL_PANEL_CACHE
from event.clickhouse.models import MonitorTransactions, Events
from event.models import Entity, EntityEventKeyMapping, EntityMonitorMapping
from event.monitors_crud import create_monitors
from event.workflows.funnel import Funnel
from protos.event.entity_pb2 import EntityPartial, Entity as EntityProto, WorkflowView
from protos.event.panel_pb2 import FunnelPanel, PanelV1, PanelData
from protos.event.monitor_pb2 import MonitorTransaction as MonitorTransactionProto
from prototype.utils.timerange import DateTimeRange, filter_dtr
from utils.proto_utils import proto_to_dict, dict_to_proto


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
        print(str(e))
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
            db_monitor, created, error = create_monitors(scope, monitor_name, primary_event_key_id,
                                                         secondary_event_key_id,
                                                         is_generated=True)
            if not db_monitor and error:
                raise EntityFunnelCrudIncorrectPayloadException(f'Error Creating Entity Funnel: {error}')
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
    return e


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
        db_entity_funnel = db_save_entity_funnel(scope, entity_funnel_name, event_keys.values_list('id', flat=True),
                                                 event_key_tuples)
        return db_entity_funnel, None
    except Exception as e:
        return None, f'Incorrect Payload: Unable to save Entity Funnel in DB'


def entity_funnels_get_clickhouse_events(account, dtr, entity_funnel_name, filter_key_name=None, filter_value=None):
    panels = GLOBAL_PANEL_CACHE.get(account_id=account.id, name=entity_funnel_name)
    panel_proto: PanelV1 = dict_to_proto(panels[0], PanelV1)
    panel_data = panel_proto.data
    if panel_data.type != PanelData.PanelDataType.FUNNEL or panel_data.funnel is None:
        raise EntityFunnelCrudIncorrectPayloadException(f'Incorrect Panel Payload: Panel Data Type is not Funnel')
    funnel = panel_data.funnel
    event_key_name = funnel.event_key_name
    funnel_event_type_ids = funnel.event_type_ids
    if not filter_key_name or not filter_value:
        filter_key_name = funnel.filter_key_name
        filter_value = funnel.filter_value
    funnel_event_type_ids_str = ','.join([str(e) for e in funnel_event_type_ids])
    dtr_geq = dtr.to_tr_str()[0]
    dtr_lt = dtr.to_tr_str()[1]
    events_group_query = f"select groupArray(id) as id, groupArray(event_type_id) as event_type_id_group, " \
                         f"groupArray(event_type_name) as event_type_name_group, " \
                         f"groupArray(timestamp) as timestamp_group, e_id from " \
                         f"(select id, event_type_id, event_type_name, timestamp, " \
                         f"processed_kvs.{event_key_name} as e_id from events where " \
                         f"event_type_id in ({funnel_event_type_ids_str}) and account_id = {account.id} and " \
                         f"timestamp between '{dtr_geq}' and '{dtr_lt}' and processed_kvs.{event_key_name} in " \
                         f"(select distinct processed_kvs.{event_key_name} from events where " \
                         f"event_type_id = {funnel_event_type_ids[0]} and account_id = {account.id} and " \
                         f"timestamp between '{dtr_geq}' and '{dtr_lt}') " \
                         f"order by timestamp asc, created_at asc) group by e_id;"

    if filter_key_name and filter_value:
        events_group_query = f"select groupArray(id) as id, groupArray(event_type_id) as event_type_id_group, " \
                             f"groupArray(event_type_name) as event_type_name_group, " \
                             f"groupArray(timestamp) as timestamp_group, groupArray(e_filter_value) as filter_group, " \
                             f"e_id from (select id, event_type_id, event_type_name, timestamp, " \
                             f"processed_kvs.{event_key_name} as e_id, " \
                             f"processed_kvs.{filter_key_name} as e_filter_value from events where " \
                             f"event_type_id in ({funnel_event_type_ids_str}) and account_id = {account.id} and " \
                             f"timestamp between '{dtr_geq}' and '{dtr_lt}' and processed_kvs.{event_key_name} in " \
                             f"(select distinct processed_kvs.{event_key_name} from events where " \
                             f"event_type_id = {funnel_event_type_ids[0]} and account_id = {account.id} and " \
                             f"timestamp between '{dtr_geq}' and '{dtr_lt}') " \
                             f"order by timestamp asc, created_at asc) group by e_id;"

    qs = Events.objects.raw(events_group_query)
    events_group_set = list(qs)

    f = Funnel()

    for grouped_event in events_group_set:
        f.add_to_node_map(grouped_event, filter_key_name=filter_key_name, filter_value=filter_value)

    ordered_funnel_data = f.get_ordered_funnel_data(funnel_event_type_ids)
    return ordered_funnel_data


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

    entity_monitor = scope.entitymonitormapping_set.filter(entity=db_entity_funnel, is_active=True, is_generated=True)
    entity_monitor = entity_monitor.prefetch_related('monitor').values('monitor_id',
                                                                       'monitor__primary_key__name',
                                                                       'monitor__primary_key__event_type_id',
                                                                       'monitor__primary_key__event_type__name',
                                                                       'monitor__secondary_key__event_type_id',
                                                                       'monitor__secondary_key__event_type__name')
    if not entity_monitor:
        raise EntityFunnelCrudIncorrectPayloadException(
            f'Incorrect Panel Payload: Entity Funnel Monitors not found for {entity_funnel_name}')
    entity_monitor_ids = [monitor['monitor_id'] for monitor in entity_monitor]

    head_monitor = entity_monitor[0]
    unique_transactions = MonitorTransactions.objects.filter(account_id=account_id).filter(
        monitor_id=head_monitor['monitor_id']).filter(event_type_id=head_monitor['monitor__primary_key__event_type_id'])
    unique_transactions = filter_dtr(unique_transactions, dtr, 'event_timestamp')
    if filter_key_name and filter_value:
        unique_transactions = unique_transactions.annotate(
            event_attribute=F('event_processed_kvs__{}'.format(filter_key_name)))
        unique_transactions = unique_transactions.filter(event_attribute=filter_value)
    unique_transactions = unique_transactions.values_list('transaction', flat=True).distinct()

    monitor_transactions = MonitorTransactions.objects.filter(account_id=account_id).filter(
        event_timestamp__gte=dtr.time_geq).filter(monitor_id__in=entity_monitor_ids).filter(
        monitor_transaction_event_type=MonitorTransactionProto.MonitorTransactionEventType.PRIMARY).filter(
        transaction__in=unique_transactions).values('monitor_id').annotate(
        transaction_count=Count('transaction', distinct=True))

    monitor_transactions_finished = MonitorTransactions.objects.filter(account_id=account_id).filter(
        event_timestamp__gte=dtr.time_geq).filter(monitor_id__in=entity_monitor_ids).filter(
        monitor_transaction_event_type=MonitorTransactionProto.MonitorTransactionEventType.SECONDARY).filter(
        transaction__in=unique_transactions).values('monitor_id').annotate(
        avg_duration=Avg('transaction_time')).annotate(completed_transaction_count=Count('transaction', distinct=True))

    monitor_transactions_count = {item['monitor_id']: item['transaction_count'] for item in monitor_transactions}
    monitor_transactions_finished_count = {
        item['monitor_id']: {'completed_transaction_count': item['completed_transaction_count'],
                             'avg_duration': item['avg_duration']} for item in monitor_transactions_finished}
    data = []
    links = []
    node_map = {}
    edge_map = {}
    start_conn_types = [WorkflowView.NodeConnectionType.OUT]
    mid_conn_types = [WorkflowView.NodeConnectionType.IN, WorkflowView.NodeConnectionType.OUT]
    end_conn_types = [WorkflowView.NodeConnectionType.IN]
    for idx, monitor in enumerate(entity_monitor):
        monitor_id = monitor['monitor_id']

        primary_node_transaction_count = monitor_transactions_count.get(monitor_id, 0)
        secondary_node_transaction_count = 0
        avg_duration = 0
        monitor_transactions_finished_stats = monitor_transactions_finished_count.get(monitor_id, {})
        if monitor_transactions_finished_stats:
            secondary_node_transaction_count = monitor_transactions_finished_stats.get('completed_transaction_count', 0)
            avg_duration = monitor_transactions_finished_stats.get('avg_duration', 0)

        primary_conn_types = mid_conn_types
        secondary_conn_types = mid_conn_types
        if len(data) == 0:
            primary_conn_types = start_conn_types
        elif idx >= len(entity_monitor) - 1:
            secondary_conn_types = end_conn_types

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
        if primary_node_transaction_count > 0 and secondary_node_transaction_count > 0:
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
