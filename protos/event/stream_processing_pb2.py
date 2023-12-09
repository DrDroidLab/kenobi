# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/event/stream_processing.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
from protos.event import query_base_pb2 as protos_dot_event_dot_query__base__pb2
from protos.event import literal_pb2 as protos_dot_event_dot_literal__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n$protos/event/stream_processing.proto\x12\x0cprotos.event\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x1cgoogle/protobuf/struct.proto\x1a\x1dprotos/event/query_base.proto\x1a\x1aprotos/event/literal.proto\"9\n\x1aRegexEventProcessingFilter\x12\x1b\n\x13regular_expressions\x18\x01 \x03(\t\"\xcf\x01\n\x19JSONEventProcessingFilter\x12\x43\n\x07\x66ilters\x18\x01 \x03(\x0b\x32\x32.protos.event.JSONEventProcessingFilter.JSONFilter\x1am\n\nJSONFilter\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x0c\n\x04path\x18\x02 \x01(\t\x12\x1c\n\x02op\x18\x03 \x01(\x0e\x32\x10.protos.event.Op\x12&\n\x07literal\x18\x04 \x01(\x0b\x32\x15.protos.event.Literal\"R\n\x19GrokEventProcessingParser\x12\x35\n\x0fgrok_expression\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xeb\x05\n\x15\x45ventProcessingFilter\x12(\n\x02id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12*\n\x04name\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x36\n\x04type\x18\x03 \x01(\x0e\x32(.protos.event.EventProcessingFilter.Type\x12-\n\tis_active\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x12\n\ncreated_at\x18\x05 \x01(\x10\x12\x38\n\x05stats\x18\x06 \x01(\x0b\x32).protos.event.EventProcessingFilter.Stats\x12\x39\n\x05regex\x18\x64 \x01(\x0b\x32(.protos.event.RegexEventProcessingFilterH\x00\x12=\n\njson_field\x18\x65 \x01(\x0b\x32\'.protos.event.JSONEventProcessingFilterH\x00\x1a\x92\x02\n\x05Stats\x12\x37\n\x11total_event_count\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12@\n\x1atotal_filtered_event_count\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12G\n!total_filtered_failed_event_count\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x45\n\x1ftotal_generated_drd_event_count\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\".\n\x04Type\x12\x0b\n\x07\x44\x45\x46\x41ULT\x10\x00\x12\t\n\x05REGEX\x10\x01\x12\x0e\n\nJSON_FIELD\x10\x02\x42\x08\n\x06\x66ilter\"\xeb\x04\n\x1dUpdateEventProcessingFilterOp\x12:\n\x02op\x18\x01 \x01(\x0e\x32..protos.event.UpdateEventProcessingFilterOp.Op\x12z\n#update_event_processing_filter_name\x18\x64 \x01(\x0b\x32K.protos.event.UpdateEventProcessingFilterOp.UpdateEventProcessingFilterNameH\x00\x12~\n%update_event_processing_filter_status\x18\x65 \x01(\x0b\x32M.protos.event.UpdateEventProcessingFilterOp.UpdateEventProcessingFilterStatusH\x00\x1aM\n\x1fUpdateEventProcessingFilterName\x12*\n\x04name\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x1aR\n!UpdateEventProcessingFilterStatus\x12-\n\tis_active\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\"e\n\x02Op\x12\x0b\n\x07UNKNOWN\x10\x00\x12\'\n#UPDATE_EVENT_PROCESSING_FILTER_NAME\x10\x01\x12)\n%UPDATE_EVENT_PROCESSING_FILTER_STATUS\x10\x02\x42\x08\n\x06update\"\x87\t\n\x15\x45ventProcessingParser\x12(\n\x02id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12*\n\x04name\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x36\n\x04type\x18\x03 \x01(\x0e\x32(.protos.event.EventProcessingParser.Type\x12\x33\n\x06\x66ilter\x18\x04 \x01(\x0b\x32#.protos.event.EventProcessingFilter\x12_\n\x19\x64rd_event_definition_rule\x18\x05 \x01(\x0b\x32<.protos.event.EventProcessingParser.ParsedDrdEventDefinition\x12-\n\tis_active\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x12\n\ncreated_at\x18\x07 \x01(\x10\x12\x38\n\x05stats\x18\x08 \x01(\x0b\x32).protos.event.EventProcessingParser.Stats\x12>\n\x0bgrok_parser\x18\x64 \x01(\x0b\x32\'.protos.event.GrokEventProcessingParserH\x00\x1a\xda\x01\n\x18ParsedDrdEventDefinition\x12;\n\x15\x65vent_timestamp_field\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x38\n\x10\x65vent_name_field\x18\x64 \x01(\x0b\x32\x1c.google.protobuf.StringValueH\x00\x12\x39\n\x11\x63ustom_event_name\x18\x65 \x01(\x0b\x32\x1c.google.protobuf.StringValueH\x00\x42\x0c\n\nevent_name\x1a\x86\x03\n\x05Stats\x12>\n\x18total_parsed_event_count\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x45\n\x1ftotal_parser_failed_event_count\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12=\n\x17total_parsed_event_keys\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x45\n\x1ftotal_generated_drd_event_count\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x19\n\x11parsed_event_keys\x18\x64 \x03(\t\x12\x1d\n\x15parsed_timestamp_keys\x18\x65 \x03(\t\x12\x36\n\x15parsed_keys_frequency\x18\x66 \x03(\x0b\x32\x17.google.protobuf.Struct\"\x1d\n\x04Type\x12\x0b\n\x07\x44\x45\x46\x41ULT\x10\x00\x12\x08\n\x04GROK\x10\x01\x42\x08\n\x06parser\"\xeb\x04\n\x1dUpdateEventProcessingParserOp\x12:\n\x02op\x18\x01 \x01(\x0e\x32..protos.event.UpdateEventProcessingParserOp.Op\x12z\n#update_event_processing_parser_name\x18\x64 \x01(\x0b\x32K.protos.event.UpdateEventProcessingParserOp.UpdateEventProcessingParserNameH\x00\x12~\n%update_event_processing_parser_status\x18\x65 \x01(\x0b\x32M.protos.event.UpdateEventProcessingParserOp.UpdateEventProcessingParserStatusH\x00\x1aM\n\x1fUpdateEventProcessingParserName\x12*\n\x04name\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x1aR\n!UpdateEventProcessingParserStatus\x12-\n\tis_active\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\"e\n\x02Op\x12\x0b\n\x07UNKNOWN\x10\x00\x12\'\n#UPDATE_EVENT_PROCESSING_PARSER_NAME\x10\x01\x12)\n%UPDATE_EVENT_PROCESSING_PARSER_STATUS\x10\x02\x42\x08\n\x06updateb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.event.stream_processing_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _REGEXEVENTPROCESSINGFILTER._serialized_start=175
  _REGEXEVENTPROCESSINGFILTER._serialized_end=232
  _JSONEVENTPROCESSINGFILTER._serialized_start=235
  _JSONEVENTPROCESSINGFILTER._serialized_end=442
  _JSONEVENTPROCESSINGFILTER_JSONFILTER._serialized_start=333
  _JSONEVENTPROCESSINGFILTER_JSONFILTER._serialized_end=442
  _GROKEVENTPROCESSINGPARSER._serialized_start=444
  _GROKEVENTPROCESSINGPARSER._serialized_end=526
  _EVENTPROCESSINGFILTER._serialized_start=529
  _EVENTPROCESSINGFILTER._serialized_end=1276
  _EVENTPROCESSINGFILTER_STATS._serialized_start=944
  _EVENTPROCESSINGFILTER_STATS._serialized_end=1218
  _EVENTPROCESSINGFILTER_TYPE._serialized_start=1220
  _EVENTPROCESSINGFILTER_TYPE._serialized_end=1266
  _UPDATEEVENTPROCESSINGFILTEROP._serialized_start=1279
  _UPDATEEVENTPROCESSINGFILTEROP._serialized_end=1898
  _UPDATEEVENTPROCESSINGFILTEROP_UPDATEEVENTPROCESSINGFILTERNAME._serialized_start=1624
  _UPDATEEVENTPROCESSINGFILTEROP_UPDATEEVENTPROCESSINGFILTERNAME._serialized_end=1701
  _UPDATEEVENTPROCESSINGFILTEROP_UPDATEEVENTPROCESSINGFILTERSTATUS._serialized_start=1703
  _UPDATEEVENTPROCESSINGFILTEROP_UPDATEEVENTPROCESSINGFILTERSTATUS._serialized_end=1785
  _UPDATEEVENTPROCESSINGFILTEROP_OP._serialized_start=1787
  _UPDATEEVENTPROCESSINGFILTEROP_OP._serialized_end=1888
  _EVENTPROCESSINGPARSER._serialized_start=1901
  _EVENTPROCESSINGPARSER._serialized_end=3060
  _EVENTPROCESSINGPARSER_PARSEDDRDEVENTDEFINITION._serialized_start=2408
  _EVENTPROCESSINGPARSER_PARSEDDRDEVENTDEFINITION._serialized_end=2626
  _EVENTPROCESSINGPARSER_STATS._serialized_start=2629
  _EVENTPROCESSINGPARSER_STATS._serialized_end=3019
  _EVENTPROCESSINGPARSER_TYPE._serialized_start=3021
  _EVENTPROCESSINGPARSER_TYPE._serialized_end=3050
  _UPDATEEVENTPROCESSINGPARSEROP._serialized_start=3063
  _UPDATEEVENTPROCESSINGPARSEROP._serialized_end=3682
  _UPDATEEVENTPROCESSINGPARSEROP_UPDATEEVENTPROCESSINGPARSERNAME._serialized_start=3408
  _UPDATEEVENTPROCESSINGPARSEROP_UPDATEEVENTPROCESSINGPARSERNAME._serialized_end=3485
  _UPDATEEVENTPROCESSINGPARSEROP_UPDATEEVENTPROCESSINGPARSERSTATUS._serialized_start=3487
  _UPDATEEVENTPROCESSINGPARSEROP_UPDATEEVENTPROCESSINGPARSERSTATUS._serialized_end=3569
  _UPDATEEVENTPROCESSINGPARSEROP_OP._serialized_start=3571
  _UPDATEEVENTPROCESSINGPARSEROP_OP._serialized_end=3672
# @@protoc_insertion_point(module_scope)