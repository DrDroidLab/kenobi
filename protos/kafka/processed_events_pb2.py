# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/kafka/processed_events.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from protos.kafka import base_pb2 as protos_dot_kafka_dot_base__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#protos/kafka/processed_events.proto\x12\x0cprotos.kafka\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x17protos/kafka/base.proto\"\x1a\n\x18ProcessedEventPayloadKey\"\x84\x01\n\x1aProcessedEventPayloadValue\x12\x30\n\naccount_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x34\n\x05\x65vent\x18\x02 \x01(\x0b\x32%.protos.kafka.ProcessedIngestionEventb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.kafka.processed_events_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _PROCESSEDEVENTPAYLOADKEY._serialized_start=110
  _PROCESSEDEVENTPAYLOADKEY._serialized_end=136
  _PROCESSEDEVENTPAYLOADVALUE._serialized_start=139
  _PROCESSEDEVENTPAYLOADVALUE._serialized_end=271
# @@protoc_insertion_point(module_scope)
