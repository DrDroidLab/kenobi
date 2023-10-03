# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/event/monitor.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from protos.event import base_pb2 as protos_dot_event_dot_base__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1aprotos/event/monitor.proto\x12\x0cprotos.event\x1a\x17protos/event/base.proto\x1a\x1egoogle/protobuf/wrappers.proto\"\xbc\x02\n\x0cMonitorStats\x12\x37\n\x11transaction_count\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12@\n\x1a\x66inished_transaction_count\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12;\n\x15transaction_avg_delay\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.DoubleValue\x12@\n\x0bpercentiles\x18\x04 \x03(\x0b\x32+.protos.event.MonitorStats.PercentilesEntry\x1a\x32\n\x10PercentilesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x02:\x02\x38\x01\"*\n\x0eMonitorPartial\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x0c\n\x04name\x18\x02 \x01(\t\"\xce\x01\n\x07Monitor\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x31\n\x11primary_event_key\x18\x04 \x01(\x0b\x32\x16.protos.event.EventKey\x12\x33\n\x13secondary_event_key\x18\x06 \x01(\x0b\x32\x16.protos.event.EventKey\x12\x12\n\ncreated_at\x18\x07 \x01(\x10\x12-\n\tis_active\x18\x08 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\"f\n\x11MonitorDefinition\x12&\n\x07monitor\x18\x01 \x01(\x0b\x32\x15.protos.event.Monitor\x12)\n\x05stats\x18\x02 \x01(\x0b\x32\x1a.protos.event.MonitorStats\"\xc2\x01\n\x17MonitorEventTypeDetails\x12-\n\x07monitor\x18\x01 \x01(\x0b\x32\x1c.protos.event.MonitorPartial\x12:\n\x12primary_event_type\x18\x02 \x01(\x0b\x32\x1e.protos.event.EventTypePartial\x12<\n\x14secondary_event_type\x18\x03 \x01(\x0b\x32\x1e.protos.event.EventTypePartial\"\xa3\x01\n\x1bMonitorTransactionGetParams\x12\x17\n\x0ftransaction_ids\x18\x01 \x03(\x04\x12\x14\n\x0ctransactions\x18\x02 \x03(\t\x12U\n\x12transaction_status\x18\x03 \x01(\x0e\x32\x39.protos.event.MonitorTransaction.MonitorTransactionStatus\"\x87\x04\n\x12MonitorTransaction\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x13\n\x0btransaction\x18\x02 \x01(\t\x12-\n\x07monitor\x18\x03 \x01(\x0b\x32\x1c.protos.event.MonitorPartial\x12\x12\n\ncreated_at\x18\x04 \x01(\x10\x12I\n\x06status\x18\x05 \x01(\x0e\x32\x39.protos.event.MonitorTransaction.MonitorTransactionStatus\x12.\n\nhas_alerts\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x35\n\x0ftransaction_age\x18\x07 \x01(\x0b\x32\x1c.google.protobuf.DoubleValue\x12\x36\n\x10transaction_time\x18\x08 \x01(\x0b\x32\x1c.google.protobuf.DoubleValue\"L\n\x1bMonitorTransactionEventType\x12\x11\n\rUNKNOWN_MT_ET\x10\x00\x12\x0b\n\x07PRIMARY\x10\x01\x12\r\n\tSECONDARY\x10\x02\"U\n\x18MonitorTransactionStatus\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x14\n\x10PRIMARY_RECEIVED\x10\x01\x12\x16\n\x12SECONDARY_RECEIVED\x10\x02\"\x8c\x01\n\x17MonitorTransactionStats\x12\x36\n\x10transaction_time\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.DoubleValue\x12\x39\n\x15primary_event_missing\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\"\x90\x01\n\x19MonitorTransactionDetails\x12=\n\x13monitor_transaction\x18\x01 \x01(\x0b\x32 .protos.event.MonitorTransaction\x12\x34\n\x05stats\x18\x02 \x01(\x0b\x32%.protos.event.MonitorTransactionStats\"\xa7\x01\n\x19MonitorTransactionPartial\x12(\n\x02id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x31\n\x0btransaction\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12-\n\x07monitor\x18\x03 \x01(\x0b\x32\x1c.protos.event.MonitorPartial\"\xaa\x08\n\x0fUpdateMonitorOp\x12,\n\x02op\x18\x01 \x01(\x0e\x32 .protos.event.UpdateMonitorOp.Op\x12N\n\x13update_monitor_name\x18\x02 \x01(\x0b\x32/.protos.event.UpdateMonitorOp.UpdateMonitorNameH\x00\x12[\n\x1aupdate_monitor_primary_key\x18\x03 \x01(\x0b\x32\x35.protos.event.UpdateMonitorOp.UpdateMonitorPrimaryKeyH\x00\x12_\n\x1cupdate_monitor_secondary_key\x18\x04 \x01(\x0b\x32\x37.protos.event.UpdateMonitorOp.UpdateMonitorSecondaryKeyH\x00\x12R\n\x15update_monitor_status\x18\x05 \x01(\x0b\x32\x31.protos.event.UpdateMonitorOp.UpdateMonitorStatusH\x00\x12]\n\x1bupdate_monitor_is_generated\x18\x06 \x01(\x0b\x32\x36.protos.event.UpdateMonitorOp.UpdateMonitorIsGeneratedH\x00\x1a?\n\x11UpdateMonitorName\x12*\n\x04name\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x1aL\n\x17UpdateMonitorPrimaryKey\x12\x31\n\x11primary_event_key\x18\x01 \x01(\x0b\x32\x16.protos.event.EventKey\x1aP\n\x19UpdateMonitorSecondaryKey\x12\x33\n\x13secondary_event_key\x18\x01 \x01(\x0b\x32\x16.protos.event.EventKey\x1a\x44\n\x13UpdateMonitorStatus\x12-\n\tis_active\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x1aL\n\x18UpdateMonitorIsGenerated\x12\x30\n\x0cis_generated\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\"\xa8\x01\n\x02Op\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x17\n\x13UPDATE_MONITOR_NAME\x10\x01\x12\x1e\n\x1aUPDATE_MONITOR_PRIMARY_KEY\x10\x02\x12 \n\x1cUPDATE_MONITOR_SECONDARY_KEY\x10\x03\x12\x19\n\x15UPDATE_MONITOR_STATUS\x10\x04\x12\x1f\n\x1bUPDATE_MONITOR_IS_GENERATED\x10\x05\x42\x08\n\x06updateb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.event.monitor_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _MONITORSTATS_PERCENTILESENTRY._options = None
  _MONITORSTATS_PERCENTILESENTRY._serialized_options = b'8\001'
  _MONITORSTATS._serialized_start=102
  _MONITORSTATS._serialized_end=418
  _MONITORSTATS_PERCENTILESENTRY._serialized_start=368
  _MONITORSTATS_PERCENTILESENTRY._serialized_end=418
  _MONITORPARTIAL._serialized_start=420
  _MONITORPARTIAL._serialized_end=462
  _MONITOR._serialized_start=465
  _MONITOR._serialized_end=671
  _MONITORDEFINITION._serialized_start=673
  _MONITORDEFINITION._serialized_end=775
  _MONITOREVENTTYPEDETAILS._serialized_start=778
  _MONITOREVENTTYPEDETAILS._serialized_end=972
  _MONITORTRANSACTIONGETPARAMS._serialized_start=975
  _MONITORTRANSACTIONGETPARAMS._serialized_end=1138
  _MONITORTRANSACTION._serialized_start=1141
  _MONITORTRANSACTION._serialized_end=1660
  _MONITORTRANSACTION_MONITORTRANSACTIONEVENTTYPE._serialized_start=1497
  _MONITORTRANSACTION_MONITORTRANSACTIONEVENTTYPE._serialized_end=1573
  _MONITORTRANSACTION_MONITORTRANSACTIONSTATUS._serialized_start=1575
  _MONITORTRANSACTION_MONITORTRANSACTIONSTATUS._serialized_end=1660
  _MONITORTRANSACTIONSTATS._serialized_start=1663
  _MONITORTRANSACTIONSTATS._serialized_end=1803
  _MONITORTRANSACTIONDETAILS._serialized_start=1806
  _MONITORTRANSACTIONDETAILS._serialized_end=1950
  _MONITORTRANSACTIONPARTIAL._serialized_start=1953
  _MONITORTRANSACTIONPARTIAL._serialized_end=2120
  _UPDATEMONITOROP._serialized_start=2123
  _UPDATEMONITOROP._serialized_end=3189
  _UPDATEMONITOROP_UPDATEMONITORNAME._serialized_start=2637
  _UPDATEMONITOROP_UPDATEMONITORNAME._serialized_end=2700
  _UPDATEMONITOROP_UPDATEMONITORPRIMARYKEY._serialized_start=2702
  _UPDATEMONITOROP_UPDATEMONITORPRIMARYKEY._serialized_end=2778
  _UPDATEMONITOROP_UPDATEMONITORSECONDARYKEY._serialized_start=2780
  _UPDATEMONITOROP_UPDATEMONITORSECONDARYKEY._serialized_end=2860
  _UPDATEMONITOROP_UPDATEMONITORSTATUS._serialized_start=2862
  _UPDATEMONITOROP_UPDATEMONITORSTATUS._serialized_end=2930
  _UPDATEMONITOROP_UPDATEMONITORISGENERATED._serialized_start=2932
  _UPDATEMONITOROP_UPDATEMONITORISGENERATED._serialized_end=3008
  _UPDATEMONITOROP_OP._serialized_start=3011
  _UPDATEMONITOROP_OP._serialized_end=3179
# @@protoc_insertion_point(module_scope)