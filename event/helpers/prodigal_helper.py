from datetime import datetime, timedelta, timezone

def append_metrics(metric_object, event_count_object):
    event_name_metric_name_map = {
        'p1-error': 'P1 Error',
        "p1-success": 'Metadata received',
        "p1-failed": 'Metadata received',
        'p2-audioReceived': 'Audio files received',
        'p2-success':   'Matched Records',
        'p3-filteredRecord':  'Filtered Records',
        'p6-success': 'Ingested Records',
        'publish-end': 'Published Records'
    }

    metric_array = metric_object['record_count_metrics']
    if event_count_object['event_type_name'] in event_name_metric_name_map:
        metric_name = event_name_metric_name_map[event_count_object['event_type_name']]
        for metric in metric_array:
            if metric['metric_name'] == metric_name:
                metric['metric_value'] = metric['metric_value'] + int(event_count_object['record_count'])
                metric['event_type_ids'].append(event_count_object['event_type_id'])

    for metric in metric_array:
        event_type_ids_str = '['
        event_type_ids_str_tokens = []
        for e_type_id in metric['event_type_ids']:
            event_type_ids_str_tokens.append('{"type": "LONG", "long": "' + str(e_type_id) + '"}')
        event_type_ids_str += ",".join(event_type_ids_str_tokens) + ']'
        metric['filter_query'] = '[{"op":"EQ","lhs":{"attribute_identifier":{"name":"tenantId","path":"event_attribute","type":"STRING"}},"rhs":{"literal":{"literal_type":"STRING","string":"' + metric_object['tenantId'] + '"}}},{"op":"EQ","lhs":{"attribute_identifier":{"name":"connectorId","path":"event_attribute","type":"STRING"}},"rhs":{"literal":{"literal_type":"STRING","string":"' + metric_object['connectorId'] + '"}}},{"op":"EQ","lhs":{"attribute_identifier":{"name":"integrationType","path":"event_attribute","type":"STRING"}},"rhs":{"literal":{"literal_type":"STRING","string":"' + metric_object['integrationType'] + '"}}},{"op":"IN","lhs":{"column_identifier":{"name":"event_type_id","type":"ID"}},"rhs":{"literal":{"literal_type":"ID_ARRAY","id_array":' + event_type_ids_str + '}}}]'


def get_timestamp_utc(timestamp_str):
    if not timestamp_str:
        return None

    if len(timestamp_str) == 3:
        hours = int(timestamp_str[0])
        minutes = int(timestamp_str[1:])
    elif len(timestamp_str) == 4:
        hours = int(timestamp_str[:2])
        minutes = int(timestamp_str[2:])
    else:
        return None

    now_utc = datetime.now(tz=timezone.utc)
    desired_time = now_utc.replace(hour=hours, minute=minutes, second=0, microsecond=0)

    return desired_time