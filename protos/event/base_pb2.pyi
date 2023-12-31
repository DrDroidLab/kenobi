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
import protos.event.schema_pb2
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _Context:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _ContextEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_Context.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    UNKNOWN_C: _Context.ValueType  # 0
    EVENT: _Context.ValueType  # 1
    MONITOR_TRANSACTION: _Context.ValueType  # 2
    ENTITY_INSTANCE: _Context.ValueType  # 3
    EVENT_TYPE: _Context.ValueType  # 4
    MONITOR: _Context.ValueType  # 5
    ENTITY: _Context.ValueType  # 6
    EVENTS_CLICKHOUSE: _Context.ValueType  # 7

class Context(_Context, metaclass=_ContextEnumTypeWrapper): ...

UNKNOWN_C: Context.ValueType  # 0
EVENT: Context.ValueType  # 1
MONITOR_TRANSACTION: Context.ValueType  # 2
ENTITY_INSTANCE: Context.ValueType  # 3
EVENT_TYPE: Context.ValueType  # 4
MONITOR: Context.ValueType  # 5
ENTITY: Context.ValueType  # 6
EVENTS_CLICKHOUSE: Context.ValueType  # 7
global___Context = Context

@typing_extensions.final
class TimeRange(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TIME_GEQ_FIELD_NUMBER: builtins.int
    TIME_LT_FIELD_NUMBER: builtins.int
    time_geq: builtins.int
    time_lt: builtins.int
    def __init__(
        self,
        *,
        time_geq: builtins.int = ...,
        time_lt: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["time_geq", b"time_geq", "time_lt", b"time_lt"]) -> None: ...

global___TimeRange = TimeRange

@typing_extensions.final
class Page(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    LIMIT_FIELD_NUMBER: builtins.int
    OFFSET_FIELD_NUMBER: builtins.int
    @property
    def limit(self) -> google.protobuf.wrappers_pb2.UInt32Value: ...
    @property
    def offset(self) -> google.protobuf.wrappers_pb2.UInt32Value: ...
    def __init__(
        self,
        *,
        limit: google.protobuf.wrappers_pb2.UInt32Value | None = ...,
        offset: google.protobuf.wrappers_pb2.UInt32Value | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["limit", b"limit", "offset", b"offset"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["limit", b"limit", "offset", b"offset"]) -> None: ...

global___Page = Page

@typing_extensions.final
class EventKey(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _KeyType:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _KeyTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[EventKey._KeyType.ValueType], builtins.type):  # noqa: F821
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        UNKNOWN: EventKey._KeyType.ValueType  # 0
        STRING: EventKey._KeyType.ValueType  # 1
        LONG: EventKey._KeyType.ValueType  # 2
        DOUBLE: EventKey._KeyType.ValueType  # 3
        BOOLEAN: EventKey._KeyType.ValueType  # 4
        BYTE: EventKey._KeyType.ValueType  # 5
        ARRAY: EventKey._KeyType.ValueType  # 6
        OBJECT: EventKey._KeyType.ValueType  # 7

    class KeyType(_KeyType, metaclass=_KeyTypeEnumTypeWrapper): ...
    UNKNOWN: EventKey.KeyType.ValueType  # 0
    STRING: EventKey.KeyType.ValueType  # 1
    LONG: EventKey.KeyType.ValueType  # 2
    DOUBLE: EventKey.KeyType.ValueType  # 3
    BOOLEAN: EventKey.KeyType.ValueType  # 4
    BYTE: EventKey.KeyType.ValueType  # 5
    ARRAY: EventKey.KeyType.ValueType  # 6
    OBJECT: EventKey.KeyType.ValueType  # 7

    ID_FIELD_NUMBER: builtins.int
    KEY_FIELD_NUMBER: builtins.int
    KEY_TYPE_FIELD_NUMBER: builtins.int
    EVENT_TYPE_FIELD_NUMBER: builtins.int
    id: builtins.int
    key: builtins.str
    key_type: global___EventKey.KeyType.ValueType
    @property
    def event_type(self) -> global___EventTypePartial: ...
    def __init__(
        self,
        *,
        id: builtins.int = ...,
        key: builtins.str = ...,
        key_type: global___EventKey.KeyType.ValueType = ...,
        event_type: global___EventTypePartial | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["event_type", b"event_type"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["event_type", b"event_type", "id", b"id", "key", b"key", "key_type", b"key_type"]) -> None: ...

global___EventKey = EventKey

@typing_extensions.final
class EventType(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    KEYS_FIELD_NUMBER: builtins.int
    EVENT_SOURCES_FIELD_NUMBER: builtins.int
    id: builtins.int
    name: builtins.str
    @property
    def keys(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___EventKey]: ...
    @property
    def event_sources(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[global___Event.EventSource.ValueType]: ...
    def __init__(
        self,
        *,
        id: builtins.int = ...,
        name: builtins.str = ...,
        keys: collections.abc.Iterable[global___EventKey] | None = ...,
        event_sources: collections.abc.Iterable[global___Event.EventSource.ValueType] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["event_sources", b"event_sources", "id", b"id", "keys", b"keys", "name", b"name"]) -> None: ...

global___EventType = EventType

@typing_extensions.final
class EventTypeStats(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    KEYS_COUNT_FIELD_NUMBER: builtins.int
    EVENT_COUNT_FIELD_NUMBER: builtins.int
    MONITOR_COUNT_FIELD_NUMBER: builtins.int
    @property
    def keys_count(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def event_count(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def monitor_count(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    def __init__(
        self,
        *,
        keys_count: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        event_count: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        monitor_count: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["event_count", b"event_count", "keys_count", b"keys_count", "monitor_count", b"monitor_count"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["event_count", b"event_count", "keys_count", b"keys_count", "monitor_count", b"monitor_count"]) -> None: ...

global___EventTypeStats = EventTypeStats

@typing_extensions.final
class EventTypePartial(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    id: builtins.int
    name: builtins.str
    def __init__(
        self,
        *,
        id: builtins.int = ...,
        name: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["id", b"id", "name", b"name"]) -> None: ...

global___EventTypePartial = EventTypePartial

@typing_extensions.final
class EventTypeSummary(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    EVENT_TYPE_FIELD_NUMBER: builtins.int
    STATS_FIELD_NUMBER: builtins.int
    @property
    def event_type(self) -> global___EventTypePartial: ...
    @property
    def stats(self) -> global___EventTypeStats: ...
    def __init__(
        self,
        *,
        event_type: global___EventTypePartial | None = ...,
        stats: global___EventTypeStats | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["event_type", b"event_type", "stats", b"stats"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["event_type", b"event_type", "stats", b"stats"]) -> None: ...

global___EventTypeSummary = EventTypeSummary

@typing_extensions.final
class EventTypeDefinition(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    EVENT_TYPE_FIELD_NUMBER: builtins.int
    STATS_FIELD_NUMBER: builtins.int
    @property
    def event_type(self) -> global___EventType: ...
    @property
    def stats(self) -> global___EventTypeStats: ...
    def __init__(
        self,
        *,
        event_type: global___EventType | None = ...,
        stats: global___EventTypeStats | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["event_type", b"event_type", "stats", b"stats"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["event_type", b"event_type", "stats", b"stats"]) -> None: ...

global___EventTypeDefinition = EventTypeDefinition

@typing_extensions.final
class Event(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _EventSource:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _EventSourceEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[Event._EventSource.ValueType], builtins.type):  # noqa: F821
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        UNKNOWN: Event._EventSource.ValueType  # 0
        SAMPLE: Event._EventSource.ValueType  # 1
        API: Event._EventSource.ValueType  # 2
        SDK: Event._EventSource.ValueType  # 3
        SEGMENT: Event._EventSource.ValueType  # 4
        AMPLITUDE: Event._EventSource.ValueType  # 5
        SNS: Event._EventSource.ValueType  # 6
        CLOUDWATCH: Event._EventSource.ValueType  # 7
        COLLECTOR: Event._EventSource.ValueType  # 8
        AWS_KINESIS: Event._EventSource.ValueType  # 9

    class EventSource(_EventSource, metaclass=_EventSourceEnumTypeWrapper): ...
    UNKNOWN: Event.EventSource.ValueType  # 0
    SAMPLE: Event.EventSource.ValueType  # 1
    API: Event.EventSource.ValueType  # 2
    SDK: Event.EventSource.ValueType  # 3
    SEGMENT: Event.EventSource.ValueType  # 4
    AMPLITUDE: Event.EventSource.ValueType  # 5
    SNS: Event.EventSource.ValueType  # 6
    CLOUDWATCH: Event.EventSource.ValueType  # 7
    COLLECTOR: Event.EventSource.ValueType  # 8
    AWS_KINESIS: Event.EventSource.ValueType  # 9

    ID_FIELD_NUMBER: builtins.int
    EVENT_TYPE_FIELD_NUMBER: builtins.int
    KVS_FIELD_NUMBER: builtins.int
    TIMESTAMP_FIELD_NUMBER: builtins.int
    EVENT_SOURCE_FIELD_NUMBER: builtins.int
    id: builtins.int
    @property
    def event_type(self) -> global___EventTypePartial: ...
    @property
    def kvs(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[protos.event.schema_pb2.KeyValue]: ...
    timestamp: builtins.int
    event_source: global___Event.EventSource.ValueType
    def __init__(
        self,
        *,
        id: builtins.int = ...,
        event_type: global___EventTypePartial | None = ...,
        kvs: collections.abc.Iterable[protos.event.schema_pb2.KeyValue] | None = ...,
        timestamp: builtins.int = ...,
        event_source: global___Event.EventSource.ValueType = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["event_type", b"event_type"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["event_source", b"event_source", "event_type", b"event_type", "id", b"id", "kvs", b"kvs", "timestamp", b"timestamp"]) -> None: ...

global___Event = Event
