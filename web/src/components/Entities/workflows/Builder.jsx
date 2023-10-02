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

const Builder = () => {
  const [refresh, setRefresh] = useState(false);
  const [workflowLoading, setWorkflowLoading] = useState(false);
  const [workflowConfig, setWorkflowConfig] = useState(
    '{"compare_to":"1d","nodes":[{"name":"ingestion API","metrics":[{"name":"Hits","source":"Datadog","expr":"sum:trace.django.request.hits{env:prod,service:ingest}.as_count()"},{"name":"Errors","source":"Datadog","expr":"sum:trace.django.request.errors{env:prod,service:ingest}.as_count()"}]},{"name":"Raw Packets Accepted","metrics":[{"name":"Hits","source":"Datadog","expr":"sum:trace.kafka_consumer.raw_events.consume_msgs.hits{env:prod,service:raw-events-consumer-ingest}.as_count()"}]}]}'
  );

  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const buildWorkflow = API.useWorkflowBuilder();
  const saveDashboard = API.useSaveDashboardData();

  const [loading, setLoading] = useState(false);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalConfig, setModalConfig] = useState(null);

  const navigate = useNavigate();

  const [isSaveDashboardOverlayOpen, setIsSaveDashboardOverlayOpen] = useState(false);

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

  const handleTimeRangeChange = () => {
    handleSubmit();
  };

  const handleWorkflowConfigChange = val => {
    setWorkflowConfig(val);
  };

  const validateWorkflowConfig = () => {
    try {
      JSON.parse(workflowConfig);
      return false;
    } catch (error) {
      return true;
    }
  };

  const handlePrettify = () => {
    const validationMsg = validateWorkflowConfig();
    if (validationMsg) {
      alert('Invalid Workflow Config');
      return;
    } else {
      let obj = JSON.parse(workflowConfig);
      let pretty = JSON.stringify(obj, undefined, 4);
      setWorkflowConfig(pretty);
    }
  };

  const handleSubmitSave = () => {
    const validationMsg = validateWorkflowConfig();
    if (validationMsg) {
      alert('Invalid Workflow Config');
      return;
    } else {
      setIsSaveDashboardOverlayOpen(true);
    }
  };

  const handleSaveWithName = name => {
    setIsSaveDashboardOverlayOpen(false);

    let panelData = { type: 5, workflow: { workflow_config: workflowConfig } };
    let panelName = name;

    setLoading(true);
    saveDashboard(
      {
        dashboard: {
          name: panelName,
          panels: [{ meta_info: { name: panelName }, data: panelData }]
        }
      },
      res => {
        setLoading(false);
        navigate(`/dashboard/${btoa(panelName)}`);
      },
      err => {
        setLoading(false);
        console.error(err);
      }
    );
  };

  const handleSubmit = () => {
    const validationMsg = validateWorkflowConfig();
    if (validationMsg) {
      alert('Invalid Workflow Config');
      return;
    } else {
      setWorkflowLoading(true);
      buildWorkflow(
        { workflow_config: workflowConfig },
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
    }
  };

  return (
    <>
      <Heading
        heading={'Workflow Builder'}
        onTimeRangeChangeCb={handleTimeRangeChange}
        onRefreshCb={handleTimeRangeChange}
      />

      <Backdrop sx={{ zIndex: theme => theme.zIndex.drawer, position: 'absolute' }} open={loading}>
        <CircularProgress />
      </Backdrop>

      <div className={styles['container']}>
        <div className={styles['workflowContent']}>
          <div className={styles['workflowConfig']}>
            <span style={{ color: '#9553FE', fontSize: '16px', marginLeft: '5px' }}>
              <a href="https://docs.drdroid.io/docs/workflow-builder" target="_blank">
                <b>How this works?</b>
              </a>
            </span>
            <br></br>
            <textarea
              className={styles['textValueContainer']}
              placeholder={'Enter workflow JSON config...'}
              onChange={e => handleWorkflowConfigChange(e.target.value)}
              value={workflowConfig}
            />
            <button className={styles['submitButton']} onClick={handlePrettify}>
              Prettify
            </button>
            <button className={styles['submitButton']} onClick={handleSubmit}>
              Visualize
            </button>
            <button className={styles['submitButton']} onClick={handleSubmitSave}>
              Save
            </button>
            <span style={{ color: '#9553FE', fontSize: '12px', marginLeft: '5px' }}>
              <a href="https://docs.drdroid.io/docs/creating-metric-expressions" target="_blank">
                <u>How to create metric expressions</u>
              </a>
            </span>
          </div>
          <div className={styles['vl']}></div>
          <div className={styles['workflowPlot']}>
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
        <SaveDashboardOverlay
          isOpen={isSaveDashboardOverlayOpen}
          close={() => setIsSaveDashboardOverlayOpen(false)}
          saveCallback={handleSaveWithName}
        />
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

export default Builder;
