from collections import defaultdict

from google.protobuf.wrappers_pb2 import BoolValue, UInt64Value, StringValue, DoubleValue

from protos.event.entity_pb2 import FunnelView, WorkflowView


def get_duration(ts1, ts2):
    return (ts2 - ts1).seconds


def get_dag_values(event_type_ids, event_type_names, event_timestamps):
    unique_dict = {}
    result = []

    for timestamp, type_name, type_id in zip(event_timestamps, event_type_names, event_type_ids):
        type_tuple = (type_id, type_name)
        if type_tuple not in unique_dict:
            unique_dict[type_tuple] = []
        unique_dict[type_tuple].append(timestamp)

    for type_tuple, timestamps in unique_dict.items():
        timestamp_elements_count = len(timestamps)
        result.append((type_tuple[0], type_tuple[1], timestamps[timestamp_elements_count - 1]))

    return result


class Node:

    def __init__(self, event_type_name, event_type_id):
        self.name = event_type_name
        self.id = event_type_id
        self.counter = 0
        self.owners = set()
        self.has_in_connections = False
        self.has_out_connections = False

    def __str__(self):
        return "{} (Count: {})".format(self.name, self.counter)

    def incr(self, owner):
        self.counter += 1
        self.owners.add(owner)

    def mark_in_connection(self):
        self.has_in_connections = True

    def mark_out_connection(self):
        self.has_out_connections = True

    def get_proto(self):
        conn_types = []

        if self.has_in_connections:
            conn_types.append(WorkflowView.NodeConnectionType.IN)
        if self.has_out_connections:
            conn_types.append(WorkflowView.NodeConnectionType.OUT)

        return WorkflowView.Node(
            node_id=UInt64Value(value=self.id), label=StringValue(value=self.name),
            status=WorkflowView.NodeStatus.GOOD,
            connection_types=conn_types,
            metrics=[
                WorkflowView.Node.NodeMetric(name=StringValue(value="Count"),
                                             value=StringValue(value=str(self.counter)),
                                             metric_status=WorkflowView.MetricStatus.GREEN)
            ]
        )


class Edge:

    def __init__(self, start: Node, end: Node):
        self.start = start
        self.end = end
        self.counter = 0
        self.owners = []
        self.durations = []
        start.mark_out_connection()
        end.mark_in_connection()

    def __str__(self):
        return "{} - {} (Count: {})".format(self.start.name, self.end.name, self.counter)

    def add_edge(self, edge_owner, edge_duration):
        self.counter += 1
        self.owners.append(edge_owner)
        self.durations.append(edge_duration)

    def print(self):
        print("{} -> {} ({}, {})".format(self.start.name, self.end.name, len(self.owners), self.owners[:1]))

    def get_proto(self):
        avg_duration = round((sum(self.durations) / self.counter), 2)
        return WorkflowView.Edge(
            start_node_id=UInt64Value(value=self.start.id),
            end_node_id=UInt64Value(value=self.end.id),
            metrics=[
                WorkflowView.Edge.EdgeMetric(name=StringValue(value="Txn Count"),
                                             value=StringValue(value=str(self.counter)),
                                             metric_status=WorkflowView.MetricStatus.GREEN),
                WorkflowView.Edge.EdgeMetric(name=StringValue(value="Avg Time"),
                                             value=StringValue(value="{} sec".format(str(avg_duration))),
                                             metric_status=WorkflowView.MetricStatus.GREEN)
            ],
        )


class Funnel:

    def __init__(self):
        self.node_map = {}
        self.edge_map = {}
        pass

    def add_to_node_map(self, grouped_event, filter_key_name=None, filter_value=None):
        event_type_id_group = grouped_event.event_type_id_group
        event_type_name_group = grouped_event.event_type_name_group
        timestamp_group = grouped_event.timestamp_group
        dag_values = get_dag_values(event_type_id_group, event_type_name_group, timestamp_group)
        owner = grouped_event.e_id

        if filter_key_name and filter_value:
            filter_group = grouped_event.filter_group
            if filter_value.lower() not in list(x.lower() for x in filter_group):
                return

        for idx in range(0, len(dag_values)):
            if dag_values[idx][0] not in self.node_map:
                self.node_map[dag_values[idx][0]] = Node(dag_values[idx][1], dag_values[idx][0])
            self.node_map[dag_values[idx][0]].incr(owner)
            if idx + 1 < len(dag_values):
                if dag_values[idx + 1][0] not in self.node_map:
                    self.node_map[dag_values[idx + 1][0]] = Node(dag_values[idx + 1][1], dag_values[idx + 1][0])
                if dag_values[idx][0] != dag_values[idx + 1][0]:
                    edge_key = "{}-{}".format(dag_values[idx][0], dag_values[idx + 1][0])
                    if edge_key not in self.edge_map:
                        self.edge_map[edge_key] = Edge(self.node_map[dag_values[idx][0]],
                                                       self.node_map[dag_values[idx + 1][0]])
                    self.edge_map[edge_key].add_edge(owner,
                                                     get_duration(dag_values[idx][2], dag_values[idx + 1][2]))

    def get_funnel_data(self):
        data = []
        for node in self.node_map.values():
            data.append(
                node.get_proto()
            )

        links = []
        acyclic_edges = self.edge_map.values()
        for edge in acyclic_edges:
            links.append(
                edge.get_proto()
            )

        return WorkflowView(
            nodes=data,
            edges=links
        )

    def get_funnel_drop_records(self, funnel_event_type_ids, start_event_type_id, end_event_type_id):
        prev_node = self.node_map.get(funnel_event_type_ids[0])
        funnel_records = prev_node.owners

        for idx, event_type_id in enumerate(funnel_event_type_ids[1:]):
            node = self.node_map.get(event_type_id)
            if node:
                if prev_node.id == start_event_type_id and node.id == end_event_type_id:
                    dropped_funnel_records = funnel_records - node.owners
                    return dropped_funnel_records, funnel_records

                prev_node = node
                funnel_records = funnel_records & node.owners

        return set(), set()

    def get_ordered_funnel_data(self, funnel_event_type_ids):
        data = []
        links = []

        prev_node = self.node_map.get(funnel_event_type_ids[0])
        if prev_node:
            funnel_records = prev_node.owners
            prev_record_count = len(funnel_records)
            data.append(
                WorkflowView.Node(
                    node_id=UInt64Value(value=prev_node.id), label=StringValue(value=prev_node.name),
                    connection_types=[WorkflowView.NodeConnectionType.OUT],
                    metrics=[
                        WorkflowView.Node.NodeMetric(name=StringValue(value="Count"),
                                                     value=StringValue(value=str(prev_record_count)),
                                                     metric_status=WorkflowView.MetricStatus.GREEN)
                    ]
                )
            )

            for idx, event_type_id in enumerate(funnel_event_type_ids[1:]):
                node = self.node_map.get(event_type_id)
                if node:
                    funnel_records = funnel_records & node.owners
                    funnel_records_count = len(funnel_records)

                    conn_types = [WorkflowView.NodeConnectionType.IN, WorkflowView.NodeConnectionType.OUT]
                    if idx == len(funnel_event_type_ids) - 2:
                        conn_types = [WorkflowView.NodeConnectionType.IN]

                    data.append(
                        WorkflowView.Node(
                            node_id=UInt64Value(value=node.id), label=StringValue(value=node.name),
                            connection_types=conn_types,
                            metrics=[
                                WorkflowView.Node.NodeMetric(name=StringValue(value="Count"),
                                                             value=StringValue(value=str(funnel_records_count)),
                                                             metric_status=WorkflowView.MetricStatus.GREEN)
                            ]
                        )
                    )
                    edge = self.edge_map.get("{}-{}".format(prev_node.id, node.id))
                    drop_percent = 0
                    if prev_record_count > 0 and funnel_records_count > 0:
                        drop_percent = round(((prev_record_count - funnel_records_count) * 100 / prev_record_count), 2)
                    if edge:
                        avg_duration = round((sum(edge.durations) / edge.counter), 2)
                        links.append(
                            WorkflowView.Edge(
                                start_node_id=UInt64Value(value=prev_node.id),
                                end_node_id=UInt64Value(value=node.id),
                                metrics=[
                                    WorkflowView.Edge.EdgeMetric(name=StringValue(value="Drop"),
                                                                 value=StringValue(
                                                                     value="{}%".format(str(drop_percent))),
                                                                 metric_status=WorkflowView.MetricStatus.GREEN),
                                    WorkflowView.Edge.EdgeMetric(name=StringValue(value="Avg Time"),
                                                                 value=StringValue(
                                                                     value="{} sec".format(str(avg_duration))),
                                                                 metric_status=WorkflowView.MetricStatus.GREEN)
                                ],
                            )
                        )
                    prev_node = node
                    prev_record_count = funnel_records_count

        return WorkflowView(
            nodes=data,
            edges=links
        )
