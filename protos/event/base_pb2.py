# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/event/base.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from protos.event import schema_pb2 as protos_dot_event_dot_schema__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17protos/event/base.proto\x12\x0cprotos.event\x1a\x19protos/event/schema.proto\x1a\x1egoogle/protobuf/wrappers.proto\".\n\tTimeRange\x12\x10\n\x08time_geq\x18\x01 \x01(\x04\x12\x0f\n\x07time_lt\x18\x02 \x01(\x04\"a\n\x04Page\x12+\n\x05limit\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\x12,\n\x06offset\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\"\xf1\x01\n\x08\x45ventKey\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x0b\n\x03key\x18\x02 \x01(\t\x12\x30\n\x08key_type\x18\x03 \x01(\x0e\x32\x1e.protos.event.EventKey.KeyType\x12\x32\n\nevent_type\x18\x04 \x01(\x0b\x32\x1e.protos.event.EventTypePartial\"f\n\x07KeyType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\n\n\x06STRING\x10\x01\x12\x08\n\x04LONG\x10\x02\x12\n\n\x06\x44OUBLE\x10\x03\x12\x0b\n\x07\x42OOLEAN\x10\x04\x12\x08\n\x04\x42YTE\x10\x05\x12\t\n\x05\x41RRAY\x10\x06\x12\n\n\x06OBJECT\x10\x07\"\x83\x01\n\tEventType\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x0c\n\x04name\x18\x02 \x01(\t\x12$\n\x04keys\x18\x03 \x03(\x0b\x32\x16.protos.event.EventKey\x12\x36\n\revent_sources\x18\x04 \x03(\x0e\x32\x1f.protos.event.Event.EventSource\"\xaa\x01\n\x0e\x45ventTypeStats\x12\x30\n\nkeys_count\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x31\n\x0b\x65vent_count\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x33\n\rmonitor_count\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\",\n\x10\x45ventTypePartial\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x0c\n\x04name\x18\x02 \x01(\t\"s\n\x10\x45ventTypeSummary\x12\x32\n\nevent_type\x18\x01 \x01(\x0b\x32\x1e.protos.event.EventTypePartial\x12+\n\x05stats\x18\x02 \x01(\x0b\x32\x1c.protos.event.EventTypeStats\"o\n\x13\x45ventTypeDefinition\x12+\n\nevent_type\x18\x01 \x01(\x0b\x32\x17.protos.event.EventType\x12+\n\x05stats\x18\x02 \x01(\x0b\x32\x1c.protos.event.EventTypeStats\"\xa5\x02\n\x05\x45vent\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x32\n\nevent_type\x18\x02 \x01(\x0b\x32\x1e.protos.event.EventTypePartial\x12#\n\x03kvs\x18\x03 \x03(\x0b\x32\x16.protos.event.KeyValue\x12\x11\n\ttimestamp\x18\x04 \x01(\x10\x12\x35\n\x0c\x65vent_source\x18\x05 \x01(\x0e\x32\x1f.protos.event.Event.EventSource\"m\n\x0b\x45ventSource\x12\x0b\n\x07UNKNOWN\x10\x00\x12\n\n\x06SAMPLE\x10\x01\x12\x07\n\x03\x41PI\x10\x02\x12\x07\n\x03SDK\x10\x03\x12\x0b\n\x07SEGMENT\x10\x04\x12\r\n\tAMPLITUDE\x10\x05\x12\x07\n\x03SNS\x10\x06\x12\x0e\n\nCLOUDWATCH\x10\x07*\x91\x01\n\x07\x43ontext\x12\r\n\tUNKNOWN_C\x10\x00\x12\t\n\x05\x45VENT\x10\x01\x12\x17\n\x13MONITOR_TRANSACTION\x10\x02\x12\x13\n\x0f\x45NTITY_INSTANCE\x10\x03\x12\x0e\n\nEVENT_TYPE\x10\x04\x12\x0b\n\x07MONITOR\x10\x05\x12\n\n\x06\x45NTITY\x10\x06\x12\x15\n\x11\x45VENTS_CLICKHOUSE\x10\x07\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.event.base_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CONTEXT._serialized_start=1371
  _CONTEXT._serialized_end=1516
  _TIMERANGE._serialized_start=100
  _TIMERANGE._serialized_end=146
  _PAGE._serialized_start=148
  _PAGE._serialized_end=245
  _EVENTKEY._serialized_start=248
  _EVENTKEY._serialized_end=489
  _EVENTKEY_KEYTYPE._serialized_start=387
  _EVENTKEY_KEYTYPE._serialized_end=489
  _EVENTTYPE._serialized_start=492
  _EVENTTYPE._serialized_end=623
  _EVENTTYPESTATS._serialized_start=626
  _EVENTTYPESTATS._serialized_end=796
  _EVENTTYPEPARTIAL._serialized_start=798
  _EVENTTYPEPARTIAL._serialized_end=842
  _EVENTTYPESUMMARY._serialized_start=844
  _EVENTTYPESUMMARY._serialized_end=959
  _EVENTTYPEDEFINITION._serialized_start=961
  _EVENTTYPEDEFINITION._serialized_end=1072
  _EVENT._serialized_start=1075
  _EVENT._serialized_end=1368
  _EVENT_EVENTSOURCE._serialized_start=1259
  _EVENT_EVENTSOURCE._serialized_end=1368
# @@protoc_insertion_point(module_scope)