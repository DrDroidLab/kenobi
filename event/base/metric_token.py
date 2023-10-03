from collections import OrderedDict
from functools import lru_cache
from typing import List, Dict
import re

from django.db import models
from django.db.models import QuerySet, Count, Sum, Avg, Max, Min, StdDev, Variance
from django.db.models.expressions import RawSQL, F
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast
from google.protobuf.wrappers_pb2 import BoolValue, UInt64Value

from event.clickhouse.models import Events

from event.base.filter_token import FilterToken, FilterTokenizer, FilterTokenValidator, \
    FilterTokenEvaluator, FilterTokenAnnotator
from event.base.literal import obj_to_literal
from event.base.token import Token, Groupable, Filterable, ColumnToken, AttributeToken, ExpressionTokenizer, Annotable
from protos.event.literal_pb2 import LiteralType
from protos.event.metric_pb2 import AggregationFunction, LabeledData, MetricData, MetricDataMetadata, MetricExpression, \
    MetricSelector, TsDataPoint
from prototype.utils.timerange import DateTimeRange, filter_dtr

_FUNCTION_DICT = {
    AggregationFunction.SUM: Sum,
    AggregationFunction.AVG: Avg,
    AggregationFunction.MAX: Max,
    AggregationFunction.MIN: Min,
    AggregationFunction.STD_DEV: StdDev,
    AggregationFunction.VARIANCE: Variance,
    AggregationFunction.COUNT: Count,
}

_AGGREGATEABLE_TYPES = {
    LiteralType.LONG,
    LiteralType.DOUBLE,
    LiteralType.TIMESTAMP,
}


@lru_cache(maxsize=10)
def get_metric_for_idx(idx: int):
    return f'metric_{idx + 1}'


def get_float_metric(aggrfn, key, field):
    return aggrfn(
        Cast(
            KeyTextTransform(key, field), models.FloatField()
        )
    )


def get_label_group(label_group_keys, record):
    return '__'.join([str(record[key]) for key in label_group_keys])


class MetricSelectorToken(Token):
    function: AggregationFunction = None
    expression: Token = None
    alias: str = None
    metric_alias: str = None
    metric_selector: MetricSelector = None

    def display(self) -> str:
        return f'{AggregationFunction.Name(self.function)}({self.expression.display()}) as {self.alias}'


class MetricSelectorTokenizer:
    def __init__(self, columns):
        self._columns = columns
        self._expression_tokenizer = ExpressionTokenizer(columns)

    def tokenize(self, metric_selector: MetricSelector, idx) -> MetricSelectorToken:
        metric_selector_token = MetricSelectorToken()

        metric_selector_token.function = metric_selector.function
        metric_selector_token.expression = self._expression_tokenizer.tokenize(metric_selector.expression)
        metric_selector_token.alias = metric_selector.alias
        metric_selector_token.metric_alias = get_metric_for_idx(idx)
        metric_selector_token.metric_selector = metric_selector

        return metric_selector_token


class MetricSelectorTokenAnnotator:
    def annotations(self, selector: Token) -> Dict:
        if not isinstance(selector, MetricSelectorToken):
            raise ValueError('MetricSelectorTokenAnnotator can only process MetricSelectorToken')
        annotations = {}
        if isinstance(selector.expression, Annotable):
            annotations.update(selector.expression.annotations())
        return annotations


class MetricToken(Token):
    filter: FilterToken = None
    group_by: List[Token] = None
    selectors: List[MetricSelectorToken] = None
    selector_metric_idx_alias_dict: Dict = None
    is_timeseries: bool = False
    resolution: int = 30
    timestamp_field: str = None

    def display(self) -> str:
        return f'{" ,".join(selector.display() for selector in self.selectors)} WHERE {self.filter.display()} GROUP BY {", ".join([group_by.display() for group_by in self.group_by])}'


class MetricTokenizer:
    def __init__(self, columns, timestamp_field):
        self._columns = columns
        self._timestamp_field = timestamp_field
        self._filter_tokenizer = FilterTokenizer(columns)
        self._metric_selector_tokenizer = MetricSelectorTokenizer(columns)
        self._expression_tokenizer = ExpressionTokenizer(columns)

    def tokenize(self, metric_expression: MetricExpression) -> MetricToken:
        metric_token = MetricToken()
        metric_token.filter = self._filter_tokenizer.tokenize(metric_expression.filter)
        metric_token.group_by = [self._expression_tokenizer.tokenize(g) for g in metric_expression.group_by]
        metric_token.selectors = [self._metric_selector_tokenizer.tokenize(s, idx) for idx, s in
                                  enumerate(metric_expression.selectors)]

        metric_token.selector_metric_idx_alias_dict = {
            get_metric_for_idx(idx): s.alias for idx, s in enumerate(metric_token.selectors)
        }

        metric_token.is_timeseries = metric_expression.is_timeseries.value
        if metric_expression.resolution.value:
            metric_token.resolution = metric_expression.resolution.value
        metric_token.timestamp_field = self._timestamp_field
        return metric_token


class MetricTokenValidator:
    def __init__(self):
        self._filter_token_validator = FilterTokenValidator()

    def validate(self, metric_token: MetricToken) -> (bool, str):
        if metric_token.filter:
            is_filter_token_valid, err = self._filter_token_validator.validate(metric_token.filter)
            if not is_filter_token_valid:
                return False, err
        return True, ''

        # TODO: Add validation checks for group_by and selectors


class MetricTokenAnnotator:
    def __init__(self):
        self._metric_selector_token_annotator = MetricSelectorTokenAnnotator()
        self._filter_token_annotator = FilterTokenAnnotator()

    def annotations(self, token: Token) -> Dict:
        if not isinstance(token, MetricToken):
            raise ValueError('MetricTokenAnnotator can only process MetricToken')
        annotations = {}
        if token.filter:
            annotations.update(self._filter_token_annotator.annotations(token.filter))
        for g in token.group_by:
            if isinstance(g, Annotable):
                annotations.update(g.annotations())

        for selector in token.selectors:
            annotations.update(self._metric_selector_token_annotator.annotations(selector))

        return annotations


class MetricTokenProcessor:
    def __init__(self):
        self._filter_token_evaluator = FilterTokenEvaluator()
        self._metric_token_annotator = MetricTokenAnnotator()
        self._timestamp_bucket = 'timestamp_bucket'

    def _selector_annotations(self, selectors: List[MetricSelectorToken]) -> OrderedDict:
        selector_annotations = OrderedDict({})
        for idx, selector in enumerate(selectors):
            selector_function = selector.function
            expression: Filterable = selector.expression
            metric_alias = selector.metric_alias

            if selector_function is AggregationFunction.COUNT:
                if expression:
                    selector_annotations[metric_alias] = Count(F(expression.filter_key()))
                else:
                    selector_annotations[metric_alias] = Count('pk')
            elif selector_function is AggregationFunction.COUNT_DISTINCT:
                selector_annotations[metric_alias] = Count(F(expression.filter_key()), distinct=True)
            else:
                if isinstance(expression, ColumnToken):
                    column_type = expression.column.type
                    if column_type not in _AGGREGATEABLE_TYPES:
                        raise ValueError(
                            f'Function {AggregationFunction.Name(selector_function)} not valid for column {expression.column.display_name} of type {LiteralType.Name(column_type)}'
                        )
                    if selector_function not in expression.column.aggregation_functions:
                        raise ValueError(
                            f'Function {AggregationFunction.Name(selector_function)} not valid for column {expression.column.display_name}'
                        )

                    selector_annotations[metric_alias] = _FUNCTION_DICT[selector_function](F(expression.filter_key()))
                elif isinstance(expression, AttributeToken):
                    selector_annotations[metric_alias] = _FUNCTION_DICT[selector_function](
                        Cast(
                            KeyTextTransform(expression.attribute_identifier.name,
                                             expression.attribute_identifier.path), models.FloatField()
                        )
                    )
        return selector_annotations

    def process(self, qs: QuerySet, metric_token: MetricToken, dtr: DateTimeRange):
        is_timeseries = metric_token.is_timeseries
        ts_field = metric_token.timestamp_field
        resolution = metric_token.resolution

        # Filter timerange on the base qs
        qs: QuerySet = filter_dtr(qs, dtr, ts_field)

        annotations = self._metric_token_annotator.annotations(metric_token)
        qs = qs.annotate(**annotations)
        if metric_token.filter:
            # Apply filter on the base qs
            qs = self._filter_token_evaluator.process(qs, metric_token.filter)
        if is_timeseries:
            # Annotate each record with a timestamp bucket based on the resolution and the start timestamp
            qs = qs.annotate(timestamp_bucket=RawSQL(
                '{start_ts} + (((CAST(extract(epoch from "{table}"."{ts_field}") as BIGINT) - {start_ts}) /%s) * %s)'.format(
                    table=qs.model._meta.db_table,
                    ts_field=ts_field,
                    start_ts=int(dtr.time_geq.timestamp())
                )
                , [resolution, resolution])
            )

        # All group by labels from columns
        group_by: list = list()
        # All metric label metadata expressions
        metric_label_metadata = OrderedDict()
        for g in metric_token.group_by:
            if isinstance(g, Groupable):
                k = g.group_key()
                group_by.append(k)
                metric_label_metadata[k] = g

        if is_timeseries:
            group_by.insert(0, self._timestamp_bucket)

        selector_annotations = self._selector_annotations(metric_token.selectors)
        selector_annotation_aliases = list(selector_annotations.keys())

        if group_by:
            qs = qs.values(*(list(group_by)))
            qs = qs.annotate(**selector_annotations)
            if is_timeseries:
                qs = qs.order_by(self._timestamp_bucket)
        else:
            # In case there is no group by and no timeseries, we need to resolve the selections here only
            qs = qs.aggregate(**selector_annotations)

        resolved_qs = []
        if isinstance(qs, QuerySet):
            resolved_qs = list(qs)
        elif isinstance(qs, Dict):
            resolved_qs = [qs]

        label_key_ordering = metric_label_metadata.keys()

        label_group_data_map = {}
        for record in resolved_qs:
            label_group = get_label_group(label_key_ordering, record)
            if label_group not in label_group_data_map:
                label_group_data_map[label_group] = LabeledData(
                    label_group=label_group,
                    labels=[
                        metric_label_metadata[label_key].group_label(record[label_key])
                        for label_key in label_key_ordering
                    ],
                    alias_data_map={}
                )
            data = label_group_data_map[label_group]
            for metric_alias in selector_annotation_aliases:
                metric = obj_to_literal(record[metric_alias])
                if is_timeseries:
                    data.alias_data_map[metric_alias].timeseries_data.append(
                        TsDataPoint(
                            timestamp=int(record[self._timestamp_bucket]),
                            value=metric
                        )
                    )
                else:
                    data.alias_data_map[metric_alias].value.CopyFrom(metric)

        metric_data_metadata = MetricDataMetadata(
            labels_metadata=[
                metric_label_metadata[label_key].group_label_metadata()
                for label_key in label_key_ordering
            ],
            is_timeseries=BoolValue(value=is_timeseries),
            resolution=UInt64Value(value=resolution),
            time_range=dtr.to_tr(),
            metric_alias_selector_map={
                selector.metric_alias: selector.metric_selector
                for selector in metric_token.selectors
            }
        )

        return MetricData(
            metadata=metric_data_metadata,
            labeled_data=list(label_group_data_map.values())
        )


class EventsClickhouseMetricTokenProcessor(MetricTokenProcessor):

    def process(self, qs: QuerySet, metric_token: MetricToken, dtr: DateTimeRange):
        is_timeseries = metric_token.is_timeseries
        ts_field = metric_token.timestamp_field
        resolution = metric_token.resolution

        # Filter timerange on the base qs
        qs: QuerySet = filter_dtr(qs, dtr, ts_field)

        annotations = self._metric_token_annotator.annotations(metric_token)
        qs = qs.annotate(**annotations)
        if metric_token.filter:
            # Apply filter on the base qs
            qs = self._filter_token_evaluator.process(qs, metric_token.filter)
        if is_timeseries:
            # Annotate each record with a timestamp bucket based on the resolution and the start timestamp
            qs = qs.annotate(timestamp_bucket=RawSQL(
                '{start_ts} + (floor((toUInt64(toDateTime("{table}"."{ts_field}")) - {start_ts}) /%s) * %s)'.format(
                    table=qs.model._meta.db_table,
                    ts_field=ts_field,
                    start_ts=int(dtr.time_geq.timestamp())
                )
                , [resolution, resolution])
            )

        # All group by labels from columns
        group_by: list = list()
        # All metric label metadata expressions
        metric_label_metadata = OrderedDict()
        for g in metric_token.group_by:
            if isinstance(g, Groupable):
                k = g.group_key()
                group_by.append(k)
                metric_label_metadata[k] = g

        if is_timeseries:
            group_by.insert(0, self._timestamp_bucket)

        selector_annotations = self._selector_annotations(metric_token.selectors)
        selector_annotation_aliases = list(selector_annotations.keys())

        if group_by:
            qs = qs.values(*(list(group_by)))
            qs = qs.annotate(**selector_annotations)
            if is_timeseries:
                qs = qs.order_by(self._timestamp_bucket)
        else:
            # In case there is no group by and no timeseries, we need to resolve the selections here only
            qs = qs.aggregate(**selector_annotations)

        resolved_qs = []
        if isinstance(qs, QuerySet):
            resolved_qs = list(qs)
        elif isinstance(qs, Dict):
            resolved_qs = [qs]

        label_key_ordering = metric_label_metadata.keys()

        label_group_data_map = {}
        for record in resolved_qs:
            label_group = get_label_group(label_key_ordering, record)
            if label_group not in label_group_data_map:
                label_group_data_map[label_group] = LabeledData(
                    label_group=label_group,
                    labels=[
                        metric_label_metadata[label_key].group_label(record[label_key])
                        for label_key in label_key_ordering
                    ],
                    alias_data_map={}
                )
            data = label_group_data_map[label_group]
            for metric_alias in selector_annotation_aliases:
                metric = obj_to_literal(record[metric_alias])
                if is_timeseries:
                    data.alias_data_map[metric_alias].timeseries_data.append(
                        TsDataPoint(
                            timestamp=int(record[self._timestamp_bucket]),
                            value=metric
                        )
                    )
                else:
                    data.alias_data_map[metric_alias].value.CopyFrom(metric)

        metric_data_metadata = MetricDataMetadata(
            labels_metadata=[
                metric_label_metadata[label_key].group_label_metadata()
                for label_key in label_key_ordering
            ],
            is_timeseries=BoolValue(value=is_timeseries),
            resolution=UInt64Value(value=resolution),
            time_range=dtr.to_tr(),
            metric_alias_selector_map={
                selector.metric_alias: selector.metric_selector
                for selector in metric_token.selectors
            }
        )

        return MetricData(
            metadata=metric_data_metadata,
            labeled_data=list(label_group_data_map.values())
        )


class MetricExpressionEvaluator:
    def __init__(self, parent_model, columns, timestamp_field):
        self._metric_tokenizer = MetricTokenizer(columns, timestamp_field)
        self._metric_token_validator = MetricTokenValidator()

        if parent_model == Events:
            self._metric_token_processor = EventsClickhouseMetricTokenProcessor()
        else:
            self._metric_token_processor = MetricTokenProcessor()

    def process(self, qs, metric_expression: MetricExpression, dtr: DateTimeRange):
        metric_token: MetricToken = self._metric_tokenizer.tokenize(metric_expression)
        is_valid, err = self._metric_token_validator.validate(metric_token)
        if not is_valid:
            raise ValueError(err)
        return self._metric_token_processor.process(qs, metric_token, dtr)

    def process_batch(self, qs: QuerySet, metric_expressions: List[MetricExpression], dtr: DateTimeRange):
        metric_tokens: List[MetricToken] = [
            self._metric_tokenizer.tokenize(metric_expression) for metric_expression in metric_expressions
        ]
        for metric_token in metric_tokens:
            is_valid, err = self._metric_token_validator.validate(metric_token)
            if not is_valid:
                raise ValueError(err)
        return [
            self._metric_token_processor.process(qs, metric_token, dtr) for metric_token in metric_tokens
        ]
