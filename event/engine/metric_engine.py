import math
from typing import List

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
