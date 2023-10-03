from collections import OrderedDict

from google.protobuf.wrappers_pb2 import BoolValue, StringValue

from protos.event.engine_options_pb2 import MetricOptions
from protos.event.metric_pb2 import AggregationFunction

metric_aggregation_function_options_dict = OrderedDict([
    (AggregationFunction.COUNT, MetricOptions.AggregationFunctionOption(
        aggregation_function=AggregationFunction.COUNT,
        supports_empty_expression_selector=BoolValue(value=True),
        label=StringValue(value='Count'),
    )),
    (AggregationFunction.SUM, MetricOptions.AggregationFunctionOption(
        aggregation_function=AggregationFunction.SUM,
        supports_empty_expression_selector=BoolValue(value=False),
        label=StringValue(value='Sum'),
    )),
    (AggregationFunction.AVG, MetricOptions.AggregationFunctionOption(
        aggregation_function=AggregationFunction.AVG,
        supports_empty_expression_selector=BoolValue(value=False),
        label=StringValue(value='Avg'),
    )),
    (AggregationFunction.MIN, MetricOptions.AggregationFunctionOption(
        aggregation_function=AggregationFunction.MIN,
        supports_empty_expression_selector=BoolValue(value=False),
        label=StringValue(value='Min'),
    )),
    (AggregationFunction.MAX, MetricOptions.AggregationFunctionOption(
        aggregation_function=AggregationFunction.MAX,
        supports_empty_expression_selector=BoolValue(value=False),
        label=StringValue(value='Max'),
    )),
    (AggregationFunction.STD_DEV, MetricOptions.AggregationFunctionOption(
        aggregation_function=AggregationFunction.STD_DEV,
        supports_empty_expression_selector=BoolValue(value=False),
        label=StringValue(value='Std Dev'),
    )),
    (AggregationFunction.VARIANCE, MetricOptions.AggregationFunctionOption(
        aggregation_function=AggregationFunction.VARIANCE,
        supports_empty_expression_selector=BoolValue(value=False),
        label=StringValue(value='Variance'),
    )),
    (AggregationFunction.COUNT_DISTINCT, MetricOptions.AggregationFunctionOption(
        aggregation_function=AggregationFunction.COUNT_DISTINCT,
        supports_empty_expression_selector=BoolValue(value=False),
        label=StringValue(value='Count Distinct'),
    ))
])

metric_aggregation_function_options_list = list(metric_aggregation_function_options_dict.values())


def get_metric_aggregation_function_options():
    return metric_aggregation_function_options_list
