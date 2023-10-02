import React from 'react';
import { getBezierPath, EdgeLabelRenderer, BaseEdge } from 'reactflow';

export default function TransactionEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data
}) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition
  });

  const render = data => {
    return data.metrics?.map(dm => (
      <div style={{ fontSize: '6px' }}>
        {dm.name}: <b>{dm.value}</b>
      </div>
    ));
  };

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={{
          fill: 'none',
          strokeWidth: '1px',
          stroke: '#7c3aed'
        }}
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            background: '#fff',
            padding: 2,
            borderRadius: 3,
            color: '#9553fe',
            fontSize: 5,
            pointerEvents: 'all'
          }}
          className="nodrag nopan"
        >
          {render(data)}
        </div>
      </EdgeLabelRenderer>
    </>
  );
}
