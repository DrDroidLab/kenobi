# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/kafka/event_entity.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from protos.kafka import base_pb2 as protos_dot_kafka_dot_base__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fprotos/kafka/event_entity.proto\x12\x0cprotos.kafka\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x17protos/kafka/base.proto\"\x17\n\x15\x45ventEntityPayloadKey\"\xce\x01\n\x17\x45ventEntityPayloadValue\x12\x30\n\naccount_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x34\n\x05\x65vent\x18\x02 \x01(\x0b\x32%.protos.kafka.ProcessedIngestionEvent\x12K\n\x1b\x64iscovered_entity_instances\x18\x03 \x03(\x0b\x32&.protos.kafka.DiscoveredEntityInstanceb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.kafka.event_entity_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _EVENTENTITYPAYLOADKEY._serialized_start=106
  _EVENTENTITYPAYLOADKEY._serialized_end=129
  _EVENTENTITYPAYLOADVALUE._serialized_start=132
  _EVENTENTITYPAYLOADVALUE._serialized_end=338
# @@protoc_insertion_point(module_scope)
