import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType
} from 'reactflow';

export const initialNodes = [
  {
    id: '1',
    position: { x: 100, y: 200 },
    data: {
      nodeConnections: ['out'],
      label: 'OrderCreated',
      labelStatus: 'good',
      metrics: [{ name: 'Count', value: '547', status: 'red' }]
    },
    type: 'eventNode'
  },
  {
    id: '2',
    position: { x: 350, y: 200 },
    data: {
      nodeConnections: ['in', 'out'],
      label: 'DriverFetched',
      labelStatus: 'bad',
      metrics: [
        { name: 'Avg', value: '22.9', status: 'green' },
        { name: 'p99', value: '1.08', status: 'red' }
      ]
    },
    type: 'eventNode'
  },
  {
    id: '3',
    position: { x: 600, y: 150 },
    data: {
      nodeConnections: ['in'],
      label: 'Allocation Done',
      labelStatus: 'good',
      metrics: [
        { name: 'Avg', value: '22.9', status: 'green' },
        { name: 'p99', value: '1.08', status: 'red' }
      ]
    },
    type: 'eventNode'
  },
  {
    id: '4',
    position: { x: 650, y: 380 },
    data: {
      nodeConnections: ['in'],
      label: 'Cancelled',
      labelStatus: 'good',
      metrics: [{ name: 'Avg', value: '22.9', status: 'green' }]
    },
    type: 'eventNode'
  }
];

export const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e2-3', source: '2', target: '3', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e2-4', source: '2', target: '4', markerEnd: { type: MarkerType.ArrowClosed } }
];
