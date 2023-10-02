"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.message
import google.protobuf.wrappers_pb2
import protos.event.literal_pb2
import protos.event.metric_pb2
import protos.event.query_base_pb2
import sys

if sys.version_info >= (3, 8):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class GlobalQueryOptions(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    OP_DESCRIPTIONS_FIELD_NUMBER: builtins.int
    OP_MAPPING_FIELD_NUMBER: builtins.int
    LITERAL_TYPE_DESCRIPTION_FIELD_NUMBER: builtins.int
    @property
    def op_descriptions(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[protos.event.query_base_pb2.OpDescription]: ...
    @property
    def op_mapping(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[protos.event.query_base_pb2.OpMapping]: ...
    @property
    def literal_type_description(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[protos.event.literal_pb2.LiteralTypeDescription]: ...
    def __init__(
        self,
        *,
        op_descriptions: collections.abc.Iterable[protos.event.query_base_pb2.OpDescription] | None = ...,
        op_mapping: collections.abc.Iterable[protos.event.query_base_pb2.OpMapping] | None = ...,
        literal_type_description: collections.abc.Iterable[protos.event.literal_pb2.LiteralTypeDescription] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["literal_type_description", b"literal_type_description", "op_descriptions", b"op_descriptions", "op_mapping", b"op_mapping"]) -> None: ...

global___GlobalQueryOptions = GlobalQueryOptions

@typing_extensions.final
class ColumnOption(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class IdOption(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        @typing_extensions.final
        class LongOptionsEntry(google.protobuf.message.Message):
            DESCRIPTOR: google.protobuf.descriptor.Descriptor

            KEY_FIELD_NUMBER: builtins.int
            VALUE_FIELD_NUMBER: builtins.int
            key: builtins.int
            value: builtins.str
            def __init__(
                self,
                *,
                key: builtins.int = ...,
                value: builtins.str = ...,
            ) -> None: ...
            def ClearField(self, field_name: typing_extensions.Literal["key", b"key", "value", b"value"]) -> None: ...

        @typing_extensions.final
        class StringOptionsEntry(google.protobuf.message.Message):
            DESCRIPTOR: google.protobuf.descriptor.Descriptor

            KEY_FIELD_NUMBER: builtins.int
            VALUE_FIELD_NUMBER: builtins.int
            key: builtins.str
            value: builtins.str
            def __init__(
                self,
                *,
                key: builtins.str = ...,
                value: builtins.str = ...,
            ) -> None: ...
            def ClearField(self, field_name: typing_extensions.Literal["key", b"key", "value", b"value"]) -> None: ...

        TYPE_FIELD_NUMBER: builtins.int
        LONG_OPTIONS_FIELD_NUMBER: builtins.int
        STRING_OPTIONS_FIELD_NUMBER: builtins.int
        type: protos.event.literal_pb2.IdLiteral.Type.ValueType
        @property
        def long_options(self) -> google.protobuf.internal.containers.ScalarMap[builtins.int, builtins.str]: ...
        @property
        def string_options(self) -> google.protobuf.internal.containers.ScalarMap[builtins.str, builtins.str]: ...
        def __init__(
            self,
            *,
            type: protos.event.literal_pb2.IdLiteral.Type.ValueType = ...,
            long_options: collections.abc.Mapping[builtins.int, builtins.str] | None = ...,
            string_options: collections.abc.Mapping[builtins.str, builtins.str] | None = ...,
        ) -> None: ...
        def ClearField(self, field_name: typing_extensions.Literal["long_options", b"long_options", "string_options", b"string_options", "type", b"type"]) -> None: ...

    NAME_FIELD_NUMBER: builtins.int
    ALIAS_FIELD_NUMBER: builtins.int
    TYPE_FIELD_NUMBER: builtins.int
    IS_GROUPABLE_FIELD_NUMBER: builtins.int
    AGGREGATION_FUNCTIONS_FIELD_NUMBER: builtins.int
    ID_OPTION_FIELD_NUMBER: builtins.int
    name: builtins.str
    alias: builtins.str
    type: protos.event.literal_pb2.LiteralType.ValueType
    is_groupable: builtins.bool
    @property
    def aggregation_functions(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[protos.event.metric_pb2.AggregationFunction.ValueType]: ...
    @property
    def id_option(self) -> global___ColumnOption.IdOption: ...
    def __init__(
        self,
        *,
        name: builtins.str = ...,
        alias: builtins.str = ...,
        type: protos.event.literal_pb2.LiteralType.ValueType = ...,
        is_groupable: builtins.bool = ...,
        aggregation_functions: collections.abc.Iterable[protos.event.metric_pb2.AggregationFunction.ValueType] | None = ...,
        id_option: global___ColumnOption.IdOption | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["id_option", b"id_option"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["aggregation_functions", b"aggregation_functions", "alias", b"alias", "id_option", b"id_option", "is_groupable", b"is_groupable", "name", b"name", "type", b"type"]) -> None: ...

global___ColumnOption = ColumnOption

@typing_extensions.final
class AttributeOption(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class ColumnContext(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        ID_FIELD_NUMBER: builtins.int
        ALIAS_FIELD_NUMBER: builtins.int
        @property
        def id(self) -> protos.event.literal_pb2.IdLiteral: ...
        alias: builtins.str
        def __init__(
            self,
            *,
            id: protos.event.literal_pb2.IdLiteral | None = ...,
            alias: builtins.str = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["id", b"id"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["alias", b"alias", "id", b"id"]) -> None: ...

    NAME_FIELD_NUMBER: builtins.int
    PATH_FIELD_NUMBER: builtins.int
    TYPE_FIELD_NUMBER: builtins.int
    ALIAS_FIELD_NUMBER: builtins.int
    COLUMN_CONTEXT_FIELD_NUMBER: builtins.int
    PATH_ALIAS_FIELD_NUMBER: builtins.int
    IS_GROUPABLE_FIELD_NUMBER: builtins.int
    AGGREGATION_FUNCTIONS_FIELD_NUMBER: builtins.int
    name: builtins.str
    path: builtins.str
    type: protos.event.literal_pb2.LiteralType.ValueType
    alias: builtins.str
    @property
    def column_context(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___AttributeOption.ColumnContext]: ...
    path_alias: builtins.str
    is_groupable: builtins.bool
    @property
    def aggregation_functions(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[protos.event.metric_pb2.AggregationFunction.ValueType]: ...
    def __init__(
        self,
        *,
        name: builtins.str = ...,
        path: builtins.str = ...,
        type: protos.event.literal_pb2.LiteralType.ValueType = ...,
        alias: builtins.str = ...,
        column_context: collections.abc.Iterable[global___AttributeOption.ColumnContext] | None = ...,
        path_alias: builtins.str = ...,
        is_groupable: builtins.bool = ...,
        aggregation_functions: collections.abc.Iterable[protos.event.metric_pb2.AggregationFunction.ValueType] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["aggregation_functions", b"aggregation_functions", "alias", b"alias", "column_context", b"column_context", "is_groupable", b"is_groupable", "name", b"name", "path", b"path", "path_alias", b"path_alias", "type", b"type"]) -> None: ...

global___AttributeOption = AttributeOption

@typing_extensions.final
class AttributeOptionV2(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    NAME_FIELD_NUMBER: builtins.int
    PATH_FIELD_NUMBER: builtins.int
    TYPE_FIELD_NUMBER: builtins.int
    name: builtins.str
    @property
    def path(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    type: protos.event.literal_pb2.LiteralType.ValueType
    def __init__(
        self,
        *,
        name: builtins.str = ...,
        path: collections.abc.Iterable[builtins.str] | None = ...,
        type: protos.event.literal_pb2.LiteralType.ValueType = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["name", b"name", "path", b"path", "type", b"type"]) -> None: ...

global___AttributeOptionV2 = AttributeOptionV2

@typing_extensions.final
class QueryOptions(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    COLUMN_OPTIONS_FIELD_NUMBER: builtins.int
    ATTRIBUTE_OPTIONS_FIELD_NUMBER: builtins.int
    @property
    def column_options(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___ColumnOption]: ...
    @property
    def attribute_options(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___AttributeOption]: ...
    def __init__(
        self,
        *,
        column_options: collections.abc.Iterable[global___ColumnOption] | None = ...,
        attribute_options: collections.abc.Iterable[global___AttributeOption] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["attribute_options", b"attribute_options", "column_options", b"column_options"]) -> None: ...

global___QueryOptions = QueryOptions

@typing_extensions.final
class QueryOptionsV2(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    COLUMN_OPTIONS_FIELD_NUMBER: builtins.int
    ATTRIBUTE_OPTIONS_V2_FIELD_NUMBER: builtins.int
    @property
    def column_options(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___ColumnOption]: ...
    @property
    def attribute_options_v2(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___AttributeOptionV2]: ...
    def __init__(
        self,
        *,
        column_options: collections.abc.Iterable[global___ColumnOption] | None = ...,
        attribute_options_v2: collections.abc.Iterable[global___AttributeOptionV2] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["attribute_options_v2", b"attribute_options_v2", "column_options", b"column_options"]) -> None: ...

global___QueryOptionsV2 = QueryOptionsV2

@typing_extensions.final
class MetricOptions(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class AggregationFunctionOption(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        AGGREGATION_FUNCTION_FIELD_NUMBER: builtins.int
        SUPPORTS_EMPTY_EXPRESSION_SELECTOR_FIELD_NUMBER: builtins.int
        LABEL_FIELD_NUMBER: builtins.int
        aggregation_function: protos.event.metric_pb2.AggregationFunction.ValueType
        @property
        def supports_empty_expression_selector(self) -> google.protobuf.wrappers_pb2.BoolValue: ...
        @property
        def label(self) -> google.protobuf.wrappers_pb2.StringValue: ...
        def __init__(
            self,
            *,
            aggregation_function: protos.event.metric_pb2.AggregationFunction.ValueType = ...,
            supports_empty_expression_selector: google.protobuf.wrappers_pb2.BoolValue | None = ...,
            label: google.protobuf.wrappers_pb2.StringValue | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["label", b"label", "supports_empty_expression_selector", b"supports_empty_expression_selector"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["aggregation_function", b"aggregation_function", "label", b"label", "supports_empty_expression_selector", b"supports_empty_expression_selector"]) -> None: ...

    AGGREGATION_FUNCTION_OPTIONS_FIELD_NUMBER: builtins.int
    COLUMN_OPTIONS_FIELD_NUMBER: builtins.int
    ATTRIBUTE_OPTIONS_FIELD_NUMBER: builtins.int
    @property
    def aggregation_function_options(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___MetricOptions.AggregationFunctionOption]: ...
    @property
    def column_options(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___ColumnOption]: ...
    @property
    def attribute_options(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___AttributeOption]: ...
    def __init__(
        self,
        *,
        aggregation_function_options: collections.abc.Iterable[global___MetricOptions.AggregationFunctionOption] | None = ...,
        column_options: collections.abc.Iterable[global___ColumnOption] | None = ...,
        attribute_options: collections.abc.Iterable[global___AttributeOption] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["aggregation_function_options", b"aggregation_function_options", "attribute_options", b"attribute_options", "column_options", b"column_options"]) -> None: ...

global___MetricOptions = MetricOptions
