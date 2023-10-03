BAD_METRICS = ['error', 'latency', 'duration', 'memory', 'cpu', 'failure']
GOOD_METRICS = ['count', 'throughput', 'hit', 'success']
AGGR_MAP = {'count': 'count({})', 'avg': 'avg({})', 'sum': 'sum({})', 'min': 'min({})', 'max': 'max({})',
            'count_distinct': 'count(distinct {})', 'distinct_count': 'count(distinct {})'}
AGGR_FUNCTION_MAP = {'count': 'COUNT', 'avg': 'AVG', 'sum': 'SUM', 'min': 'MIN', 'max': 'MAX',
            'count_distinct': 'COUNT_DISTINCT', 'distinct_count': 'COUNT_DISTINCT'}


def get_metric_key_context(key):
    for m in BAD_METRICS:
        if m in key.lower():
            return 'down'
    for m in GOOD_METRICS:
        if m in key.lower():
            return 'up'
    return 'up'


def get_metric_aggr_function_mapping(aggr):
    return AGGR_FUNCTION_MAP.get(aggr, 'COUNT')


def get_event_metric_expr_query(aggr_type, aggr_field, filters, account_id, dtr):
    start_time, end_time = dtr.to_tr_str()

    selector = 'count(id)'
    if '.' in aggr_field and aggr_field.split('.')[0] == 'event' and aggr_field.split('.')[1]:
        selector = AGGR_MAP.get(aggr_type, 'count({})').format('processed_kvs.{}'.format(aggr_field.split('.')[1]))

    q_filter = 'account_id = {}'.format(account_id)
    for f in filters:
        if f['lhs'] == 'event_name':
            q_filter += ' and event_type_name = \'{}\''.format(f['rhs'])
        else:
            q_filter += ' and processed_kvs.{} = \'{}\''.format(f['lhs'], f['rhs'])
    q_filter = q_filter + ' and '

    query = "select {} as id from events where {} timestamp between '{}' and '{}'".format(selector, q_filter, start_time,
                                                                                    end_time)
    return query


def get_transaction_metric_expr_query(aggr_type, aggr_field, filters, account_id, dtr):
    start_time, end_time = dtr.to_tr_str()

    metric_type = aggr_field.split('.')[1]
    metric_object = aggr_field.split('.')[0]
    primary_event_name = list(filter(lambda x: x['lhs'] == 'primary_event_name', filters))[0]['rhs']
    secondary_event_name = list(filter(lambda x: x['lhs'] == 'secondary_event_name', filters))[0]['rhs']
    joining_key = list(filter(lambda x: x['lhs'] == 'joining_key', filters))[0]['rhs']

    filter_clause = ''
    event_filters = list(filter(lambda x: x['lhs'] != 'primary_event_name' and x['lhs'] != 'secondary_event_name' and x['lhs'] != 'joining_key', filters))
    for f in event_filters:
        filter_clause += ' and processed_kvs.{} = \'{}\''.format(f['lhs'], f['rhs'])

    query = None
    if aggr_type == 'percent':
        if metric_type == 'active':
            query = "select (1 - count(distinct B.s_j_key) / count(distinct A.p_j_key))*100 as id from (select processed_kvs.{} as p_j_key from events where account_id = {} and event_type_name = '{}' and timestamp between '{}' and '{}' {}) A left join (select processed_kvs.{} as s_j_key from events where account_id = {} and event_type_name = '{}' and timestamp >= '{}') B on A.p_j_key = B.s_j_key".format(
                joining_key, account_id, primary_event_name, start_time, end_time, filter_clause, joining_key, account_id, secondary_event_name, start_time
            )
        if metric_type == 'finished':
            query = "select count(distinct B.s_j_key) * 100 / count(distinct A.p_j_key) as id from (select processed_kvs.{} as p_j_key from events where account_id = {} and event_type_name = '{}' and timestamp between '{}' and '{}' {}) A left join (select processed_kvs.{} as s_j_key from events where account_id = {} and event_type_name = '{}' and timestamp >= '{}') B on A.p_j_key = B.s_j_key".format(
                joining_key, account_id, primary_event_name, start_time, end_time, filter_clause, joining_key, account_id, secondary_event_name, start_time
            )

    if aggr_type == 'avg':
        if metric_type == 'time':
            query = "select avg(date_diff('ms', p_timestamp, s_timestamp)) as id from (select processed_kvs.{} as p_j_key, timestamp as p_timestamp from events where account_id = {} and event_type_name = '{}' and timestamp between '{}' and '{}' {}) A left join (select processed_kvs.{} as s_j_key, timestamp as s_timestamp from events where account_id = {} and event_type_name = '{}' and timestamp >= '{}') B on A.p_j_key = B.s_j_key where A.p_j_key = B.s_j_key".format(
                joining_key, account_id, primary_event_name, start_time, end_time, filter_clause, joining_key, account_id, secondary_event_name, start_time
            )

    return query