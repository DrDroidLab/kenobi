import { MarkerType } from 'reactflow';
import dagre from 'dagre';

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 172;
const nodeHeight = 36;

export const getLayoutedElements = (nodes, edges, direction = 'TB') => {
  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach(node => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach(edge => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  nodes.forEach((node, idx) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.targetPosition = isHorizontal ? 'left' : 'top';
    node.sourcePosition = isHorizontal ? 'right' : 'bottom';

    // We are shifting the dagre node position (anchor=center center) to the top left
    // so it matches the React Flow node anchor point (top left).
    node.position = {
      x: nodeWithPosition.x - nodeWidth / 2,
      y: nodeWithPosition.y - nodeHeight / 2
    };

    return node;
  });

  return { nodes, edges };
};

export const processWorkflowData = (
  data,
  funnel_key_name,
  selectedEventTypes,
  selectedFilterKeyName,
  filterValue,
  workflowNodeClickCb
) => {
  let res = { processedNodes: [], processedEdges: [] };

  let workflow_view_data = data.workflow_view;

  if (hasOwnProperty.call(workflow_view_data, 'nodes') === false) {
    res['message'] = 'No workflow for this entity value';
    return res;
  }

  workflow_view_data.nodes.map(n => {
    res.processedNodes.push({
      id: n.node_id,
      data: {
        label: n.label,
        nodeConnections: n.connection_types,
        labelStatus: n.status,
        metrics: n.metrics,
        workflow_config: n.workflow_node_config,
        clickCb: () => {
          workflowNodeClickCb(n.workflow_node_config);
        }
      },
      type: 'eventNode'
    });
  });

  workflow_view_data.edges?.map(e => {
    res.processedEdges.push({
      id: 'e' + e.start_node_id + '-' + e.end_node_id,
      source: e.start_node_id,
      target: e.end_node_id,
      data: {
        metrics: e.metrics,
        funnel_key_name: funnel_key_name,
        start_node_id: e.start_node_id,
        end_node_id: e.end_node_id,
        selectedEventTypes: selectedEventTypes,
        selectedFilterKeyName: selectedFilterKeyName,
        filterValue: filterValue
      },
      type: 'transactionEdge',
      animated: true,
      markerEnd: { type: MarkerType.ArrowClosed }
    });
  });

  return res;
};
