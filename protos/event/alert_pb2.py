# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/event/alert.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from protos.event import trigger_pb2 as protos_dot_event_dot_trigger__pb2
from protos.event import monitor_pb2 as protos_dot_event_dot_monitor__pb2
from protos.event import entity_pb2 as protos_dot_event_dot_entity__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18protos/event/alert.proto\x12\x0cprotos.event\x1a\x1aprotos/event/trigger.proto\x1a\x1aprotos/event/monitor.proto\x1a\x19protos/event/entity.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/wrappers.proto\"\x94\x01\n\x0c\x41lertSummary\x12\n\n\x02id\x18\x01 \x01(\x04\x12-\n\x07trigger\x18\x02 \x01(\x0b\x32\x1c.protos.event.TriggerSummary\x12\x33\n\x0e\x65ntity_trigger\x18\x03 \x01(\x0b\x32\x1b.protos.event.EntityTrigger\x12\x14\n\x0ctriggered_at\x18\x04 \x01(\x10\"\xdc\x03\n\nAlertStats\x12=\n\x17total_transaction_count\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12>\n\x18missed_transaction_count\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12?\n\x19\x64\x65layed_transaction_count\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x32\n\x0cmedian_delay\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.DoubleValue\x12\x30\n\nevent_name\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\x0e\x65vent_key_name\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x35\n\x0f\x65vent_timestamp\x18\x07 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12;\n\x15\x65ntity_instance_value\x18\x08 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xd1\x01\n\x0b\x41lertDetail\x12\n\n\x02id\x18\x01 \x01(\x04\x12&\n\x07trigger\x18\x02 \x01(\x0b\x32\x15.protos.event.Trigger\x12\x33\n\x0e\x65ntity_trigger\x18\x03 \x01(\x0b\x32\x1b.protos.event.EntityTrigger\x12\x30\n\x0ctriggered_at\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\'\n\x05stats\x18\x05 \x01(\x0b\x32\x18.protos.event.AlertStats\"V\n\x1e\x44\x65layedMonitorTransactionStats\x12\x34\n\x0e\x64\x65lay_duration\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.DoubleValue\"\xe4\x02\n\x17\x41lertMonitorTransaction\x12\x38\n\x04type\x18\x01 \x01(\x0e\x32*.protos.event.AlertMonitorTransaction.Type\x12=\n\x13monitor_transaction\x18\x02 \x01(\x0b\x32 .protos.event.MonitorTransaction\x12\x10\n\x08\x61lert_id\x18\x03 \x01(\x04\x12Y\n!delayed_monitor_transaction_stats\x18\x04 \x01(\x0b\x32,.protos.event.DelayedMonitorTransactionStatsH\x00\x12\x14\n\x0ctrigger_name\x18\x05 \x01(\t\"D\n\x04Type\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x16\n\x12MISSED_TRANSACTION\x10\x01\x12\x17\n\x13\x44\x45LAYED_TRANSACTION\x10\x02\x42\x07\n\x05stats\"\xe5\x01\n\x13\x41lertEntityInstance\x12\x34\n\x04type\x18\x01 \x01(\x0e\x32&.protos.event.AlertEntityInstance.Type\x12\x35\n\x0f\x65ntity_instance\x18\x02 \x01(\x0b\x32\x1c.protos.event.EntityInstance\x12\x10\n\x08\x61lert_id\x18\x03 \x01(\x04\x12\x14\n\x0ctrigger_name\x18\x04 \x01(\t\"9\n\x04Type\x12\x0b\n\x07UNKNOWN\x10\x00\x12\r\n\tPER_EVENT\x10\x01\x12\x15\n\x11\x41GGREGATED_EVENTS\x10\x02\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.event.alert_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ALERTSUMMARY._serialized_start=191
  _ALERTSUMMARY._serialized_end=339
  _ALERTSTATS._serialized_start=342
  _ALERTSTATS._serialized_end=818
  _ALERTDETAIL._serialized_start=821
  _ALERTDETAIL._serialized_end=1030
  _DELAYEDMONITORTRANSACTIONSTATS._serialized_start=1032
  _DELAYEDMONITORTRANSACTIONSTATS._serialized_end=1118
  _ALERTMONITORTRANSACTION._serialized_start=1121
  _ALERTMONITORTRANSACTION._serialized_end=1477
  _ALERTMONITORTRANSACTION_TYPE._serialized_start=1400
  _ALERTMONITORTRANSACTION_TYPE._serialized_end=1468
  _ALERTENTITYINSTANCE._serialized_start=1480
  _ALERTENTITYINSTANCE._serialized_end=1709
  _ALERTENTITYINSTANCE_TYPE._serialized_start=1652
  _ALERTENTITYINSTANCE_TYPE._serialized_end=1709
# @@protoc_insertion_point(module_scope)
