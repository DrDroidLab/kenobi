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

import { randomString } from '../../../utils/utils';

import ValueComponent from '../../ValueComponent';
import SelectComponent from '../../SelectComponent';
import Heading from '../../Heading';

import SuspenseLoader from '../../Skeleton/SuspenseLoader';
import TableSkeleton from '../../Skeleton/TableLoader';
import Toast from '../../Toast';

import { processWorkflowData, getLayoutedElements } from './utils';

import API from '../../../API';

import EventNode from './EventNode';
import TransactionEdge from './TransactionEdge';
import { groupedData3 } from '../../../utils/CreateMonitor';

import 'reactflow/dist/style.css';

import useToggle from '../../../hooks/useToggle';

import styles from './index.module.css';

const nodeTypes = { eventNode: EventNode };
const edgeTypes = { transactionEdge: TransactionEdge };

const FunnelBackup = () => {
  const [eventTypeOptions, setEventTypeOptions] = useState();
  const [eventTypeAttrOptions, setEventTypeAttrOptions] = useState([]);

  const [selectedEventKeyId, setSelectedEventKeyId] = useState();

  const [eventsList, setEventsList] = useState([
    { event_type_id: null, event_key_id: null, id: randomString() }
  ]);

  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [panelLoading, setPanelLoading] = useState(false);
  const [workflowLoaded, setWorkflowLoaded] = useState(false);

  const [searchString, setSearchString] = useState();
  const [searchResponseMessage, setSearchResponseMessage] = useState('');

  const { isOpen, toggle } = useToggle();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState();
  const [validationError, setValidationError] = useState();
  const [loading, setLoading] = useState(false);

  const [refreshWorkflow, setRefreshWorkflow] = useState();

  const fetchFunnel = API.useGetFunnel();
  const getEntityOptions = API.useEntityCreateOptions();

  useEffect(() => {
    getEntityOptions(
      res => {
        let entityOptions = groupedData3(res);

        let c = entityOptions[0];
        setEventTypeOptions(c);
        let d = entityOptions[1];
        setEventTypeAttrOptions(d);
      },
      err => {
        console.error(err);
      }
    );
  }, []);

  const handleEventTypeChange = (id, item_id) => {
    const selectedListItem = eventsList.find(item => item.id === item_id);

    const options =
      eventTypeAttrOptions[id]?.map(option => ({
        id: option?.id,
        label: option?.name,
        type: option?.type
      })) || [];

    eventsList.splice(
      eventsList.findIndex(item => item.id === item_id),
      1,
      {
        ...selectedListItem,
        event_type_id: id,
        event_attribution_options: options
      }
    );

    setEventsList([...eventsList]);
  };

  const handleAttributeTypeChange = (id, item_id) => {
    const selectedListItem = eventsList.find(item => item.id === item_id);

    eventsList.splice(
      eventsList.findIndex(item => item.id === item_id),
      1,
      {
        ...selectedListItem,
        event_key_id: id
      }
    );

    setEventsList([...eventsList]);
  };

  const onNodesChange = useCallback(
    changes => setNodes(nds => applyNodeChanges(changes, nds)),
    [setNodes]
  );

  const onEdgesChange = useCallback(
    changes => setEdges(eds => applyEdgeChanges(changes, eds)),
    [setEdges]
  );

  const loadingCb = () => {
    handleSubmit();
  };

  const renderAttributeList = list => {
    return list.map(item => (
      <div className={styles['eventTypeSelectionSection']}>
        <div className={styles['content']}>Start Event</div>
        <SelectComponent
          data={eventTypeOptions}
          placeholder="Select event type"
          onSelectionChange={id => handleEventTypeChange(id, item.id)}
          selected={item.event_type_id}
          className={styles['selectList']}
          searchable={true}
        />
        {item.event_type_id && (
          <>
            <div className={styles['content-centre']}>Attribute</div>
            <SelectComponent
              data={item.event_attribution_options}
              placeholder="Select attribute"
              onSelectionChange={id => handleAttributeTypeChange(id, item.id)}
              selected={item.event_key_id}
              className={styles['selectList']}
              searchable={true}
            />
          </>
        )}
      </div>
    ));
  };

  useEffect(() => {
    if (panelLoading) {
      setWorkflowLoaded(false);
      fetchFunnel(
        { event_key_id: eventsList[0].event_key_id },
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
    }
  }, [panelLoading]);

  const handleSubmit = () => {
    setPanelLoading(true);
  };

  return (
    <div>
      <Heading heading="Funnel" onTimeRangeChangeCb={loadingCb} onRefreshCb={loadingCb} />

      <div className={styles['container']}>
        {eventsList?.length >= 1 && renderAttributeList(eventsList)}
        {eventsList?.length >= 1 && eventsList[0]?.event_key_id && (
          <button
            className={styles['submitButton']}
            onClick={handleSubmit}
            style={{
              marginLeft: '50px',
              marginBottom: '12px'
            }}
          >
            See Funnel
          </button>
        )}
      </div>

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

      <Toast
        open={!!isOpen}
        severity="info"
        message={validationError}
        handleClose={() => toggle()}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      />
      <Toast
        open={!!IsError}
        severity="error"
        message={submitError}
        handleClose={() => toggleError()}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      />
    </div>
  );
};

export default FunnelBackup;
