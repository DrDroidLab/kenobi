from abc import abstractmethod

from google.protobuf.wrappers_pb2 import UInt64Value, BoolValue

from event.clickhouse.models import Events
from accounts.models import Account
from event.base.aggregation_function import get_metric_aggregation_function_options
from event.base.filter_token import FilterEngine
from event.base.metric_token import MetricExpressionEvaluator
from event.base.order_by_token import OrderByEngine
from event.engine.model_columns import ColumnOptions, event_columns, monitor_transaction_columns, \
    entity_instance_columns, events_clickhouse_columns
from event.models import Monitor, EventType, Entity
from protos.event.base_pb2 import Context
from protos.event.engine_options_pb2 import MetricOptions, QueryOptions, QueryOptionsV2
from protos.event.literal_pb2 import IdLiteral, Literal, LiteralType
from protos.event.metric_pb2 import MetricExpression, MetricSelector, AggregationFunction
from protos.event.query_base_pb2 import QueryRequest, Filter, Expression, Op, ColumnIdentifier, OrderByExpression, \
    SortOrder


class ContextResolver:
    columns = None
    timestamp_field = None
    parent_model = None
    parent_column_name: str = None

    def __init__(self):
        self._filter_engine = FilterEngine(self.columns)
        self._order_by_engine = OrderByEngine(self.columns, default_order_expression=OrderByExpression(
            expression=Expression(column_identifier=ColumnIdentifier(name=self.timestamp_field)),
            order=SortOrder.DESC))
        self._metric_expression_evaluator = MetricExpressionEvaluator(
            self.parent_model, self.columns, self.timestamp_field
        )
        self._column_options = ColumnOptions(self.columns)

    @abstractmethod
    def qs(self, account):
        raise NotImplementedError()

    def filter_engine(self):
        return self._filter_engine

    def order_by_engine(self):
        return self._order_by_engine

    def metric_expression_evaluator(self) -> MetricExpressionEvaluator:
        return self._metric_expression_evaluator

    def get_parent_obj(self, account, id: IdLiteral = None):
        if id.type == IdLiteral.Type.LONG:
            return self.parent_model.objects.get(account=account, id=id.long.value)
        elif id.type == IdLiteral.Type.STRING:
            return id.string.value

    def get_search_options(self, account, parent_obj=None):
        column_options, attribute_options = self._column_options.options(account=account, obj=parent_obj)

        return QueryOptions(column_options=column_options, attribute_options=attribute_options)

    def get_search_options_v2(self, account, parent_obj=None):
        column_options, attribute_options_v2 = self._column_options.options_v2(account=account, obj=parent_obj)

        return QueryOptionsV2(column_options=column_options, attribute_options_v2=attribute_options_v2)

    def get_metric_options(self, account, parent_obj=None):
        column_options, attribute_options = self._column_options.options(account=account, obj=parent_obj)
        return MetricOptions(
            aggregation_function_options=get_metric_aggregation_function_options(),
            column_options=column_options,
            attribute_options=attribute_options
        )

    def get_parent_id_filter(self, id: IdLiteral = None):
        return Filter(
            lhs=Expression(column_identifier=ColumnIdentifier(name=self.parent_column_name, type=LiteralType.ID)),
            op=Op.EQ,
            rhs=Expression(
                literal=Literal(
                    literal_type=LiteralType.ID,
                    id=id
                )
            )
        )

    def get_default_metric_expression(self, account, id: IdLiteral = None):
        parent_id_filter = None
        if id is not None and id.ByteSize() != 0:
            parent_id_filter = self.get_parent_id_filter(id)

        return MetricExpression(
            filter=parent_id_filter,
            selectors=[
                MetricSelector(
                    function=AggregationFunction.COUNT,
                )
            ],
            is_timeseries=BoolValue(value=True),
            resolution=UInt64Value(value=10),
        )

    def get_default_query(self, account, obj=None):
        return QueryRequest()


class EventContextResolver(ContextResolver):
    columns = event_columns
    timestamp_field = 'timestamp'
    parent_model = EventType
    parent_column_name = 'event_type_id'

    def qs(self, account):
        return account.event_set.all()

    def get_default_query(self, account, obj=None):
        if type(account) is not Account:
            raise ValueError(f'{account} needs to be Account')

        return QueryRequest(filter=Filter(op=Op.AND, filters=[]))


class EventsClickhouseContextResolver(ContextResolver):
    columns = events_clickhouse_columns
    timestamp_field = 'timestamp'
    parent_model = Events
    parent_column_name = 'event_type_id'

    def qs(self, account):
        return Events.objects.filter(account_id=account.id)

    def get_default_query(self, account, obj=None):
        if type(account) is not Account:
            raise ValueError(f'{account} needs to be Account')

        return QueryRequest(filter=Filter(op=Op.AND, filters=[]))


default_monitor_transaction_search_filter = Filter(
    lhs=Expression(column_identifier=ColumnIdentifier(name="type", type=LiteralType.ID)),
    op=Op.IN,
    rhs=Expression(
        literal=Literal(
            literal_type=LiteralType.ID_ARRAY,
            id_array=[
                IdLiteral(
                    type=IdLiteral.Type.LONG,
                    long=UInt64Value(value=1)
                ),
                IdLiteral(
                    type=IdLiteral.Type.LONG,
                    long=UInt64Value(value=2)
                )
            ]
        )
    )
)


class MonitorTransactionContextResolver(ContextResolver):
    columns = monitor_transaction_columns
    timestamp_field = 'created_at'
    parent_model = Monitor
    parent_column_name = 'monitor_id'

    def qs(self, account):
        return account.monitortransaction_set.all()

    def get_default_query(self, account, obj=None):
        if type(account) is not Account:
            raise ValueError(f'{account} needs to be Account')

        # filters = [default_monitor_transaction_search_filter]
        filters = []

        if obj:
            filters.append(
                self.get_parent_id_filter(IdLiteral(
                    long=UInt64Value(value=obj.id),
                    type=IdLiteral.Type.LONG
                ))
            )

        return QueryRequest(filter=Filter(op=Op.AND, filters=filters))


class EntityInstanceContextResolver(ContextResolver):
    columns = entity_instance_columns
    timestamp_field = 'created_at'
    parent_model = Entity
    parent_column_name = 'entity_id'

    def qs(self, account):
        return account.entityinstance_set.all()

    def get_default_query(self, account, obj=None):
        if type(account) is not Account:
            raise ValueError(f'{account} needs to be Account')

        filters = []

        if obj:
            filters.append(
                self.get_parent_id_filter(IdLiteral(
                    long=UInt64Value(value=obj.id),
                    type=IdLiteral.Type.LONG
                ))
            )

        return QueryRequest(filter=Filter(op=Op.AND, filters=filters))


class EventTypeContextResolver(ContextResolver):
    def qs(self, account):
        return account.eventtype_set.all()


class MonitorContextResolver(ContextResolver):
    def qs(self, account):
        return account.monitor_set.all()


class EntityContextResolver(ContextResolver):
    def qs(self, account):
        return account.entity_set.all()


_context_to_resolver = {
    Context.EVENT: EventContextResolver(),
    Context.EVENTS_CLICKHOUSE: EventsClickhouseContextResolver(),
    Context.MONITOR_TRANSACTION: MonitorTransactionContextResolver(),
    Context.ENTITY_INSTANCE: EntityInstanceContextResolver(),
    Context.EVENT_TYPE: EventTypeContextResolver(),
    Context.MONITOR: MonitorContextResolver(),
    Context.ENTITY: EntityContextResolver(),
}


def get_context_resolver(context: Context) -> ContextResolver:
    return _context_to_resolver.get(context)
