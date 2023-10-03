# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/config/collector.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dprotos/config/collector.proto\x12\rprotos.config\x1a\x1egoogle/protobuf/wrappers.proto\"\xe0\x01\n\x0bSqsConsumer\x12+\n\x07\x65nabled\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12/\n\tqueue_url\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12;\n\x16max_number_of_messages\x18\x03 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12\x36\n\x11wait_time_seconds\x18\x04 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\"\xcd\x01\n\x0ePipelineConfig\x12.\n\x0bhttp_server\x18\x01 \x01(\x0b\x32\x19.protos.config.HttpServer\x12\'\n\x07\x62\x61tcher\x18\x02 \x01(\x0b\x32\x16.protos.config.Batcher\x12\x30\n\x08\x65xporter\x18\x03 \x01(\x0b\x32\x1e.protos.config.WrappedExporter\x12\x30\n\x0csqs_consumer\x18\x04 \x01(\x0b\x32\x1a.protos.config.SqsConsumer\"j\n\x07NetAddr\x12.\n\x08\x65ndpoint\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12/\n\ttransport\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"6\n\nHttpServer\x12(\n\x08net_addr\x18\x01 \x01(\x0b\x32\x16.protos.config.NetAddr\"\x9b\x01\n\x07\x42\x61tcher\x12/\n\tchan_size\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\x12\x30\n\nbatch_size\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\x12-\n\x07timeout\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xb3\x02\n\x0fWrappedExporter\x12>\n\x08wrappers\x18\x01 \x03(\x0b\x32,.protos.config.WrappedExporter.WrappersEntry\x1a\x86\x01\n\x07Wrapper\x12:\n\x10\x63onsole_exporter\x18\x01 \x01(\x0b\x32\x1e.protos.config.ConsoleExporterH\x00\x12\x34\n\rhttp_exporter\x18\x02 \x01(\x0b\x32\x1b.protos.config.HttpExporterH\x00\x42\t\n\x07wrapper\x1aW\n\rWrappersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x35\n\x05value\x18\x02 \x01(\x0b\x32&.protos.config.WrappedExporter.Wrapper:\x02\x38\x01\">\n\x0f\x43onsoleExporter\x12+\n\x07\x65nabled\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\"g\n\nBearerAuth\x12+\n\x05token\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12,\n\x06scheme\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"J\n\x0e\x41uthentication\x12\x30\n\x0b\x62\x65\x61rer_auth\x18\x01 \x01(\x0b\x32\x19.protos.config.BearerAuthH\x00\x42\x06\n\x04\x61uth\"\xbd\x02\n\x0cHttpExporter\x12*\n\x04host\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12.\n\x08\x65ndpoint\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12/\n\tchan_size\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.UInt32Value\x12\x35\n\x0e\x61uthentication\x18\x04 \x01(\x0b\x32\x1d.protos.config.Authentication\x12\x39\n\x07headers\x18\x05 \x03(\x0b\x32(.protos.config.HttpExporter.HeadersEntry\x1a.\n\x0cHeadersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x42\x11Z\x0f./protos/configb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.config.collector_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z\017./protos/config'
  _WRAPPEDEXPORTER_WRAPPERSENTRY._options = None
  _WRAPPEDEXPORTER_WRAPPERSENTRY._serialized_options = b'8\001'
  _HTTPEXPORTER_HEADERSENTRY._options = None
  _HTTPEXPORTER_HEADERSENTRY._serialized_options = b'8\001'
  _SQSCONSUMER._serialized_start=81
  _SQSCONSUMER._serialized_end=305
  _PIPELINECONFIG._serialized_start=308
  _PIPELINECONFIG._serialized_end=513
  _NETADDR._serialized_start=515
  _NETADDR._serialized_end=621
  _HTTPSERVER._serialized_start=623
  _HTTPSERVER._serialized_end=677
  _BATCHER._serialized_start=680
  _BATCHER._serialized_end=835
  _WRAPPEDEXPORTER._serialized_start=838
  _WRAPPEDEXPORTER._serialized_end=1145
  _WRAPPEDEXPORTER_WRAPPER._serialized_start=922
  _WRAPPEDEXPORTER_WRAPPER._serialized_end=1056
  _WRAPPEDEXPORTER_WRAPPERSENTRY._serialized_start=1058
  _WRAPPEDEXPORTER_WRAPPERSENTRY._serialized_end=1145
  _CONSOLEEXPORTER._serialized_start=1147
  _CONSOLEEXPORTER._serialized_end=1209
  _BEARERAUTH._serialized_start=1211
  _BEARERAUTH._serialized_end=1314
  _AUTHENTICATION._serialized_start=1316
  _AUTHENTICATION._serialized_end=1390
  _HTTPEXPORTER._serialized_start=1393
  _HTTPEXPORTER._serialized_end=1710
  _HTTPEXPORTER_HEADERSENTRY._serialized_start=1664
  _HTTPEXPORTER_HEADERSENTRY._serialized_end=1710
# @@protoc_insertion_point(module_scope)