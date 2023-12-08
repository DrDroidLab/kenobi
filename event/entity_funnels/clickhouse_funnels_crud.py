from accounts.models import Account
from event.cache import GLOBAL_PANEL_CACHE
from event.clickhouse.models import Events
from event.entity_funnels.entity_funnels_crud import EntityFunnelCrudIncorrectPayloadException
from event.workflows.funnel import Funnel
from protos.event.entity_pb2 import WorkflowView
from protos.event.panel_pb2 import PanelV1, PanelData
from utils.proto_utils import dict_to_proto

start_node_conn_types = [WorkflowView.NodeConnectionType.OUT]
mid_node_conn_types = [WorkflowView.NodeConnectionType.IN, WorkflowView.NodeConnectionType.OUT]
end_node_conn_types = [WorkflowView.NodeConnectionType.IN]


def get_funnel_panel_data(account: Account, entity_funnel_name: str, filter_key_name: str = None,
                          filter_value: str = None):
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

    return funnel_event_type_ids, event_key_name, filter_key_name, filter_value


def generate_funnel(account, dtr, funnel_event_type_ids, event_key_name, filter_key_name=None, filter_value=None):
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

    funnel = Funnel()

    for grouped_event in events_group_set:
        funnel.add_to_node_map(grouped_event, filter_key_name=filter_key_name, filter_value=filter_value)

    return funnel


def entity_funnels_get_clickhouse_events(account, dtr, funnel_event_type_ids, event_key_name, filter_key_name=None,
                                         filter_value=None):
    funnel = generate_funnel(account, dtr, funnel_event_type_ids, event_key_name, filter_key_name, filter_value)
    ordered_funnel_data = funnel.get_ordered_funnel_data(funnel_event_type_ids)

    return ordered_funnel_data


def entity_funnels_get_clickhouse_drop_off_distribution(account, dtr, funnel_event_type_ids, event_key_name,
                                                        start_event_type_id, end_event_type_id,
                                                        filter_key_name=None, filter_value=None):
    funnel = generate_funnel(account, dtr, funnel_event_type_ids, event_key_name, filter_key_name, filter_value)

    dropped_funnel_records, start_event_type_event_count = funnel.get_funnel_drop_records(funnel_event_type_ids,
                                                                                          start_event_type_id,
                                                                                          end_event_type_id)
    if not dropped_funnel_records:
        return [], len(start_event_type_event_count)
    else:
        dropped_funnel_records_str = ', '.join(f"'{x}'" for x in list(dropped_funnel_records))
        grouped_by_eventType_dropped_records = f"SELECT id, processed_kvs.{event_key_name} as p_e_id, event_type_id, event_type_name, ROW_NUMBER() OVER (PARTITION BY processed_kvs.{event_key_name} ORDER BY timestamp DESC) AS outer_row_num FROM (SELECT id, processed_kvs.{event_key_name}, event_type_id, event_type_name, timestamp FROM (SELECT id, processed_kvs.{event_key_name}, event_type_id, event_type_name, timestamp, ROW_NUMBER() OVER (PARTITION BY processed_kvs.{event_key_name}, event_type_name ORDER BY timestamp DESC) AS row_num FROM events where processed_kvs.{event_key_name} in ({dropped_funnel_records_str}) and timestamp >= '{dtr.to_tr_str()[0]}' and account_id = {account.id}) WHERE row_num = 1)"
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
        return funnel_event_type_distribution, len(start_event_type_event_count)


def entity_funnels_get_clickhouse_drop_off_distribution_download(account, dtr, funnel_event_type_ids, event_key_name,
                                                                 start_event_type_id, end_event_type_id,
                                                                 filter_key_name=None,
                                                                 filter_value=None):
    funnel = generate_funnel(account, dtr, funnel_event_type_ids, event_key_name, filter_key_name, filter_value)

    dropped_funnel_records, start_event_type_event_count = funnel.get_funnel_drop_records(funnel_event_type_ids,
                                                                                          start_event_type_id,
                                                                                          end_event_type_id)
    if not dropped_funnel_records:
        return None
    else:
        dropped_funnel_records_str = ', '.join(f"'{x}'" for x in list(dropped_funnel_records))
        grouped_by_eventType_dropped_records = f"SELECT id, processed_kvs.{event_key_name} as p_e_id, event_type_id, event_type_name, ROW_NUMBER() OVER (PARTITION BY processed_kvs.{event_key_name} ORDER BY timestamp DESC) AS outer_row_num FROM (SELECT id, processed_kvs.{event_key_name}, event_type_id, event_type_name, timestamp FROM (SELECT id, processed_kvs.{event_key_name}, event_type_id, event_type_name, timestamp, ROW_NUMBER() OVER (PARTITION BY processed_kvs.{event_key_name}, event_type_name ORDER BY timestamp DESC) AS row_num FROM events where processed_kvs.{event_key_name} in ({dropped_funnel_records_str}) and timestamp >= '{dtr.to_tr_str()[0]}' and account_id = {account.id}) WHERE row_num = 1)"
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
