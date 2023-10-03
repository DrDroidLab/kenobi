"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import google.protobuf.wrappers_pb2
import protos.event.base_pb2
import protos.event.literal_pb2
import protos.event.query_base_pb2
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _AggregationFunction:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _AggregationFunctionEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_AggregationFunction.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    UNKNOWN_MF: _AggregationFunction.ValueType  # 0
    COUNT: _AggregationFunction.ValueType  # 1
    SUM: _AggregationFunction.ValueType  # 2
    AVG: _AggregationFunction.ValueType  # 3
    MIN: _AggregationFunction.ValueType  # 4
    MAX: _AggregationFunction.ValueType  # 5
    STD_DEV: _AggregationFunction.ValueType  # 6
    VARIANCE: _AggregationFunction.ValueType  # 7
    COUNT_DISTINCT: _AggregationFunction.ValueType  # 8

class AggregationFunction(_AggregationFunction, metaclass=_AggregationFunctionEnumTypeWrapper): ...

UNKNOWN_MF: AggregationFunction.ValueType  # 0
COUNT: AggregationFunction.ValueType  # 1
SUM: AggregationFunction.ValueType  # 2
AVG: AggregationFunction.ValueType  # 3
MIN: AggregationFunction.ValueType  # 4
MAX: AggregationFunction.ValueType  # 5
STD_DEV: AggregationFunction.ValueType  # 6
VARIANCE: AggregationFunction.ValueType  # 7
COUNT_DISTINCT: AggregationFunction.ValueType  # 8
global___AggregationFunction = AggregationFunction

@typing_extensions.final
class MetricSelector(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    FUNCTION_FIELD_NUMBER: builtins.int
    EXPRESSION_FIELD_NUMBER: builtins.int
    ALIAS_FIELD_NUMBER: builtins.int
    function: global___AggregationFunction.ValueType
    @property
    def expression(self) -> protos.event.query_base_pb2.Expression: ...
    alias: builtins.str
    def __init__(
        self,
        *,
        function: global___AggregationFunction.ValueType = ...,
        expression: protos.event.query_base_pb2.Expression | None = ...,
        alias: builtins.str = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["expression", b"expression"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["alias", b"alias", "expression", b"expression", "function", b"function"]) -> None: ...

global___MetricSelector = MetricSelector

@typing_extensions.final
class MetricExpression(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    FILTER_FIELD_NUMBER: builtins.int
    GROUP_BY_FIELD_NUMBER: builtins.int
    SELECTORS_FIELD_NUMBER: builtins.int
    IS_TIMESERIES_FIELD_NUMBER: builtins.int
    RESOLUTION_FIELD_NUMBER: builtins.int
    @property
    def filter(self) -> protos.event.query_base_pb2.Filter: ...
    @property
    def group_by(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[protos.event.query_base_pb2.Expression]: ...
    @property
    def selectors(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___MetricSelector]: ...
    @property
    def is_timeseries(self) -> google.protobuf.wrappers_pb2.BoolValue:
        """ TODO: Need to add a timestamp column here"""
    @property
    def resolution(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    def __init__(
        self,
        *,
        filter: protos.event.query_base_pb2.Filter | None = ...,
        group_by: collections.abc.Iterable[protos.event.query_base_pb2.Expression] | None = ...,
        selectors: collections.abc.Iterable[global___MetricSelector] | None = ...,
        is_timeseries: google.protobuf.wrappers_pb2.BoolValue | None = ...,
        resolution: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["filter", b"filter", "is_timeseries", b"is_timeseries", "resolution", b"resolution"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["filter", b"filter", "group_by", b"group_by", "is_timeseries", b"is_timeseries", "resolution", b"resolution", "selectors", b"selectors"]) -> None: ...

global___MetricExpression = MetricExpression

@typing_extensions.final
class LabelMetadata(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    EXPRESSION_FIELD_NUMBER: builtins.int
    ALIAS_FIELD_NUMBER: builtins.int
    @property
    def expression(self) -> protos.event.query_base_pb2.Expression:
        """ This will be made up of all the columns being used in group by"""
    alias: builtins.str
    def __init__(
        self,
        *,
        expression: protos.event.query_base_pb2.Expression | None = ...,
        alias: builtins.str = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["expression", b"expression"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["alias", b"alias", "expression", b"expression"]) -> None: ...

global___LabelMetadata = LabelMetadata

@typing_extensions.final
class TsDataPoint(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TIMESTAMP_FIELD_NUMBER: builtins.int
    VALUE_FIELD_NUMBER: builtins.int
    timestamp: builtins.int
    @property
    def value(self) -> protos.event.literal_pb2.Literal: ...
    def __init__(
        self,
        *,
        timestamp: builtins.int = ...,
        value: protos.event.literal_pb2.Literal | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["value", b"value"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["timestamp", b"timestamp", "value", b"value"]) -> None: ...

global___TsDataPoint = TsDataPoint

@typing_extensions.final
class Data(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TIMESERIES_DATA_FIELD_NUMBER: builtins.int
    VALUE_FIELD_NUMBER: builtins.int
    @property
    def timeseries_data(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___TsDataPoint]: ...
    @property
    def value(self) -> protos.event.literal_pb2.Literal: ...
    def __init__(
        self,
        *,
        timeseries_data: collections.abc.Iterable[global___TsDataPoint] | None = ...,
        value: protos.event.literal_pb2.Literal | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["value", b"value"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["timeseries_data", b"timeseries_data", "value", b"value"]) -> None: ...

global___Data = Data

@typing_extensions.final
class Label(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    VALUE_FIELD_NUMBER: builtins.int
    DISPLAY_VALUE_FIELD_NUMBER: builtins.int
    @property
    def value(self) -> protos.event.literal_pb2.Literal: ...
    display_value: builtins.str
    def __init__(
        self,
        *,
        value: protos.event.literal_pb2.Literal | None = ...,
        display_value: builtins.str = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["value", b"value"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["display_value", b"display_value", "value", b"value"]) -> None: ...

global___Label = Label

@typing_extensions.final
class LabeledData(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class AliasDataMapEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: builtins.str
        @property
        def value(self) -> global___Data: ...
        def __init__(
            self,
            *,
            key: builtins.str = ...,
            value: global___Data | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["value", b"value"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["key", b"key", "value", b"value"]) -> None: ...

    LABEL_GROUP_FIELD_NUMBER: builtins.int
    LABELS_FIELD_NUMBER: builtins.int
    ALIAS_DATA_MAP_FIELD_NUMBER: builtins.int
    label_group: builtins.str
    @property
    def labels(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___Label]: ...
    @property
    def alias_data_map(self) -> google.protobuf.internal.containers.MessageMap[builtins.str, global___Data]: ...
    def __init__(
        self,
        *,
        label_group: builtins.str = ...,
        labels: collections.abc.Iterable[global___Label] | None = ...,
        alias_data_map: collections.abc.Mapping[builtins.str, global___Data] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["alias_data_map", b"alias_data_map", "label_group", b"label_group", "labels", b"labels"]) -> None: ...

global___LabeledData = LabeledData

@typing_extensions.final
class MetricDataMetadata(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class MetricAliasSelectorMapEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: builtins.str
        @property
        def value(self) -> global___MetricSelector: ...
        def __init__(
            self,
            *,
            key: builtins.str = ...,
            value: global___MetricSelector | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["value", b"value"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["key", b"key", "value", b"value"]) -> None: ...

    LABELS_METADATA_FIELD_NUMBER: builtins.int
    IS_TIMESERIES_FIELD_NUMBER: builtins.int
    RESOLUTION_FIELD_NUMBER: builtins.int
    TIME_RANGE_FIELD_NUMBER: builtins.int
    METRIC_ALIAS_SELECTOR_MAP_FIELD_NUMBER: builtins.int
    @property
    def labels_metadata(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___LabelMetadata]: ...
    @property
    def is_timeseries(self) -> google.protobuf.wrappers_pb2.BoolValue: ...
    @property
    def resolution(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def time_range(self) -> protos.event.base_pb2.TimeRange: ...
    @property
    def metric_alias_selector_map(self) -> google.protobuf.internal.containers.MessageMap[builtins.str, global___MetricSelector]: ...
    def __init__(
        self,
        *,
        labels_metadata: collections.abc.Iterable[global___LabelMetadata] | None = ...,
        is_timeseries: google.protobuf.wrappers_pb2.BoolValue | None = ...,
        resolution: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        time_range: protos.event.base_pb2.TimeRange | None = ...,
        metric_alias_selector_map: collections.abc.Mapping[builtins.str, global___MetricSelector] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["is_timeseries", b"is_timeseries", "resolution", b"resolution", "time_range", b"time_range"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["is_timeseries", b"is_timeseries", "labels_metadata", b"labels_metadata", "metric_alias_selector_map", b"metric_alias_selector_map", "resolution", b"resolution", "time_range", b"time_range"]) -> None: ...

global___MetricDataMetadata = MetricDataMetadata

@typing_extensions.final
class MetricData(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    METADATA_FIELD_NUMBER: builtins.int
    LABELED_DATA_FIELD_NUMBER: builtins.int
    @property
    def metadata(self) -> global___MetricDataMetadata: ...
    @property
    def labeled_data(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___LabeledData]: ...
    def __init__(
        self,
        *,
        metadata: global___MetricDataMetadata | None = ...,
        labeled_data: collections.abc.Iterable[global___LabeledData] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["metadata", b"metadata"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["labeled_data", b"labeled_data", "metadata", b"metadata"]) -> None: ...

global___MetricData = MetricData