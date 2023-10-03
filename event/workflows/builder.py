import json
import math
from collections import defaultdict

from google.protobuf.wrappers_pb2 import BoolValue, UInt64Value, StringValue, DoubleValue

from connectors.integrations.datadog import DatadogConnector
from connectors.integrations.newrelic import NewRelicConnector

from event.clickhouse.models import Events
from event.engine.metric_engine import process_metric_expressions
from event.workflows.workflow_utils import get_metric_key_context, get_event_metric_expr_query, \
    get_transaction_metric_expr_query
from protos.event.entity_pb2 import WorkflowView

class Node:

    def __init__(self, event_type_name, event_type_id):
        self.name = event_type_name
        self.id = event_type_id
        self.has_in_connections = False
        self.has_out_connections = False
        self.metrics = []
        self.status = WorkflowView.NodeStatus.GOOD
        self.workflow_node_config = None

    def mark_in_connection(self):
        self.has_in_connections = True

    def mark_out_connection(self):
        self.has_out_connections = True

    def add_metric(self, metric):
        self.metrics.append(metric)

    def set_status(self, status):
        self.status = status

    def get_proto(self):
        conn_types = []

        if self.has_in_connections:
            conn_types.append(WorkflowView.NodeConnectionType.IN)
        if self.has_out_connections:
            conn_types.append(WorkflowView.NodeConnectionType.OUT)

        return WorkflowView.Node(
            node_id=UInt64Value(value=self.id), label=StringValue(value=self.name),
            status=self.status,
            connection_types=conn_types,
            metrics=self.metrics,
            workflow_node_config=StringValue(value=json.dumps(self.workflow_node_config)),
        )


class Edge:

    def __init__(self, start: Node, end: Node):
        self.start = start
        self.end = end
        start.mark_out_connection()
        end.mark_in_connection()

    def __str__(self):
        return "{} - {} (Count: {})".format(self.start.name, self.end.name, self.counter)

    def print(self):
        print("{} -> {} ({}, {})".format(self.start.name, self.end.name, len(self.owners), self.owners[:1]))

    def get_proto(self):
        return WorkflowView.Edge(
            start_node_id=UInt64Value(value=self.start.id),
            end_node_id=UInt64Value(value=self.end.id),
            metrics=[],
        )

class WorkflowBuilder:

    def __init__(self, dtr, account):
        self.nodes = []
        self.edges = []
        self.dtr = dtr
        self.account = account
        self.dd_connector = None
        self.nr_connector = None

    def get_metric_from_datadog(self, metric_expr, compare_to=None):
        metric_value, delta, delta_type = None, None, None

        self.dd_connector = DatadogConnector(self.dtr.to_tr(), self.account.id)
        metric_value_json = self.dd_connector.fetch_metric(metric_expr)
        metric_value_compare = metric_value_json.get('value')
        if metric_value_compare is not None:
            metric_value = "{} {}".format(metric_value_json.get('value'), metric_value_json.get('unit'))
        else:
            metric_value = None

        if compare_to:
            prev_dtr = self.dtr.get_prev_dtr(compare_to)
            prev_metric_value_json = self.dd_connector.fetch_metric(metric_expr, prev_dtr.to_tr())
            prev_metric_value_compare = prev_metric_value_json.get('value')
            if metric_value_compare and not prev_metric_value_compare:
                delta = 100
                delta_type = WorkflowView.DeltaType.UP
            elif prev_metric_value_compare and not metric_value_compare:
                delta = 100
                delta_type = WorkflowView.DeltaType.DOWN
            elif not prev_metric_value_compare and not metric_value_compare:
                delta = None
                delta_type = None
            else:
                delta = abs(round((metric_value_compare / prev_metric_value_compare) - 1.0, 2)) * 100
                if metric_value_compare >= prev_metric_value_compare:
                    delta_type = WorkflowView.DeltaType.UP
                else:
                    delta_type = WorkflowView.DeltaType.DOWN

        return metric_value, delta, delta_type


    def get_metric_from_drdroid(self, metric_expr, compare_to=None):
        metric_value, delta, delta_type = None, None, None

        aggregation_type = metric_expr.split(':')[0]
        aggregation_field = metric_expr.split(':')[1].split('{')[0]
        filters = list({'lhs': x.split(':')[0], 'rhs': x.split(':')[1]} for x in metric_expr.split('{')[1].split('}')[0].split(','))

        aggregation_object = aggregation_field.split('.')[0]
        metric_expr_query = None
        if aggregation_object == 'event':
            metric_expr_query = get_event_metric_expr_query(aggregation_type, aggregation_field, filters, self.account.id, self.dtr)
        if aggregation_object == 'transaction':
            metric_expr_query = get_transaction_metric_expr_query(aggregation_type, aggregation_field, filters, self.account.id, self.dtr)

        if metric_expr_query:
            qs = Events.objects.raw(metric_expr_query)
            metric_value = list(qs)[0].id
            metric_value = round(metric_value, 2)

            if compare_to:
                prev_dtr = self.dtr.get_prev_dtr(compare_to)
                prev_metric_expr_query = None
                if aggregation_object == 'event':
                    prev_metric_expr_query = get_event_metric_expr_query(aggregation_type, aggregation_field, filters,
                                                                    self.account.id, prev_dtr)
                if aggregation_object == 'transaction':
                    prev_metric_expr_query = get_transaction_metric_expr_query(aggregation_type, aggregation_field, filters,
                                                                          self.account.id, prev_dtr)

                prev_qs = Events.objects.raw(prev_metric_expr_query)
                prev_metric_value = list(prev_qs)[0].id
                if metric_value and not prev_metric_value:
                    delta = 100
                    delta_type = WorkflowView.DeltaType.UP
                elif prev_metric_value and not metric_value:
                    delta = 100
                    delta_type = WorkflowView.DeltaType.DOWN
                elif not prev_metric_value and not metric_value:
                    delta = None
                    delta_type = None
                else:
                    delta = abs(round((metric_value / prev_metric_value) - 1.0, 2)) * 100
                    if metric_value >= prev_metric_value:
                        delta_type = WorkflowView.DeltaType.UP
                    else:
                        delta_type = WorkflowView.DeltaType.DOWN

        return metric_value, delta, delta_type

    def process_workflow_config(self, workflow_config):

        compare_to = workflow_config.get('compare_to')
        nodes = workflow_config.get('nodes')

        for idx, node in enumerate(nodes):
            name = node.get('name')
            metrics = node.get('metrics')
            wb_node = Node(name, idx)

            for metric in metrics:
                metric_name = metric.get('name')
                metric_source = metric.get('source')
                metric_expr = metric.get('expr')

                metric_value, delta, delta_type = None, None, None

                if metric_source == 'Datadog':
                    metric_value, delta, delta_type = self.get_metric_from_datadog(metric_expr, compare_to)
                if metric_source == 'DrDroid':
                    metric_value, delta, delta_type = self.get_metric_from_drdroid(metric_expr, compare_to)
                if metric_source == 'Newrelic':
                    metric_value, delta, delta_type = self.get_metric_from_newrelic(metric_expr, compare_to)

                metric_status = WorkflowView.MetricStatus.GREEN
                if delta_type:
                    metric_context = get_metric_key_context(metric_name)

                    if metric_context == 'up' and delta_type == WorkflowView.DeltaType.DOWN:
                        metric_status = WorkflowView.MetricStatus.RED
                    if metric_context == 'down' and delta_type == WorkflowView.DeltaType.UP:
                        metric_status = WorkflowView.MetricStatus.RED

                if metric_status == WorkflowView.MetricStatus.RED and delta and delta > 15.0:
                    wb_node.set_status(WorkflowView.NodeStatus.BAD)

                wb_node.add_metric(WorkflowView.Node.NodeMetric(name=StringValue(value=metric_name),
                                                                      value=StringValue(value=str(metric_value)),
                                                                      metric_status=metric_status,
                                                                      delta=DoubleValue(value=delta),
                                                                      delta_type=delta_type
                                                                    ))
                wb_node.workflow_node_config = {"config": node, "compare_to": compare_to}

            self.nodes.append(wb_node)
            if idx > 0:
                edge = Edge(self.nodes[idx - 1], wb_node)
                self.edges.append(edge)
                self.nodes[idx - 1].mark_out_connection()
                self.nodes[idx].mark_in_connection()


    def get_workflow_view(self):
        data = []

        for node in self.nodes:
            data.append(
                node.get_proto()
            )

        links = []
        for edge in self.edges:
            links.append(
                edge.get_proto()
            )

        return WorkflowView(
            nodes=data,
            edges=links
        )

    def get_metric_from_newrelic(self, metric_expr, compare_to):
        metric_value, delta, delta_type = None, None, None

        self.nr_connector = NewRelicConnector(self.dtr.to_tr(), self.account.id)
        metric_value_json = self.nr_connector.fetch_metric(metric_expr)
        metric_value_compare = metric_value_json.get('value')
        if metric_value_compare is not None:
            metric_value = "{} {}".format(metric_value_json.get('value'), metric_value_json.get('unit'))
        else:
            metric_value = None

        if compare_to:
            prev_dtr = self.dtr.get_prev_dtr(compare_to)
            prev_metric_value_json = self.nr_connector.fetch_metric(metric_expr, prev_dtr.to_tr())
            prev_metric_value_compare = prev_metric_value_json.get('value')
            if metric_value_compare and not prev_metric_value_compare:
                delta = 100
                delta_type = WorkflowView.DeltaType.UP
            elif prev_metric_value_compare and not metric_value_compare:
                delta = 100
                delta_type = WorkflowView.DeltaType.DOWN
            elif not prev_metric_value_compare and not metric_value_compare:
                delta = None
                delta_type = None
            else:
                delta = abs(round(((metric_value_compare / prev_metric_value_compare) - 1.0), 2)) * 100
                if metric_value_compare >= prev_metric_value_compare:
                    delta_type = WorkflowView.DeltaType.UP
                else:
                    delta_type = WorkflowView.DeltaType.DOWN

        return metric_value, delta, delta_type



