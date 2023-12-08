import math
from typing import List

from event.clickhouse.models import Events
from event.engine.context import get_context_resolver
from event.models import EventType
from event.workflows.workflow_utils import get_metric_aggr_function_mapping
from protos.event.base_pb2 import Context
from protos.event.literal_pb2 import IdLiteral, LiteralType
from protos.event.metric_pb2 import MetricExpression
from prototype.utils.timerange import DateTimeRange
from utils.proto_utils import dict_to_proto


class MetricEngine:
    def process(self, account, context: Context, expressions: List[MetricExpression], dtr: DateTimeRange):
        if context == Context.EVENT:
            context = Context.EVENTS_CLICKHOUSE

        context_resolver = get_context_resolver(context)
        if context_resolver is None:
            raise Exception(f'invalid context: {context}')

        qs = context_resolver.qs(account)
        evaluator = context_resolver.metric_expression_evaluator()
        return evaluator.process_batch(qs, expressions, dtr)

    def get_options(self, account, context: Context, id: IdLiteral = None):
        context_resolver = get_context_resolver(context)
        if context_resolver is None:
            raise Exception(f'invalid context: {context}')
        parent_obj = context_resolver.get_parent_obj(account, id)
        return context_resolver.get_metric_options(account, parent_obj)

    def get_default_metric_expression(self, account, context: Context, id: IdLiteral = None):
        context_resolver = get_context_resolver(context)
        if context_resolver is None:
            raise Exception(f'invalid context: {context}')
        return context_resolver.get_default_metric_expression(account, id)


metric_engine = MetricEngine()


def process_workflow_monitor_metric_expression(account, metric_expr, dtr: DateTimeRange):
    start_time, end_time = dtr.to_tr_str()
    metric_timeseries_data = []

    tr = dtr.to_tr()
    time_duration = tr.time_lt - tr.time_geq
    account_id = account.id

    aggr_field = metric_expr.split(':')[1].split('{')[0]
    filters = list(
        {'lhs': x.split(':')[0], 'rhs': x.split(':')[1]} for x in metric_expr.split('{')[1].split('}')[0].split(','))

    resolution = math.ceil(time_duration / 15 / 60)

    aggr_type = metric_expr.split(':')[0]
    metric_type = aggr_field.split('.')[1]
    primary_event_name = list(filter(lambda x: x['lhs'] == 'primary_event_name', filters))[0]['rhs']
    secondary_event_name = list(filter(lambda x: x['lhs'] == 'secondary_event_name', filters))[0]['rhs']
    joining_key = list(filter(lambda x: x['lhs'] == 'joining_key', filters))[0]['rhs']

    filter_clause = ''
    event_filters = list(filter(
        lambda x: x['lhs'] != 'primary_event_name' and x['lhs'] != 'secondary_event_name' and x['lhs'] != 'joining_key',
        filters))
    for f in event_filters:
        filter_clause += ' and processed_kvs.{} = \'{}\''.format(f['lhs'], f['rhs'])

    query = None
    if aggr_type == 'percent':
        if metric_type == 'active':
            query = "SELECT toStartOfInterval(C.p_timestamp, INTERVAL {} minute) AS interval_start, (SUM(C.result) * 100.0 / COUNT(*)) AS id FROM (select IF(A.p_j_key = B.s_j_key, 0, IF(A.p_j_key != B.s_j_key, 1, 0)) AS result, A.p_timestamp from (select processed_kvs.{} as p_j_key, timestamp as p_timestamp from events where account_id = {} and event_type_name = '{}' and timestamp between '{}' and '{}' {}) A left join (select processed_kvs.{} as s_j_key from events where account_id = {} and event_type_name = '{}' and timestamp >= '{}') B on A.p_j_key = B.s_j_key) C GROUP BY interval_start ORDER BY interval_start".format(
                resolution, joining_key, account_id, primary_event_name, start_time, end_time, filter_clause,
                joining_key,
                account_id, secondary_event_name, start_time
            )
        if metric_type == 'finished':
            query = "SELECT toStartOfInterval(C.p_timestamp, INTERVAL {} minute) AS interval_start, (SUM(C.result) * 100.0 / COUNT(*)) AS id FROM (select IF(A.p_j_key = B.s_j_key, 1, IF(A.p_j_key != B.s_j_key, 0, 0)) AS result, A.p_timestamp from (select processed_kvs.{} as p_j_key, timestamp as p_timestamp from events where account_id = {} and event_type_name = '{}' and timestamp between '{}' and '{}' {}) A left join (select processed_kvs.{} as s_j_key from events where account_id = {} and event_type_name = '{}' and timestamp >= '{}') B on A.p_j_key = B.s_j_key) C GROUP BY interval_start ORDER BY interval_start".format(
                resolution, joining_key, account_id, primary_event_name, start_time, end_time, filter_clause,
                joining_key,
                account_id, secondary_event_name, start_time
            )

    if aggr_type == 'avg':
        if metric_type == 'time':
            query = "SELECT toStartOfInterval(C.p_timestamp, INTERVAL {} minute) AS interval_start, avg(id) as id FROM (select date_diff('ms', p_timestamp, s_timestamp) as id, p_timestamp  from (select processed_kvs.{} as p_j_key, timestamp as p_timestamp from events where account_id = {} and event_type_name = '{}' and timestamp between '{}' and '{}' {}) A left join (select processed_kvs.{} as s_j_key, timestamp as s_timestamp from events where account_id = {} and event_type_name = '{}' and timestamp >= '{}') B on A.p_j_key = B.s_j_key where A.p_j_key = B.s_j_key) C GROUP BY interval_start ORDER BY interval_start".format(
                resolution, joining_key, account_id, primary_event_name, start_time, end_time, filter_clause,
                joining_key,
                account_id, secondary_event_name, start_time
            )

    qs = Events.objects.raw(query)
    metric_data = list(qs)

    for d in metric_data:
        metric_timeseries_data.append({
            'timestamp': int(d.interval_start.timestamp() * 1000),
            'value': d.id
        })
    return metric_timeseries_data


def process_workflow_metric_expression(account, metric_expr, dtr: DateTimeRange):
    tr = dtr.to_tr()
    time_duration = tr.time_lt - tr.time_geq

    aggregation_type = metric_expr.split(':')[0]
    aggregation_field = metric_expr.split(':')[1].split('{')[0]
    metric_context = metric_expr.split('{')[0].split(':')[1].split('.')[0].upper()
    aggregation_object = aggregation_field.split('.')[0]
    filters = []
    selectors = []
    resolution = math.ceil(time_duration / 15 / 60) * 60

    if aggregation_object == 'transaction':
        return process_workflow_monitor_metric_expression(account, metric_expr, dtr)

    for token in metric_expr.split('{')[1].split('}')[0].split(','):
        filter_lhs = token.split(':')[0]
        filter_rhs = token.split(':')[1]

        if filter_lhs == 'event_name':
            event_type = EventType.objects.filter(account=account, name=filter_rhs).first()
            filters.append({
                "lhs": {
                    "column_identifier": {
                        "name": "event_type_id"
                    }
                },
                "op": "EQ",
                "rhs": {
                    "literal": {
                        "literal_type": "ID",
                        "id": {
                            "type": "LONG",
                            "long": event_type.id
                        }
                    }
                }
            })
        else:
            filters.append({
                "lhs": {
                    {
                        "attribute_identifier": {
                            "name": filter_lhs,
                            "path": "event_attribute"
                        }
                    }
                },
                "op": "EQ",
                "rhs": {
                    "literal": {
                        "literal_type": "STRING",
                        "string": filter_rhs
                    }
                }
            })

    if '.' in aggregation_field and aggregation_field.split('.')[0] == 'event' and aggregation_field.split('.')[1]:
        selectors.append({
            "function": get_metric_aggr_function_mapping(aggregation_type),
            "expression": {
                "attribute_identifier": {
                    "name": aggregation_field.split('.')[1],
                    "path": "event_attribute"
                }
            }
        })
    else:
        selectors.append({
            "function": get_metric_aggr_function_mapping(aggregation_type),
            "expression": {
                "column_identifier": {
                    "name": "event_type_id"
                }
            }
        })

    expression = {
        "filter": {
            "op": "AND",
            "filters": filters
        },
        "selectors": selectors,
        "resolution": resolution,
        "is_timeseries": True,
    }

    expr = dict_to_proto(expression, MetricExpression)

    context = Context.EVENT
    if metric_context == 'monitor':
        context = Context.MONITOR_TRANSACTION

    metric_data = metric_engine.process(account, context, [expr], dtr)
    timeseries_data = metric_data[0].labeled_data[0].alias_data_map['metric_1'].timeseries_data

    metric_timeseries_data = []
    for ts_data in timeseries_data:
        metric_value = None
        if get_literal_value(ts_data.value):
            metric_value = float(get_literal_value(ts_data.value).value)

        metric_timeseries_data.append({
            'timestamp': ts_data.timestamp * 1000,
            'value': metric_value
        })

    return metric_timeseries_data


def get_literal_value(literal):
    literal_type = literal.literal_type
    if literal_type == LiteralType.LONG:
        return literal.long
    if literal_type == LiteralType.DOUBLE:
        return literal.double
    return None


def process_metric_expressions(account, context: Context, expressions: List[MetricExpression], dtr: DateTimeRange):
    return metric_engine.process(account, context, expressions, dtr)


def get_metric_options(account, context: Context, id: IdLiteral = None):
    return metric_engine.get_options(account, context, id)


def get_default_metric_expression(account, context: Context, id: IdLiteral = None):
    return metric_engine.get_default_metric_expression(account, context, id)
