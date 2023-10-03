from django.db.models import QuerySet

from event.engine.context import ContextResolver, get_context_resolver
from event.models import Event, MonitorTransaction, EntityInstance
from event.clickhouse.models import Events
from protos.event.base_pb2 import Context
from protos.event.literal_pb2 import IdLiteral
from protos.event.query_base_pb2 import QueryRequest, OrderByExpression


class QueryEngineException(ValueError):
    pass


def get_default_query(account, obj) -> QueryRequest:
    return QueryRequest()


class QueryEngine:
    def __init__(self, model, context_resolver: ContextResolver):
        self._model = model
        self._context_resolver = context_resolver

    def process_query(self, qs: QuerySet, query_request: QueryRequest) -> QuerySet:
        if qs.model is not self._model:
            raise QueryEngineException(f'Query engine not supported for {qs.model.__name__}')
        return self._context_resolver.filter_engine().process(qs, query_request.filter)

    def process_query_with_filter(self, qs: QuerySet, query_filter) -> QuerySet:
        if qs.model is not self._model:
            raise QueryEngineException(f'Query engine not supported for {qs.model.__name__}')
        return self._context_resolver.filter_engine().process(qs, query_filter)

    def process_ordering(self, qs: QuerySet, query_request: QueryRequest) -> QuerySet:
        if qs.model is not self._model:
            raise QueryEngineException(f'Query engine not supported for {qs.model.__name__}')

        order_by_expression: OrderByExpression = query_request.order_by
        return self._context_resolver.order_by_engine().process(qs, order_by_expression)

    def get_obj(self, account, id: IdLiteral = None):
        return self._context_resolver.get_parent_obj(account, id)

    def get_search_options(self, account, parent_obj=None):
        return self._context_resolver.get_search_options(account, parent_obj)

    def get_search_options_v2(self, account, parent_obj=None):
        return self._context_resolver.get_search_options_v2(account, parent_obj)

    def get_default_query(self, account, obj=None):
        return self._context_resolver.get_default_query(account, obj)


global_event_search_clickhouse_engine = QueryEngine(
    Events,
    get_context_resolver(Context.EVENTS_CLICKHOUSE),
)

global_event_search_engine = QueryEngine(
    Event,
    get_context_resolver(Context.EVENT),
)

monitor_transaction_search_engine = QueryEngine(
    MonitorTransaction,
    get_context_resolver(Context.MONITOR_TRANSACTION),
)

entity_instance_search_engine = QueryEngine(
    EntityInstance,
    get_context_resolver(Context.ENTITY_INSTANCE),
)
