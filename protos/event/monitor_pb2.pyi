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
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class MonitorStats(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class PercentilesEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: builtins.str
        value: builtins.float
        def __init__(
            self,
            *,
            key: builtins.str = ...,
            value: builtins.float = ...,
        ) -> None: ...
        def ClearField(self, field_name: typing_extensions.Literal["key", b"key", "value", b"value"]) -> None: ...

    TRANSACTION_COUNT_FIELD_NUMBER: builtins.int
    FINISHED_TRANSACTION_COUNT_FIELD_NUMBER: builtins.int
    TRANSACTION_AVG_DELAY_FIELD_NUMBER: builtins.int
    PERCENTILES_FIELD_NUMBER: builtins.int
    @property
    def transaction_count(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def finished_transaction_count(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def transaction_avg_delay(self) -> google.protobuf.wrappers_pb2.DoubleValue: ...
    @property
    def percentiles(self) -> google.protobuf.internal.containers.ScalarMap[builtins.str, builtins.float]: ...
    def __init__(
        self,
        *,
        transaction_count: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        finished_transaction_count: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        transaction_avg_delay: google.protobuf.wrappers_pb2.DoubleValue | None = ...,
        percentiles: collections.abc.Mapping[builtins.str, builtins.float] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["finished_transaction_count", b"finished_transaction_count", "transaction_avg_delay", b"transaction_avg_delay", "transaction_count", b"transaction_count"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["finished_transaction_count", b"finished_transaction_count", "percentiles", b"percentiles", "transaction_avg_delay", b"transaction_avg_delay", "transaction_count", b"transaction_count"]) -> None: ...

global___MonitorStats = MonitorStats

@typing_extensions.final
class MonitorPartial(google.protobuf.message.Message):
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

global___MonitorPartial = MonitorPartial

@typing_extensions.final
class Monitor(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    PRIMARY_EVENT_KEY_FIELD_NUMBER: builtins.int
    SECONDARY_EVENT_KEY_FIELD_NUMBER: builtins.int
    CREATED_AT_FIELD_NUMBER: builtins.int
    IS_ACTIVE_FIELD_NUMBER: builtins.int
    id: builtins.int
    name: builtins.str
    @property
    def primary_event_key(self) -> protos.event.base_pb2.EventKey: ...
    @property
    def secondary_event_key(self) -> protos.event.base_pb2.EventKey: ...
    created_at: builtins.int
    @property
    def is_active(self) -> google.protobuf.wrappers_pb2.BoolValue: ...
    def __init__(
        self,
        *,
        id: builtins.int = ...,
        name: builtins.str = ...,
        primary_event_key: protos.event.base_pb2.EventKey | None = ...,
        secondary_event_key: protos.event.base_pb2.EventKey | None = ...,
        created_at: builtins.int = ...,
        is_active: google.protobuf.wrappers_pb2.BoolValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["is_active", b"is_active", "primary_event_key", b"primary_event_key", "secondary_event_key", b"secondary_event_key"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["created_at", b"created_at", "id", b"id", "is_active", b"is_active", "name", b"name", "primary_event_key", b"primary_event_key", "secondary_event_key", b"secondary_event_key"]) -> None: ...

global___Monitor = Monitor

@typing_extensions.final
class MonitorDefinition(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    MONITOR_FIELD_NUMBER: builtins.int
    STATS_FIELD_NUMBER: builtins.int
    @property
    def monitor(self) -> global___Monitor: ...
    @property
    def stats(self) -> global___MonitorStats: ...
    def __init__(
        self,
        *,
        monitor: global___Monitor | None = ...,
        stats: global___MonitorStats | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["monitor", b"monitor", "stats", b"stats"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["monitor", b"monitor", "stats", b"stats"]) -> None: ...

global___MonitorDefinition = MonitorDefinition

@typing_extensions.final
class MonitorEventTypeDetails(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    MONITOR_FIELD_NUMBER: builtins.int
    PRIMARY_EVENT_TYPE_FIELD_NUMBER: builtins.int
    SECONDARY_EVENT_TYPE_FIELD_NUMBER: builtins.int
    @property
    def monitor(self) -> global___MonitorPartial: ...
    @property
    def primary_event_type(self) -> protos.event.base_pb2.EventTypePartial: ...
    @property
    def secondary_event_type(self) -> protos.event.base_pb2.EventTypePartial: ...
    def __init__(
        self,
        *,
        monitor: global___MonitorPartial | None = ...,
        primary_event_type: protos.event.base_pb2.EventTypePartial | None = ...,
        secondary_event_type: protos.event.base_pb2.EventTypePartial | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["monitor", b"monitor", "primary_event_type", b"primary_event_type", "secondary_event_type", b"secondary_event_type"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["monitor", b"monitor", "primary_event_type", b"primary_event_type", "secondary_event_type", b"secondary_event_type"]) -> None: ...

global___MonitorEventTypeDetails = MonitorEventTypeDetails

@typing_extensions.final
class MonitorTransactionGetParams(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TRANSACTION_IDS_FIELD_NUMBER: builtins.int
    TRANSACTIONS_FIELD_NUMBER: builtins.int
    TRANSACTION_STATUS_FIELD_NUMBER: builtins.int
    @property
    def transaction_ids(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.int]: ...
    @property
    def transactions(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    transaction_status: global___MonitorTransaction.MonitorTransactionStatus.ValueType
    def __init__(
        self,
        *,
        transaction_ids: collections.abc.Iterable[builtins.int] | None = ...,
        transactions: collections.abc.Iterable[builtins.str] | None = ...,
        transaction_status: global___MonitorTransaction.MonitorTransactionStatus.ValueType = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["transaction_ids", b"transaction_ids", "transaction_status", b"transaction_status", "transactions", b"transactions"]) -> None: ...

global___MonitorTransactionGetParams = MonitorTransactionGetParams

@typing_extensions.final
class MonitorTransaction(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _MonitorTransactionEventType:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _MonitorTransactionEventTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[MonitorTransaction._MonitorTransactionEventType.ValueType], builtins.type):  # noqa: F821
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        UNKNOWN_MT_ET: MonitorTransaction._MonitorTransactionEventType.ValueType  # 0
        PRIMARY: MonitorTransaction._MonitorTransactionEventType.ValueType  # 1
        SECONDARY: MonitorTransaction._MonitorTransactionEventType.ValueType  # 2

    class MonitorTransactionEventType(_MonitorTransactionEventType, metaclass=_MonitorTransactionEventTypeEnumTypeWrapper): ...
    UNKNOWN_MT_ET: MonitorTransaction.MonitorTransactionEventType.ValueType  # 0
    PRIMARY: MonitorTransaction.MonitorTransactionEventType.ValueType  # 1
    SECONDARY: MonitorTransaction.MonitorTransactionEventType.ValueType  # 2

    class _MonitorTransactionStatus:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _MonitorTransactionStatusEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[MonitorTransaction._MonitorTransactionStatus.ValueType], builtins.type):  # noqa: F821
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        UNKNOWN: MonitorTransaction._MonitorTransactionStatus.ValueType  # 0
        PRIMARY_RECEIVED: MonitorTransaction._MonitorTransactionStatus.ValueType  # 1
        SECONDARY_RECEIVED: MonitorTransaction._MonitorTransactionStatus.ValueType  # 2

    class MonitorTransactionStatus(_MonitorTransactionStatus, metaclass=_MonitorTransactionStatusEnumTypeWrapper): ...
    UNKNOWN: MonitorTransaction.MonitorTransactionStatus.ValueType  # 0
    PRIMARY_RECEIVED: MonitorTransaction.MonitorTransactionStatus.ValueType  # 1
    SECONDARY_RECEIVED: MonitorTransaction.MonitorTransactionStatus.ValueType  # 2

    ID_FIELD_NUMBER: builtins.int
    TRANSACTION_FIELD_NUMBER: builtins.int
    MONITOR_FIELD_NUMBER: builtins.int
    CREATED_AT_FIELD_NUMBER: builtins.int
    STATUS_FIELD_NUMBER: builtins.int
    HAS_ALERTS_FIELD_NUMBER: builtins.int
    TRANSACTION_AGE_FIELD_NUMBER: builtins.int
    TRANSACTION_TIME_FIELD_NUMBER: builtins.int
    id: builtins.int
    transaction: builtins.str
    @property
    def monitor(self) -> global___MonitorPartial: ...
    created_at: builtins.int
    status: global___MonitorTransaction.MonitorTransactionStatus.ValueType
    @property
    def has_alerts(self) -> google.protobuf.wrappers_pb2.BoolValue: ...
    @property
    def transaction_age(self) -> google.protobuf.wrappers_pb2.DoubleValue: ...
    @property
    def transaction_time(self) -> google.protobuf.wrappers_pb2.DoubleValue: ...
    def __init__(
        self,
        *,
        id: builtins.int = ...,
        transaction: builtins.str = ...,
        monitor: global___MonitorPartial | None = ...,
        created_at: builtins.int = ...,
        status: global___MonitorTransaction.MonitorTransactionStatus.ValueType = ...,
        has_alerts: google.protobuf.wrappers_pb2.BoolValue | None = ...,
        transaction_age: google.protobuf.wrappers_pb2.DoubleValue | None = ...,
        transaction_time: google.protobuf.wrappers_pb2.DoubleValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["has_alerts", b"has_alerts", "monitor", b"monitor", "transaction_age", b"transaction_age", "transaction_time", b"transaction_time"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["created_at", b"created_at", "has_alerts", b"has_alerts", "id", b"id", "monitor", b"monitor", "status", b"status", "transaction", b"transaction", "transaction_age", b"transaction_age", "transaction_time", b"transaction_time"]) -> None: ...

global___MonitorTransaction = MonitorTransaction

@typing_extensions.final
class MonitorTransactionStats(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TRANSACTION_TIME_FIELD_NUMBER: builtins.int
    PRIMARY_EVENT_MISSING_FIELD_NUMBER: builtins.int
    @property
    def transaction_time(self) -> google.protobuf.wrappers_pb2.DoubleValue: ...
    @property
    def primary_event_missing(self) -> google.protobuf.wrappers_pb2.BoolValue: ...
    def __init__(
        self,
        *,
        transaction_time: google.protobuf.wrappers_pb2.DoubleValue | None = ...,
        primary_event_missing: google.protobuf.wrappers_pb2.BoolValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["primary_event_missing", b"primary_event_missing", "transaction_time", b"transaction_time"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["primary_event_missing", b"primary_event_missing", "transaction_time", b"transaction_time"]) -> None: ...

global___MonitorTransactionStats = MonitorTransactionStats

@typing_extensions.final
class MonitorTransactionDetails(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    MONITOR_TRANSACTION_FIELD_NUMBER: builtins.int
    STATS_FIELD_NUMBER: builtins.int
    @property
    def monitor_transaction(self) -> global___MonitorTransaction: ...
    @property
    def stats(self) -> global___MonitorTransactionStats: ...
    def __init__(
        self,
        *,
        monitor_transaction: global___MonitorTransaction | None = ...,
        stats: global___MonitorTransactionStats | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["monitor_transaction", b"monitor_transaction", "stats", b"stats"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["monitor_transaction", b"monitor_transaction", "stats", b"stats"]) -> None: ...

global___MonitorTransactionDetails = MonitorTransactionDetails

@typing_extensions.final
class MonitorTransactionPartial(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    TRANSACTION_FIELD_NUMBER: builtins.int
    MONITOR_FIELD_NUMBER: builtins.int
    @property
    def id(self) -> google.protobuf.wrappers_pb2.UInt64Value: ...
    @property
    def transaction(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def monitor(self) -> global___MonitorPartial: ...
    def __init__(
        self,
        *,
        id: google.protobuf.wrappers_pb2.UInt64Value | None = ...,
        transaction: google.protobuf.wrappers_pb2.StringValue | None = ...,
        monitor: global___MonitorPartial | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["id", b"id", "monitor", b"monitor", "transaction", b"transaction"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["id", b"id", "monitor", b"monitor", "transaction", b"transaction"]) -> None: ...

global___MonitorTransactionPartial = MonitorTransactionPartial

@typing_extensions.final
class UpdateMonitorOp(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _Op:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _OpEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[UpdateMonitorOp._Op.ValueType], builtins.type):  # noqa: F821
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        UNKNOWN: UpdateMonitorOp._Op.ValueType  # 0
        UPDATE_MONITOR_NAME: UpdateMonitorOp._Op.ValueType  # 1
        UPDATE_MONITOR_PRIMARY_KEY: UpdateMonitorOp._Op.ValueType  # 2
        UPDATE_MONITOR_SECONDARY_KEY: UpdateMonitorOp._Op.ValueType  # 3
        UPDATE_MONITOR_STATUS: UpdateMonitorOp._Op.ValueType  # 4
        UPDATE_MONITOR_IS_GENERATED: UpdateMonitorOp._Op.ValueType  # 5

    class Op(_Op, metaclass=_OpEnumTypeWrapper): ...
    UNKNOWN: UpdateMonitorOp.Op.ValueType  # 0
    UPDATE_MONITOR_NAME: UpdateMonitorOp.Op.ValueType  # 1
    UPDATE_MONITOR_PRIMARY_KEY: UpdateMonitorOp.Op.ValueType  # 2
    UPDATE_MONITOR_SECONDARY_KEY: UpdateMonitorOp.Op.ValueType  # 3
    UPDATE_MONITOR_STATUS: UpdateMonitorOp.Op.ValueType  # 4
    UPDATE_MONITOR_IS_GENERATED: UpdateMonitorOp.Op.ValueType  # 5

    @typing_extensions.final
    class UpdateMonitorName(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        NAME_FIELD_NUMBER: builtins.int
        @property
        def name(self) -> google.protobuf.wrappers_pb2.StringValue: ...
        def __init__(
            self,
            *,
            name: google.protobuf.wrappers_pb2.StringValue | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["name", b"name"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["name", b"name"]) -> None: ...

    @typing_extensions.final
    class UpdateMonitorPrimaryKey(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        PRIMARY_EVENT_KEY_FIELD_NUMBER: builtins.int
        @property
        def primary_event_key(self) -> protos.event.base_pb2.EventKey: ...
        def __init__(
            self,
            *,
            primary_event_key: protos.event.base_pb2.EventKey | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["primary_event_key", b"primary_event_key"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["primary_event_key", b"primary_event_key"]) -> None: ...

    @typing_extensions.final
    class UpdateMonitorSecondaryKey(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        SECONDARY_EVENT_KEY_FIELD_NUMBER: builtins.int
        @property
        def secondary_event_key(self) -> protos.event.base_pb2.EventKey: ...
        def __init__(
            self,
            *,
            secondary_event_key: protos.event.base_pb2.EventKey | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["secondary_event_key", b"secondary_event_key"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["secondary_event_key", b"secondary_event_key"]) -> None: ...

    @typing_extensions.final
    class UpdateMonitorStatus(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        IS_ACTIVE_FIELD_NUMBER: builtins.int
        @property
        def is_active(self) -> google.protobuf.wrappers_pb2.BoolValue: ...
        def __init__(
            self,
            *,
            is_active: google.protobuf.wrappers_pb2.BoolValue | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["is_active", b"is_active"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["is_active", b"is_active"]) -> None: ...

    @typing_extensions.final
    class UpdateMonitorIsGenerated(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        IS_GENERATED_FIELD_NUMBER: builtins.int
        @property
        def is_generated(self) -> google.protobuf.wrappers_pb2.BoolValue: ...
        def __init__(
            self,
            *,
            is_generated: google.protobuf.wrappers_pb2.BoolValue | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["is_generated", b"is_generated"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["is_generated", b"is_generated"]) -> None: ...

    OP_FIELD_NUMBER: builtins.int
    UPDATE_MONITOR_NAME_FIELD_NUMBER: builtins.int
    UPDATE_MONITOR_PRIMARY_KEY_FIELD_NUMBER: builtins.int
    UPDATE_MONITOR_SECONDARY_KEY_FIELD_NUMBER: builtins.int
    UPDATE_MONITOR_STATUS_FIELD_NUMBER: builtins.int
    UPDATE_MONITOR_IS_GENERATED_FIELD_NUMBER: builtins.int
    op: global___UpdateMonitorOp.Op.ValueType
    @property
    def update_monitor_name(self) -> global___UpdateMonitorOp.UpdateMonitorName: ...
    @property
    def update_monitor_primary_key(self) -> global___UpdateMonitorOp.UpdateMonitorPrimaryKey: ...
    @property
    def update_monitor_secondary_key(self) -> global___UpdateMonitorOp.UpdateMonitorSecondaryKey: ...
    @property
    def update_monitor_status(self) -> global___UpdateMonitorOp.UpdateMonitorStatus: ...
    @property
    def update_monitor_is_generated(self) -> global___UpdateMonitorOp.UpdateMonitorIsGenerated: ...
    def __init__(
        self,
        *,
        op: global___UpdateMonitorOp.Op.ValueType = ...,
        update_monitor_name: global___UpdateMonitorOp.UpdateMonitorName | None = ...,
        update_monitor_primary_key: global___UpdateMonitorOp.UpdateMonitorPrimaryKey | None = ...,
        update_monitor_secondary_key: global___UpdateMonitorOp.UpdateMonitorSecondaryKey | None = ...,
        update_monitor_status: global___UpdateMonitorOp.UpdateMonitorStatus | None = ...,
        update_monitor_is_generated: global___UpdateMonitorOp.UpdateMonitorIsGenerated | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["update", b"update", "update_monitor_is_generated", b"update_monitor_is_generated", "update_monitor_name", b"update_monitor_name", "update_monitor_primary_key", b"update_monitor_primary_key", "update_monitor_secondary_key", b"update_monitor_secondary_key", "update_monitor_status", b"update_monitor_status"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["op", b"op", "update", b"update", "update_monitor_is_generated", b"update_monitor_is_generated", "update_monitor_name", b"update_monitor_name", "update_monitor_primary_key", b"update_monitor_primary_key", "update_monitor_secondary_key", b"update_monitor_secondary_key", "update_monitor_status", b"update_monitor_status"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["update", b"update"]) -> typing_extensions.Literal["update_monitor_name", "update_monitor_primary_key", "update_monitor_secondary_key", "update_monitor_status", "update_monitor_is_generated"] | None: ...

global___UpdateMonitorOp = UpdateMonitorOp