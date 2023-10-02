import React, { useCallback, useEffect, useState } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
  applyEdgeChanges,
  applyNodeChanges
} from 'reactflow';

import ValueComponent from '../../ValueComponent';

import SuspenseLoader from '../../Skeleton/SuspenseLoader';
import TableSkeleton from '../../Skeleton/TableLoader';

import { processWorkflowData, getLayoutedElements } from './utils';

import API from '../../../API';

import EventNode from './EventNode';
import TransactionEdge from './TransactionEdge';

import 'reactflow/dist/style.css';

import { initialNodes, initialEdges } from './sampleData';
import styles from './index.module.css';

const nodeTypes = { eventNode: EventNode };
const edgeTypes = { transactionEdge: TransactionEdge };

const Workflow = ({ loading, entity_id }) => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [panelLoading, setPanelLoading] = useState(false);
  const [workflowLoaded, setWorkflowLoaded] = useState(false);

  const [searchString, setSearchString] = useState();
  const [searchResponseMessage, setSearchResponseMessage] = useState('');

  const fetchEntityWorkflow = API.useGetEntityWorkflow();

  useEffect(() => {
    setPanelLoading(true);
    setWorkflowLoaded(false);
    fetchEntityWorkflow(
      { entity_id: entity_id },
      res => {
        const processedData = processWorkflowData(res.data);

        const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
          processedData.processedNodes,
          processedData.processedEdges,
          'LR'
        );

        setNodes(layoutedNodes);
        setEdges(layoutedEdges);
        setPanelLoading(false);
        setWorkflowLoaded(true);
      },
      err => {
        console.error(err);
        setPanelLoading(false);
        setWorkflowLoaded(false);
      }
    );
  }, [loading]);

  const onNodesChange = useCallback(
    changes => setNodes(nds => applyNodeChanges(changes, nds)),
    [setNodes]
  );

  const onEdgesChange = useCallback(
    changes => setEdges(eds => applyEdgeChanges(changes, eds)),
    [setEdges]
  );

  const handleSubmitSearch = () => {
    setPanelLoading(true);
    setWorkflowLoaded(false);
    setSearchResponseMessage('');
    fetchEntityWorkflow(
      { entity_id: entity_id, entity_instance_value: searchString },
      res => {
        const processedData = processWorkflowData(res.data);

        if (hasOwnProperty.call(processedData, 'message')) {
          setSearchResponseMessage(processedData['message']);
        }

        const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
          processedData.processedNodes,
          processedData.processedEdges,
          'LR'
        );

        setNodes(layoutedNodes);
        setEdges(layoutedEdges);
        setPanelLoading(false);
        setWorkflowLoaded(true);
      },
      err => {
        console.error(err);
        setPanelLoading(false);
        setWorkflowLoaded(false);
      }
    );
  };

  const handleSearch = val => {
    setSearchString(val);
  };

  return (
    <div
      style={{
        width: '84vw',
        height: '75vh',
        background: 'white',
        border: '1px solid #8080804d',
        borderRadius: '5px',
        margin: '10px'
      }}
    >
      <div className={styles['searchEntity']}>
        <ValueComponent
          valueType={'STRING'}
          onValueChange={handleSearch}
          value={searchString}
          placeHolder={'Entity Value'}
          length={500}
        />
        <button
          className={styles['submitButton']}
          onClick={handleSubmitSearch}
          style={{
            marginLeft: '12px',
            marginBottom: '12px'
          }}
        >
          Search
        </button>
        <span className={styles['dataCount']}>{searchResponseMessage}</span>
      </div>
      <SuspenseLoader loading={!!panelLoading} loader={<TableSkeleton noOfLines={6} />}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
        >
          <Controls showInteractive={false} />
          <Background color="#f3f3f5" />
        </ReactFlow>
      </SuspenseLoader>
    </div>
  );
};

export default Workflow;
