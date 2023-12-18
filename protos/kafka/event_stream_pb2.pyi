"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import google.protobuf.wrappers_pb2
import protos.event.base_pb2
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class StreamEvent(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _Type:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _TypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[StreamEvent._Type.ValueType], builtins.type):  # noqa: F821
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        UNKNOWN: StreamEvent._Type.ValueType  # 0
        STRING: StreamEvent._Type.ValueType  # 1
        JSON: StreamEvent._Type.ValueType  # 2

    class Type(_Type, metaclass=_TypeEnumTypeWrapper): ...
    UNKNOWN: StreamEvent.Type.ValueType  # 0
    STRING: StreamEvent.Type.ValueType  # 1
    JSON: StreamEvent.Type.ValueType  # 2

    UUID_STR_FIELD_NUMBER: builtins.int
    EVENT_FIELD_NUMBER: builtins.int
    EVENT_SOURCE_FIELD_NUMBER: builtins.int
    RECORDED_INGESTION_TIMESTAMP_FIELD_NUMBER: builtins.int
    TYPE_FIELD_NUMBER: builtins.int
    @property
    def uuid_str(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def event(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    event_source: protos.event.base_pb2.Event.EventSource.ValueType
    recorded_ingestion_timestamp: builtins.int
    type: global___StreamEvent.Type.ValueType
    def __init__(
        self,
        *,
        uuid_str: google.protobuf.wrappers_pb2.StringValue | None = ...,
        event: google.protobuf.wrappers_pb2.StringValue | None = ...,
        event_source: protos.event.base_pb2.Event.EventSource.ValueType = ...,
        recorded_ingestion_timestamp: builtins.int = ...,
        type: global___StreamEvent.Type.ValueType = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["event", b"event", "uuid_str", b"uuid_str"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["event", b"event", "event_source", b"event_source", "recorded_ingestion_timestamp", b"recorded_ingestion_timestamp", "type", b"type", "uuid_str", b"uuid_str"]) -> None: ...

global___StreamEvent = StreamEvent

@typing_extensions.final
class RawEventStreamPayloadKey(google.protobuf.message.Message):
    """Publish on `raw-event-stream` topic"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(
        self,
    ) -> None: ...

global___RawEventStreamPayloadKey = RawEventStreamPayloadKey

@typing_extensions.final
class RawEventStreamPayloadValue(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ACCOUNT_ID_FIELD_NUMBER: builtins.int
    EVENT_FIELD_NUMBER: builtins.int
    @property
    def account_id(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def event(self) -> global___StreamEvent: ...
    def __init__(
        self,
        *,
        account_id: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        event: global___StreamEvent | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["account_id", b"account_id", "event", b"event"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["account_id", b"account_id", "event", b"event"]) -> None: ...

global___RawEventStreamPayloadValue = RawEventStreamPayloadValue

@typing_extensions.final
class FilteredEventStreamPayloadKey(google.protobuf.message.Message):
    """Publish on `filtered-event-stream` topic"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(
        self,
    ) -> None: ...

global___FilteredEventStreamPayloadKey = FilteredEventStreamPayloadKey

@typing_extensions.final
class FilteredEventStreamPayloadValue(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ACCOUNT_ID_FIELD_NUMBER: builtins.int
    FILTER_ID_FIELD_NUMBER: builtins.int
    EVENT_FIELD_NUMBER: builtins.int
    @property
    def account_id(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def filter_id(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def event(self) -> global___StreamEvent: ...
    def __init__(
        self,
        *,
        account_id: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        filter_id: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        event: global___StreamEvent | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["account_id", b"account_id", "event", b"event", "filter_id", b"filter_id"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["account_id", b"account_id", "event", b"event", "filter_id", b"filter_id"]) -> None: ...

global___FilteredEventStreamPayloadValue = FilteredEventStreamPayloadValue
