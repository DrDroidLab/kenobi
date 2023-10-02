import { useCallback, useEffect, useState } from 'react';
import API from '../../../API';
import Heading from '../../../components/Heading';
import SelectComponent from '../../SelectComponent';
import ValueComponent from '../../ValueComponent';

import SaveDashboardOverlay from '../../Dashboard/SaveDashboardOverlay';

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

import EventNode from './EventNode';
import TransactionEdge from './TransactionEdge';

import { processWorkflowData, getLayoutedElements } from './utils';

import 'reactflow/dist/style.css';

import SuspenseLoader from '../../../components/Skeleton/SuspenseLoader';
import TableSkeleton from '../../../components/Skeleton/TableLoader';

import { useNavigate } from 'react-router-dom';

import NodeMetricsDialog from './NodeMetricsDialog';

import styles from './index.module.css';

const nodeTypes = { eventNode: EventNode };
const edgeTypes = { transactionEdge: TransactionEdge };

const BuilderView = ({ builderConfig, refresh }) => {
  const [workflowLoading, setWorkflowLoading] = useState(false);

  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const buildWorkflow = API.useWorkflowBuilder();

  const [loading, setLoading] = useState(false);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalConfig, setModalConfig] = useState(null);

  const openModal = config => {
    try {
      JSON.parse(config);
      setIsModalOpen(true);
      setModalConfig(config);
    } catch (error) {
      console.log('Cannot open modal');
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setModalConfig(null);
  };

  const onNodesChange = useCallback(
    changes => setNodes(nds => applyNodeChanges(changes, nds)),
    [setNodes]
  );

  const onEdgesChange = useCallback(
    changes => setEdges(eds => applyEdgeChanges(changes, eds)),
    [setEdges]
  );

  const refreshWorkflow = () => {
    buildWorkflow(
      { workflow_config: builderConfig.workflow_config },
      res => {
        if (res.data.message) {
          alert(res.data.message);
          setWorkflowLoading(false);
          return;
        }

        if (res.data.workflow_view.nodes) {
          const processedData = processWorkflowData(res.data, null, null, null, null, openModal);

          const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
            processedData.processedNodes,
            processedData.processedEdges,
            'LR'
          );

          setNodes(layoutedNodes);
          setEdges(layoutedEdges);
        } else {
          alert('Invalid Workflow Config');
        }

        setWorkflowLoading(false);
      },
      err => {
        console.error(err);
        setWorkflowLoading(false);
      }
    );
  };

  useEffect(() => {
    setWorkflowLoading(!workflowLoading);
  }, [refresh]);

  useEffect(() => {
    if (workflowLoading) {
      refreshWorkflow();
    }
  }, [workflowLoading]);

  return (
    <>
      <div className={styles['container']}>
        <div className={styles['workflowContent']}>
          <div className={styles['workflowPlotView']}>
            <div
              style={{
                width: '100%',
                height: '100%',
                background: 'white',
                border: '1px solid #8080804d',
                borderRadius: '5px'
              }}
            >
              <SuspenseLoader loading={!!workflowLoading} loader={<TableSkeleton noOfLines={10} />}>
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
        </div>
      </div>
      {isModalOpen && modalConfig && (
        <div className={styles['modal-overlay']}>
          <div className={styles['modal']}>
            <div className={styles['modal-content']}>
              <NodeMetricsDialog config={modalConfig} onClose={closeModal} />
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default BuilderView;
