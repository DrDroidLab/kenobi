import itertools
from typing import Dict

from sortedcontainers import SortedList
from protos.event.entity_pb2 import WorkflowView
from event.models import Event, EventType

from google.protobuf.wrappers_pb2 import BoolValue, UInt64Value, StringValue, DoubleValue

class Node:
    def __init__(self, event_type_name, event_type_id):
        self.event_type_name = event_type_name
        self.events = SortedList(key=lambda e: e.timestamp)
        self.id = event_type_id
        self.edges = {}
        self.has_in_connections = False
        self.has_out_connections = False

    def __str__(self):
        return f'{self.id}:{self.event_type_name}'

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def mark_in_connection(self):
        self.has_in_connections = True

    def mark_out_connection(self):
        self.has_out_connections = True

    def add_event(self, event):
        self.events.add(event)

    def view_proto(self) -> WorkflowView.Node:
        total_count = len(self.events)

        conn_types = []
        if self.has_in_connections:
            conn_types.append(WorkflowView.NodeConnectionType.IN)
        if self.has_out_connections:
            conn_types.append(WorkflowView.NodeConnectionType.OUT)

        return WorkflowView.Node(
            node_id=UInt64Value(value=self.id), label=StringValue(value=self.event_type_name),
            status=WorkflowView.NodeStatus.GOOD,
            connection_types=conn_types,
            metrics=[
                WorkflowView.Node.NodeMetric(name=StringValue(value="Count"),
                                             value=StringValue(value=str(total_count)),
                                             metric_status=WorkflowView.MetricStatus.GREEN)
            ]
        )


class Edge:
    def __init__(self, start: Node, end: Node):
        self.start = start
        self.end = end
        self.event_pairs = SortedList(key=lambda t: (t[0].timestamp, t[1].timestamp))

    def __str__(self):
        return f'{self.start} --> {self.end}'

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

    def __hash__(self):
        return self.start, self.end

    def add_event(self, start_event, end_event):
        self.event_pairs.add((start_event, end_event))

    def view_proto(self) -> WorkflowView.Edge:
        total_transitions = len(self.event_pairs)
        time_delta = map(lambda t: t.total_seconds(), map(lambda t: t[1].timestamp - t[0].timestamp, self.event_pairs))
        return WorkflowView.Edge(
            start_node_id=UInt64Value(value=self.start.id),
            end_node_id=UInt64Value(value=self.end.id),
            metrics=[
                WorkflowView.Edge.EdgeMetric(name=StringValue(value="Txn Count"),
                                             value=StringValue(value=str(total_transitions)),
                                             metric_status=WorkflowView.MetricStatus.GREEN),
                WorkflowView.Edge.EdgeMetric(name=StringValue(value="Avg Time"),
                                             value=StringValue(value="{}s".format(str(int(sum(list(time_delta))/total_transitions)))),
                                             metric_status=WorkflowView.MetricStatus.GREEN)
            ],
        )

class Graph:
    def __init__(self):
        self._state_node_dict: Dict[str, Node] = {}
        return

    def _add_events(self, events):
        for event in events:
            self._add_event(event)

        return

    def _add_event(self, event: Event):
        if event.event_type_name not in self._state_node_dict:
            self._state_node_dict[event.event_type_name] = Node(event.event_type_name, event.event_type_id)
        node = self._state_node_dict[event.event_type_name]
        node.add_event(event)
        return

    def add_flow_events(self, events):
        # This populates the nodes
        self._add_events(events)

        for start, end in itertools.zip_longest(events, events[1:]):
            if not end:
                break
            start_node = self._state_node_dict[start.event_type_name]
            end_node = self._state_node_dict[end.event_type_name]

            if start_node.id == end_node.id:
                continue

            start_node.mark_out_connection()
            end_node.mark_in_connection()

            if end_node not in start_node.edges:
                e = Edge(start_node, end_node)
                start_node.edges[end_node] = e
            edge: Edge = start_node.edges[end_node]
            edge.add_event(start, end)

    def get_view(self) -> WorkflowView:
        nodes = []
        edges = []
        for node in self._state_node_dict.values():
            nodes.append(node.view_proto())
            for edge in node.edges.values():
                edges.append(edge.view_proto())

        return WorkflowView(
            nodes=nodes,
            edges=edges
        )


class NewNode:
    def __init__(self, event_type_name, event_type_id):
        self.event_type_name = event_type_name
        self.events = []
        self.id = event_type_id
        self.edges = {}
        self.has_in_connections = False
        self.has_out_connections = False

    def __str__(self):
        return f'{self.id}:{self.event_type_name}'

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def mark_in_connection(self):
        self.has_in_connections = True

    def mark_out_connection(self):
        self.has_out_connections = True

    def add_event(self, event):
        self.events.append(event)

    def view_proto(self) -> WorkflowView.Node:
        total_count = len(self.events)

        conn_types = []
        if self.has_in_connections:
            conn_types.append(WorkflowView.NodeConnectionType.IN)
        if self.has_out_connections:
            conn_types.append(WorkflowView.NodeConnectionType.OUT)

        return WorkflowView.Node(
            node_id=UInt64Value(value=self.id), label=StringValue(value=self.event_type_name),
            status=WorkflowView.NodeStatus.GOOD,
            connection_types=conn_types,
            metrics=[
                WorkflowView.Node.NodeMetric(name=StringValue(value="Count"),
                                             value=StringValue(value=str(total_count)),
                                             metric_status=WorkflowView.MetricStatus.GREEN)
            ]
        )

class NewEdge:
    def __init__(self, start: NewNode, end: NewNode):
        self.start = start
        self.end = end
        self.event_pairs = SortedList(key=lambda t: (t[0][2], t[1][2]))

    def __str__(self):
        return f'{self.start} --> {self.end}'

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

    def __hash__(self):
        return self.start, self.end

    def add_event(self, start_event, end_event):
        self.event_pairs.add((start_event, end_event))

    def view_proto(self) -> WorkflowView.Edge:
        total_transitions = len(self.event_pairs)
        time_delta = map(lambda t: t.total_seconds(), map(lambda t: t[1][2] - t[0][2], self.event_pairs))
        return WorkflowView.Edge(
            start_node_id=UInt64Value(value=self.start.id),
            end_node_id=UInt64Value(value=self.end.id),
            metrics=[
                WorkflowView.Edge.EdgeMetric(name=StringValue(value="Txn Count"),
                                             value=StringValue(value=str(total_transitions)),
                                             metric_status=WorkflowView.MetricStatus.GREEN),
                WorkflowView.Edge.EdgeMetric(name=StringValue(value="Avg Time"),
                                             value=StringValue(value="{}s".format(str(int(sum(list(time_delta))/total_transitions)))),
                                             metric_status=WorkflowView.MetricStatus.GREEN)
            ],
        )

class NewGraph:
    def __init__(self):
        self._state_node_dict: Dict[str, NewNode] = {}
        return

    def _add_grouped_events(self, events):
        for event in events:
            self._add_event(event)
        return

    def _add_event(self, event: tuple):
        if event[1] not in self._state_node_dict:
            self._state_node_dict[event[1]] = NewNode(event[1], event[0])
        node = self._state_node_dict[event[1]]
        node.add_event(event)
        return

    def add_flow_grouped_events(self, grouped_event):
        # This populates the nodes
        events = []
        event_type_id_group = grouped_event.event_type_id_group
        event_type_name_group = grouped_event.event_type_name_group
        timestamp_group = grouped_event.timestamp_group
        for event_type_id, event_type_name, timestamp in zip(event_type_id_group, event_type_name_group, timestamp_group):
            events.append((event_type_id, event_type_name, timestamp))

        self._add_grouped_events(events)

        for start, end in itertools.zip_longest(events, events[1:]):
            if not end:
                break

            start_node = self._state_node_dict[start[1]]
            end_node = self._state_node_dict[end[1]]

            if start_node.id == end_node.id:
                continue

            start_node.mark_out_connection()
            end_node.mark_in_connection()

            if end_node not in start_node.edges:
                e = NewEdge(start_node, end_node)
                start_node.edges[end_node] = e
            edge: NewEdge = start_node.edges[end_node]
            edge.add_event(start, end)

    def get_view(self) -> WorkflowView:
        nodes = []
        edges = []

        for node in self._state_node_dict.values():
            nodes.append(node.view_proto())
            for edge in node.edges.values():
                edges.append(edge.view_proto())

        return WorkflowView(
            nodes=nodes,
            edges=edges
        )
