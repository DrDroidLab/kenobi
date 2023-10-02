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

import { CircularProgress } from '@mui/material';
import Backdrop from '@mui/material/Backdrop';

import { randomString } from '../../../utils/utils';

import EventNode from './EventNode';
import TransactionEdge from './TransactionEdge';

import ValueComponent from '../../ValueComponent';
import SelectComponent from '../../SelectComponent';
import MultiSelectComponent from '../../MultiSelectComponent';
import Heading from '../../Heading';

import SaveDashboardOverlay from '../../Dashboard/SaveDashboardOverlay';

import cross from '../../../data/cross.svg';

import { useNavigate, useParams } from 'react-router-dom';

import { processWorkflowData, getLayoutedElements } from './utils';

import cx from 'classnames';

import SuspenseLoader from '../../Skeleton/SuspenseLoader';
import TableSkeleton from '../../Skeleton/TableLoader';
import Toast from '../../Toast';

import API from '../../../API';

import { groupedData3, getKeyNames } from '../../../utils/CreateMonitor';

import 'reactflow/dist/style.css';

import useToggle from '../../../hooks/useToggle';

import styles from './index.module.css';

const nodeTypes = { eventNode: EventNode };
const edgeTypes = { transactionEdge: TransactionEdge };

const FunnelView = ({ funnelConfig, refresh }) => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const [panelLoading, setPanelLoading] = useState();

  const fetchFunnel = API.useGetFunnelV2();

  const onNodesChange = useCallback(
    changes => setNodes(nds => applyNodeChanges(changes, nds)),
    [setNodes]
  );

  const onEdgesChange = useCallback(
    changes => setEdges(eds => applyEdgeChanges(changes, eds)),
    [setEdges]
  );

  const refreshFunnel = () => {
    const selectedKeyName = funnelConfig.event_key_name;
    const selectedEventTypes = funnelConfig.event_type_ids;
    const selectedFilterKeyName = funnelConfig.filter_key_name;
    const filterValue = funnelConfig.filter_value;

    setPanelLoading(true);

    if (selectedKeyName && selectedEventTypes.length >= 2) {
      setNodes([]);
      setEdges([]);
      fetchFunnel(
        {
          event_key_name: selectedKeyName,
          event_type_ids: selectedEventTypes,
          filter_key_name: selectedFilterKeyName,
          filter_value: filterValue
        },
        res => {
          if (res.data.workflow_view.nodes) {
            const processedData = processWorkflowData(
              res.data,
              selectedKeyName,
              selectedEventTypes,
              selectedFilterKeyName,
              filterValue
            );

            const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
              processedData.processedNodes,
              processedData.processedEdges,
              'LR'
            );

            setNodes(layoutedNodes);
            setEdges(layoutedEdges);
          } else {
            alert('No funnel found');
          }

          setPanelLoading(false);
        },
        err => {
          console.error(err);
          setPanelLoading(false);
        }
      );
    }
  };

  useEffect(() => {
    setPanelLoading(!panelLoading);
  }, [refresh]);

  useEffect(() => {
    if (panelLoading) {
      refreshFunnel();
    }
  }, [panelLoading]);

  return (
    <div>
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
    </div>
  );
};

export default FunnelView;
