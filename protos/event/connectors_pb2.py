# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/event/connectors.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dprotos/event/connectors.proto\x12\x0cprotos.event\x1a\x1egoogle/protobuf/wrappers.proto\"\x83\x02\n\tConnector\x12(\n\x02id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12)\n\x04type\x18\x02 \x01(\x0e\x32\x1b.protos.event.ConnectorType\x12-\n\tis_active\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12*\n\x04name\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12<\n\rsentry_config\x18\n \x01(\x0b\x32#.protos.event.SentryConnectorConfigH\x00\x42\x08\n\x06\x63onfig\"P\n\x15SentryConnectorConfig\x12\x37\n\x11polling_frequency\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\"\xc9\x02\n\x0c\x43onnectorKey\x12(\n\x02id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x34\n\x08key_type\x18\x02 \x01(\x0e\x32\".protos.event.ConnectorKey.KeyType\x12)\n\x03key\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12-\n\tis_active\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\"\x7f\n\x07KeyType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x12\n\x0eSENTRY_API_KEY\x10\x01\x12\x13\n\x0f\x44\x41TADOG_APP_KEY\x10\x02\x12\x13\n\x0f\x44\x41TADOG_API_KEY\x10\x03\x12\x14\n\x10NEWRELIC_API_KEY\x10\x04\x12\x13\n\x0fNEWRELIC_APP_ID\x10\x05\"T\n\x11PeriodicRunStatus\"?\n\nStatusType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0b\n\x07STARTED\x10\x01\x12\x0c\n\x08\x46INISHED\x10\x02\x12\t\n\x05\x45RROR\x10\x03*\xa1\x02\n\rConnectorType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\n\n\x06SENTRY\x10\x01\x12\x0b\n\x07SEGMENT\x10\x02\x12\x12\n\x0e\x45LASTIC_SEARCH\x10\x03\x12\r\n\tAMPLITUDE\x10\x04\x12\x0f\n\x0b\x41WS_KINESIS\x10\x05\x12\x0e\n\nCLOUDWATCH\x10\x06\x12\r\n\tCLEVERTAP\x10\x07\x12\x0f\n\x0bRUDDERSTACK\x10\x08\x12\x0c\n\x08MOENGAGE\x10\t\x12\t\n\x05\x43RIBL\x10\n\x12\t\n\x05KAFKA\x10\x0b\x12\x0b\n\x07\x44\x41TADOG\x10\x0c\x12\x0c\n\x08\x46ILEBEAT\x10\r\x12\x0c\n\x08LOGSTASH\x10\x0e\x12\x0b\n\x07\x46LUENTD\x10\x0f\x12\r\n\tFLUENTBIT\x10\x10\x12\x0e\n\nPAGER_DUTY\x10\x11\x12\r\n\tNEW_RELIC\x10\x12*\x89\x01\n\x0fTransformerType\x12\x0e\n\nUNKNOWN_TT\x10\x00\x12\x1e\n\x1aSEGMENT_DFAULT_TRANSFORMER\x10\x02\x12!\n\x1d\x41MPLITUDE_DEFAULT_TRANSFORMER\x10\x03\x12#\n\x1f\x43LOUDWATCH_JSON_LOG_TRANSFORMER\x10\x04*Z\n\x0b\x44\x65\x63oderType\x12\x0e\n\nUNKNOWN_DT\x10\x00\x12\x17\n\x13\x41WS_KINESIS_DECODER\x10\x01\x12\"\n\x1e\x41WS_CLOUDWATCH_KINESIS_DECODER\x10\x02\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.event.connectors_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CONNECTORTYPE._serialized_start=842
  _CONNECTORTYPE._serialized_end=1131
  _TRANSFORMERTYPE._serialized_start=1134
  _TRANSFORMERTYPE._serialized_end=1271
  _DECODERTYPE._serialized_start=1273
  _DECODERTYPE._serialized_end=1363
  _CONNECTOR._serialized_start=80
  _CONNECTOR._serialized_end=339
  _SENTRYCONNECTORCONFIG._serialized_start=341
  _SENTRYCONNECTORCONFIG._serialized_end=421
  _CONNECTORKEY._serialized_start=424
  _CONNECTORKEY._serialized_end=753
  _CONNECTORKEY_KEYTYPE._serialized_start=626
  _CONNECTORKEY_KEYTYPE._serialized_end=753
  _PERIODICRUNSTATUS._serialized_start=755
  _PERIODICRUNSTATUS._serialized_end=839
  _PERIODICRUNSTATUS_STATUSTYPE._serialized_start=776
  _PERIODICRUNSTATUS_STATUSTYPE._serialized_end=839
# @@protoc_insertion_point(module_scope)
