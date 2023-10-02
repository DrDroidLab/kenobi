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
import protos.event.base_pb2
import protos.event.monitor_pb2
import protos.event.schema_pb2
import sys

if sys.version_info >= (3, 8):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class DiscoveredEntityInstance(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ACCOUNT_ID_FIELD_NUMBER: builtins.int
    ENTITY_INSTANCE_ID_FIELD_NUMBER: builtins.int
    ENTITY_ID_FIELD_NUMBER: builtins.int
    INSTANCE_FIELD_NUMBER: builtins.int
    @property
    def account_id(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def entity_instance_id(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def entity_id(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def instance(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        account_id: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        entity_instance_id: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        entity_id: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        instance: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["account_id", b"account_id", "entity_id", b"entity_id", "entity_instance_id", b"entity_instance_id", "instance", b"instance"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["account_id", b"account_id", "entity_id", b"entity_id", "entity_instance_id", b"entity_instance_id", "instance", b"instance"]) -> None: ...

global___DiscoveredEntityInstance = DiscoveredEntityInstance

@typing_extensions.final
class ProcessedIngestionEvent(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class ProcessedKeyValue(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        ID_FIELD_NUMBER: builtins.int
        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        @property
        def id(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
        @property
        def key(self) -> google.protobuf.wrappers_pb2.StringValue: ...
        @property
        def value(self) -> protos.event.schema_pb2.Value: ...
        def __init__(
            self,
            *,
            id: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
            key: google.protobuf.wrappers_pb2.StringValue | None = ...,
            value: protos.event.schema_pb2.Value | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["id", b"id", "key", b"key", "value", b"value"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["id", b"id", "key", b"key", "value", b"value"]) -> None: ...

    ACCOUNT_ID_FIELD_NUMBER: builtins.int
    ID_FIELD_NUMBER: builtins.int
    EVENT_TYPE_FIELD_NUMBER: builtins.int
    KVS_FIELD_NUMBER: builtins.int
    TIMESTAMP_FIELD_NUMBER: builtins.int
    EVENT_SOURCE_FIELD_NUMBER: builtins.int
    @property
    def account_id(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def id(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def event_type(self) -> protos.event.base_pb2.EventTypePartial: ...
    @property
    def kvs(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___ProcessedIngestionEvent.ProcessedKeyValue]: ...
    timestamp: builtins.int
    """ Timestamp in milliseconds"""
    event_source: protos.event.base_pb2.Event.EventSource.ValueType
    def __init__(
        self,
        *,
        account_id: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        id: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        event_type: protos.event.base_pb2.EventTypePartial | None = ...,
        kvs: collections.abc.Iterable[global___ProcessedIngestionEvent.ProcessedKeyValue] | None = ...,
        timestamp: builtins.int = ...,
        event_source: protos.event.base_pb2.Event.EventSource.ValueType = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["account_id", b"account_id", "event_type", b"event_type", "id", b"id"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["account_id", b"account_id", "event_source", b"event_source", "event_type", b"event_type", "id", b"id", "kvs", b"kvs", "timestamp", b"timestamp"]) -> None: ...

global___ProcessedIngestionEvent = ProcessedIngestionEvent

@typing_extensions.final
class ProcessedMonitorTransaction(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ACCOUNT_ID_FIELD_NUMBER: builtins.int
    MONITOR_TRANSACTION_FIELD_NUMBER: builtins.int
    MONITOR_TRANSACTION_STATUS_FIELD_NUMBER: builtins.int
    INGESTION_EVENT_FIELD_NUMBER: builtins.int
    MONITOR_TRANSACTION_EVENT_TYPE_FIELD_NUMBER: builtins.int
    TRANSACTION_TIME_FIELD_NUMBER: builtins.int
    @property
    def account_id(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def monitor_transaction(self) -> protos.event.monitor_pb2.MonitorTransactionPartial: ...
    monitor_transaction_status: protos.event.monitor_pb2.MonitorTransaction.MonitorTransactionStatus.ValueType
    @property
    def ingestion_event(self) -> global___ProcessedIngestionEvent: ...
    monitor_transaction_event_type: protos.event.monitor_pb2.MonitorTransaction.MonitorTransactionEventType.ValueType
    @property
    def transaction_time(self) -> google.protobuf.wrappers_pb2.DoubleValue: ...
    def __init__(
        self,
        *,
        account_id: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        monitor_transaction: protos.event.monitor_pb2.MonitorTransactionPartial | None = ...,
        monitor_transaction_status: protos.event.monitor_pb2.MonitorTransaction.MonitorTransactionStatus.ValueType = ...,
        ingestion_event: global___ProcessedIngestionEvent | None = ...,
        monitor_transaction_event_type: protos.event.monitor_pb2.MonitorTransaction.MonitorTransactionEventType.ValueType = ...,
        transaction_time: google.protobuf.wrappers_pb2.DoubleValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["account_id", b"account_id", "ingestion_event", b"ingestion_event", "monitor_transaction", b"monitor_transaction", "transaction_time", b"transaction_time"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["account_id", b"account_id", "ingestion_event", b"ingestion_event", "monitor_transaction", b"monitor_transaction", "monitor_transaction_event_type", b"monitor_transaction_event_type", "monitor_transaction_status", b"monitor_transaction_status", "transaction_time", b"transaction_time"]) -> None: ...

global___ProcessedMonitorTransaction = ProcessedMonitorTransaction
