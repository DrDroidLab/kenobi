# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/event/entity.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from protos.event import base_pb2 as protos_dot_event_dot_base__pb2
from protos.event import monitor_pb2 as protos_dot_event_dot_monitor__pb2
from protos.event import query_base_pb2 as protos_dot_event_dot_query__base__pb2
from protos.event import notification_pb2 as protos_dot_event_dot_notification__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19protos/event/entity.proto\x12\x0cprotos.event\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x17protos/event/base.proto\x1a\x1aprotos/event/monitor.proto\x1a\x1dprotos/event/query_base.proto\x1a\x1fprotos/event/notification.proto\"\x9b\x01\n\x15\x45ntityEventKeyMapping\x12(\n\x02id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12)\n\tevent_key\x18\x03 \x01(\x0b\x32\x16.protos.event.EventKey\x12-\n\tis_active\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\"\x8b\x04\n\x17\x45ntityTriggerDefinition\x12N\n\trule_type\x18\x01 \x01(\x0e\x32;.protos.event.EntityTriggerDefinition.EntityTriggerRuleType\x12?\n\x04type\x18\x02 \x01(\x0e\x32\x31.protos.event.EntityTriggerDefinition.TriggerType\x12T\n\x13trigger_rule_config\x18\x03 \x01(\x0b\x32\x37.protos.event.EntityTriggerDefinition.TriggerRuleConfig\x1ai\n\x11TriggerRuleConfig\x12\x10\n\x08\x65vent_id\x18\x01 \x01(\x04\x12\x15\n\rtime_interval\x18\x02 \x01(\x04\x12\x17\n\x0fthreshold_count\x18\x03 \x01(\x04\x12\x12\n\nevent_name\x18\x04 \x01(\t\"E\n\x0bTriggerType\x12\x10\n\x0cUNKNOWN_TYPE\x10\x00\x12\r\n\tPER_EVENT\x10\x01\x12\x15\n\x11\x41GGREGATED_EVENTS\x10\x02\"W\n\x15\x45ntityTriggerRuleType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0e\n\nLAST_EVENT\x10\x01\x12\x0f\n\x0b\x45VENT_COUNT\x10\x02\x12\x10\n\x0c\x45VENT_OCCURS\x10\x03\"\x9a\x02\n\rEntityTrigger\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x11\n\tentity_id\x18\x02 \x01(\x04\x12\x13\n\x0b\x65ntity_name\x18\x03 \x01(\t\x12\x0c\n\x04name\x18\x04 \x01(\t\x12\x39\n\ndefinition\x18\x05 \x01(\x0b\x32%.protos.event.EntityTriggerDefinition\x12$\n\x06\x66ilter\x18\x06 \x01(\x0b\x32\x14.protos.event.Filter\x12\x37\n\rnotifications\x18\x07 \x03(\x0b\x32 .protos.event.NotificationConfig\x12-\n\tis_active\x18\x08 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\"\x8c\x02\n\x06\x45ntity\x12(\n\x02id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12*\n\x04name\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12-\n\tis_active\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x12\n\ncreated_at\x18\x05 \x01(\x10\x12\x12\n\nupdated_at\x18\x06 \x01(\x10\x12\'\n\x04type\x18\x07 \x01(\x0e\x32\x19.protos.event.Entity.Type\",\n\x04Type\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0b\n\x07\x44\x45\x46\x41ULT\x10\x01\x12\n\n\x06\x46UNNEL\x10\x02\"e\n\rEntityPartial\x12(\n\x02id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12*\n\x04name\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xf0\x01\n\x0b\x45ntityStats\x12\x38\n\x12new_instance_count\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12;\n\x15\x61\x63tive_instance_count\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x31\n\x0b\x65vent_count\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x37\n\x11transaction_count\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\"_\n\rEntitySummary\x12$\n\x06\x65ntity\x18\x01 \x01(\x0b\x32\x14.protos.event.Entity\x12(\n\x05stats\x18\x02 \x01(\x0b\x32\x19.protos.event.EntityStats\"\xa6\x01\n\x0c\x45ntityDetail\x12$\n\x06\x65ntity\x18\x01 \x01(\x0b\x32\x14.protos.event.Entity\x12\x46\n\x19\x65ntity_event_key_mappings\x18\x02 \x03(\x0b\x32#.protos.event.EntityEventKeyMapping\x12(\n\x05stats\x18\x03 \x01(\x0b\x32\x19.protos.event.EntityStats\"\xab\x01\n\x0e\x45ntityInstance\x12(\n\x02id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12.\n\x08instance\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12+\n\x06\x65ntity\x18\x03 \x01(\x0b\x32\x1b.protos.event.EntityPartial\x12\x12\n\ncreated_at\x18\x04 \x01(\x10\"q\n\x15\x45ntityInstancePartial\x12(\n\x02id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12.\n\x08instance\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xae\x02\n\x13\x45ntityInstanceStats\x12\x31\n\x0b\x65vent_count\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x37\n\x11transaction_count\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12.\n\nhas_alerts\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12=\n\x06\x61lerts\x18\x04 \x03(\x0b\x32-.protos.event.EntityInstanceStats.EntityAlert\x1a<\n\x0b\x45ntityAlert\x12\x10\n\x08\x61lert_id\x18\x01 \x01(\x04\x12\x1b\n\x13\x65ntity_trigger_name\x18\x02 \x01(\t\"\x87\x01\n\x15\x45ntityInstanceSummary\x12<\n\x0f\x65ntity_instance\x18\x01 \x01(\x0b\x32#.protos.event.EntityInstancePartial\x12\x30\n\x05stats\x18\x02 \x01(\x0b\x32!.protos.event.EntityInstanceStats\"\x7f\n\x14\x45ntityInstanceDetail\x12\x35\n\x0f\x65ntity_instance\x18\x01 \x01(\x0b\x32\x1c.protos.event.EntityInstance\x12\x30\n\x05stats\x18\x02 \x01(\x0b\x32!.protos.event.EntityInstanceStats\",\n\x17\x45ntityInstanceGetParams\x12\x11\n\tinstances\x18\x01 \x03(\t\"\xf1\x08\n\x0eUpdateEntityOp\x12+\n\x02op\x18\x01 \x01(\x0e\x32\x1f.protos.event.UpdateEntityOp.Op\x12K\n\x12update_entity_name\x18\x02 \x01(\x0b\x32-.protos.event.UpdateEntityOp.UpdateEntityNameH\x00\x12O\n\x14update_entity_status\x18\x03 \x01(\x0b\x32/.protos.event.UpdateEntityOp.UpdateEntityStatusH\x00\x12p\n&update_entity_event_key_mapping_status\x18\x04 \x01(\x0b\x32>.protos.event.UpdateEntityOp.UpdateEntityEventKeyMappingStatusH\x00\x12_\n\x1d\x61\x64\x64_entity_event_key_mappings\x18\x05 \x01(\x0b\x32\x36.protos.event.UpdateEntityOp.AddEntityEventKeyMappingsH\x00\x12\x65\n remove_entity_event_key_mappings\x18\x06 \x01(\x0b\x32\x39.protos.event.UpdateEntityOp.RemoveEntityEventKeyMappingsH\x00\x1a>\n\x10UpdateEntityName\x12*\n\x04name\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x1a\x43\n\x12UpdateEntityStatus\x12-\n\tis_active\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x1a\x95\x01\n!UpdateEntityEventKeyMappingStatus\x12\x41\n\x1b\x65ntity_event_key_mapping_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12-\n\tis_active\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x1a\x32\n\x19\x41\x64\x64\x45ntityEventKeyMappings\x12\x15\n\revent_key_ids\x18\x01 \x03(\x04\x1a\x44\n\x1cRemoveEntityEventKeyMappings\x12$\n\x1c\x65ntity_event_key_mapping_ids\x18\x01 \x03(\x04\"\xb8\x01\n\x02Op\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x16\n\x12UPDATE_ENTITY_NAME\x10\x01\x12\x18\n\x14UPDATE_ENTITY_STATUS\x10\x02\x12*\n&UPDATE_ENTITY_EVENT_KEY_MAPPING_STATUS\x10\x03\x12!\n\x1d\x41\x44\x44_ENTITY_EVENT_KEY_MAPPINGS\x10\x04\x12$\n REMOVE_ENTITY_EVENT_KEY_MAPPINGS\x10\x05\x42\x08\n\x06update\"\xd8\n\n\x0cWorkflowView\x12.\n\x05nodes\x18\x01 \x03(\x0b\x32\x1f.protos.event.WorkflowView.Node\x12.\n\x05\x65\x64ges\x18\x02 \x03(\x0b\x32\x1f.protos.event.WorkflowView.Edge\x1a\x9d\x05\n\x04Node\x12-\n\x07node_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12+\n\x05label\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x35\n\x06status\x18\x03 \x01(\x0e\x32%.protos.event.WorkflowView.NodeStatus\x12G\n\x10\x63onnection_types\x18\x04 \x03(\x0e\x32-.protos.event.WorkflowView.NodeConnectionType\x12;\n\x07metrics\x18\x05 \x03(\x0b\x32*.protos.event.WorkflowView.Node.NodeMetric\x12:\n\x14workflow_node_config\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x1a\xbf\x02\n\nNodeMetric\x12*\n\x04name\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12+\n\x05value\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12>\n\rmetric_status\x18\x03 \x01(\x0e\x32\'.protos.event.WorkflowView.MetricStatus\x12\x31\n\x0bmetric_link\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12+\n\x05\x64\x65lta\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.DoubleValue\x12\x38\n\ndelta_type\x18\x06 \x01(\x0e\x32$.protos.event.WorkflowView.DeltaType\x1a\xd3\x02\n\x04\x45\x64ge\x12\x33\n\rstart_node_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12\x31\n\x0b\x65nd_node_id\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12;\n\x07metrics\x18\x03 \x03(\x0b\x32*.protos.event.WorkflowView.Edge.EdgeMetric\x1a\xa5\x01\n\nEdgeMetric\x12*\n\x04name\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12+\n\x05value\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12>\n\rmetric_status\x18\x03 \x01(\x0e\x32\'.protos.event.WorkflowView.MetricStatus\"=\n\x0cMetricStatus\x12\x19\n\x15UNKNOWN_METRIC_STATUS\x10\x00\x12\t\n\x05GREEN\x10\x01\x12\x07\n\x03RED\x10\x02\"8\n\nNodeStatus\x12\x17\n\x13UNKNOWN_NODE_STATUS\x10\x00\x12\x08\n\x04GOOD\x10\x01\x12\x07\n\x03\x42\x41\x44\x10\x02\"B\n\x12NodeConnectionType\x12\x1b\n\x17UNKNOWN_CONNECTION_TYPE\x10\x00\x12\x06\n\x02IN\x10\x01\x12\x07\n\x03OUT\x10\x02\"5\n\tDeltaType\x12\x16\n\x12UNKNOWN_DELTA_TYPE\x10\x00\x12\x06\n\x02UP\x10\x01\x12\x08\n\x04\x44OWN\x10\x02\"\xda\x02\n\nFunnelView\x12+\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x1d.protos.event.FunnelView.Node\x12,\n\x05links\x18\x02 \x03(\x0b\x32\x1d.protos.event.FunnelView.Edge\x1a_\n\x04Node\x12*\n\x04name\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12+\n\x05value\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x1a\x8f\x01\n\x04\x45\x64ge\x12,\n\x06source\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12,\n\x06target\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12+\n\x05value\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\"\x94\n\n\x14UpdateEntityFunnelOp\x12\x31\n\x02op\x18\x01 \x01(\x0e\x32%.protos.event.UpdateEntityFunnelOp.Op\x12^\n\x19update_entity_funnel_name\x18\x02 \x01(\x0b\x32\x39.protos.event.UpdateEntityFunnelOp.UpdateEntityFunnelNameH\x00\x12\x62\n\x1bupdate_entity_funnel_status\x18\x03 \x01(\x0b\x32;.protos.event.UpdateEntityFunnelOp.UpdateEntityFunnelStatusH\x00\x12\x80\x01\n+update_entity_funnel_monitor_mapping_status\x18\x04 \x01(\x0b\x32I.protos.event.UpdateEntityFunnelOp.UpdateEntityFunnelMonitorMappingStatusH\x00\x12o\n\"add_entity_funnel_monitor_mappings\x18\x05 \x01(\x0b\x32\x41.protos.event.UpdateEntityFunnelOp.AddEntityFunnelMonitorMappingsH\x00\x12u\n%remove_entity_funnel_monitor_mappings\x18\x06 \x01(\x0b\x32\x44.protos.event.UpdateEntityFunnelOp.RemoveEntityFunnelMonitorMappingsH\x00\x1a\x44\n\x16UpdateEntityFunnelName\x12*\n\x04name\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x1aI\n\x18UpdateEntityFunnelStatus\x12-\n\tis_active\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x1a\x9f\x01\n&UpdateEntityFunnelMonitorMappingStatus\x12\x46\n entity_funnel_monitor_mapping_id\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.UInt64Value\x12-\n\tis_active\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x1a\x35\n\x1e\x41\x64\x64\x45ntityFunnelMonitorMappings\x12\x13\n\x0bmonitor_ids\x18\x01 \x03(\x04\x1aN\n!RemoveEntityFunnelMonitorMappings\x12)\n!entity_funnel_monitor_mapping_ids\x18\x01 \x03(\x04\"\xd5\x01\n\x02Op\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x1d\n\x19UPDATE_ENTITY_FUNNEL_NAME\x10\x01\x12\x1f\n\x1bUPDATE_ENTITY_FUNNEL_STATUS\x10\x02\x12/\n+UPDATE_ENTITY_FUNNEL_MONITOR_MAPPING_STATUS\x10\x03\x12&\n\"ADD_ENTITY_FUNNEL_MONITOR_MAPPINGS\x10\x04\x12)\n%REMOVE_ENTITY_FUNNEL_MONITOR_MAPPINGS\x10\x05\x42\x08\n\x06updateb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.event.entity_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ENTITYEVENTKEYMAPPING._serialized_start=193
  _ENTITYEVENTKEYMAPPING._serialized_end=348
  _ENTITYTRIGGERDEFINITION._serialized_start=351
  _ENTITYTRIGGERDEFINITION._serialized_end=874
  _ENTITYTRIGGERDEFINITION_TRIGGERRULECONFIG._serialized_start=609
  _ENTITYTRIGGERDEFINITION_TRIGGERRULECONFIG._serialized_end=714
  _ENTITYTRIGGERDEFINITION_TRIGGERTYPE._serialized_start=716
  _ENTITYTRIGGERDEFINITION_TRIGGERTYPE._serialized_end=785
  _ENTITYTRIGGERDEFINITION_ENTITYTRIGGERRULETYPE._serialized_start=787
  _ENTITYTRIGGERDEFINITION_ENTITYTRIGGERRULETYPE._serialized_end=874
  _ENTITYTRIGGER._serialized_start=877
  _ENTITYTRIGGER._serialized_end=1159
  _ENTITY._serialized_start=1162
  _ENTITY._serialized_end=1430
  _ENTITY_TYPE._serialized_start=1386
  _ENTITY_TYPE._serialized_end=1430
  _ENTITYPARTIAL._serialized_start=1432
  _ENTITYPARTIAL._serialized_end=1533
  _ENTITYSTATS._serialized_start=1536
  _ENTITYSTATS._serialized_end=1776
  _ENTITYSUMMARY._serialized_start=1778
  _ENTITYSUMMARY._serialized_end=1873
  _ENTITYDETAIL._serialized_start=1876
  _ENTITYDETAIL._serialized_end=2042
  _ENTITYINSTANCE._serialized_start=2045
  _ENTITYINSTANCE._serialized_end=2216
  _ENTITYINSTANCEPARTIAL._serialized_start=2218
  _ENTITYINSTANCEPARTIAL._serialized_end=2331
  _ENTITYINSTANCESTATS._serialized_start=2334
  _ENTITYINSTANCESTATS._serialized_end=2636
  _ENTITYINSTANCESTATS_ENTITYALERT._serialized_start=2576
  _ENTITYINSTANCESTATS_ENTITYALERT._serialized_end=2636
  _ENTITYINSTANCESUMMARY._serialized_start=2639
  _ENTITYINSTANCESUMMARY._serialized_end=2774
  _ENTITYINSTANCEDETAIL._serialized_start=2776
  _ENTITYINSTANCEDETAIL._serialized_end=2903
  _ENTITYINSTANCEGETPARAMS._serialized_start=2905
  _ENTITYINSTANCEGETPARAMS._serialized_end=2949
  _UPDATEENTITYOP._serialized_start=2952
  _UPDATEENTITYOP._serialized_end=4089
  _UPDATEENTITYOP_UPDATEENTITYNAME._serialized_start=3487
  _UPDATEENTITYOP_UPDATEENTITYNAME._serialized_end=3549
  _UPDATEENTITYOP_UPDATEENTITYSTATUS._serialized_start=3551
  _UPDATEENTITYOP_UPDATEENTITYSTATUS._serialized_end=3618
  _UPDATEENTITYOP_UPDATEENTITYEVENTKEYMAPPINGSTATUS._serialized_start=3621
  _UPDATEENTITYOP_UPDATEENTITYEVENTKEYMAPPINGSTATUS._serialized_end=3770
  _UPDATEENTITYOP_ADDENTITYEVENTKEYMAPPINGS._serialized_start=3772
  _UPDATEENTITYOP_ADDENTITYEVENTKEYMAPPINGS._serialized_end=3822
  _UPDATEENTITYOP_REMOVEENTITYEVENTKEYMAPPINGS._serialized_start=3824
  _UPDATEENTITYOP_REMOVEENTITYEVENTKEYMAPPINGS._serialized_end=3892
  _UPDATEENTITYOP_OP._serialized_start=3895
  _UPDATEENTITYOP_OP._serialized_end=4079
  _WORKFLOWVIEW._serialized_start=4092
  _WORKFLOWVIEW._serialized_end=5460
  _WORKFLOWVIEW_NODE._serialized_start=4205
  _WORKFLOWVIEW_NODE._serialized_end=4874
  _WORKFLOWVIEW_NODE_NODEMETRIC._serialized_start=4555
  _WORKFLOWVIEW_NODE_NODEMETRIC._serialized_end=4874
  _WORKFLOWVIEW_EDGE._serialized_start=4877
  _WORKFLOWVIEW_EDGE._serialized_end=5216
  _WORKFLOWVIEW_EDGE_EDGEMETRIC._serialized_start=5051
  _WORKFLOWVIEW_EDGE_EDGEMETRIC._serialized_end=5216
  _WORKFLOWVIEW_METRICSTATUS._serialized_start=5218
  _WORKFLOWVIEW_METRICSTATUS._serialized_end=5279
  _WORKFLOWVIEW_NODESTATUS._serialized_start=5281
  _WORKFLOWVIEW_NODESTATUS._serialized_end=5337
  _WORKFLOWVIEW_NODECONNECTIONTYPE._serialized_start=5339
  _WORKFLOWVIEW_NODECONNECTIONTYPE._serialized_end=5405
  _WORKFLOWVIEW_DELTATYPE._serialized_start=5407
  _WORKFLOWVIEW_DELTATYPE._serialized_end=5460
  _FUNNELVIEW._serialized_start=5463
  _FUNNELVIEW._serialized_end=5809
  _FUNNELVIEW_NODE._serialized_start=5568
  _FUNNELVIEW_NODE._serialized_end=5663
  _FUNNELVIEW_EDGE._serialized_start=5666
  _FUNNELVIEW_EDGE._serialized_end=5809
  _UPDATEENTITYFUNNELOP._serialized_start=5812
  _UPDATEENTITYFUNNELOP._serialized_end=7112
  _UPDATEENTITYFUNNELOP_UPDATEENTITYFUNNELNAME._serialized_start=6446
  _UPDATEENTITYFUNNELOP_UPDATEENTITYFUNNELNAME._serialized_end=6514
  _UPDATEENTITYFUNNELOP_UPDATEENTITYFUNNELSTATUS._serialized_start=6516
  _UPDATEENTITYFUNNELOP_UPDATEENTITYFUNNELSTATUS._serialized_end=6589
  _UPDATEENTITYFUNNELOP_UPDATEENTITYFUNNELMONITORMAPPINGSTATUS._serialized_start=6592
  _UPDATEENTITYFUNNELOP_UPDATEENTITYFUNNELMONITORMAPPINGSTATUS._serialized_end=6751
  _UPDATEENTITYFUNNELOP_ADDENTITYFUNNELMONITORMAPPINGS._serialized_start=6753
  _UPDATEENTITYFUNNELOP_ADDENTITYFUNNELMONITORMAPPINGS._serialized_end=6806
  _UPDATEENTITYFUNNELOP_REMOVEENTITYFUNNELMONITORMAPPINGS._serialized_start=6808
  _UPDATEENTITYFUNNELOP_REMOVEENTITYFUNNELMONITORMAPPINGS._serialized_end=6886
  _UPDATEENTITYFUNNELOP_OP._serialized_start=6889
  _UPDATEENTITYFUNNELOP_OP._serialized_end=7102
# @@protoc_insertion_point(module_scope)
