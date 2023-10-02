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

import ReactECharts from 'echarts-for-react';

import { randomString } from '../../../utils/utils';

import EventNode from './EventNode';
import TransactionEdge from './TransactionEdge';

import DataToTable from './DataToTable';

import ValueComponent from '../../ValueComponent';
import SelectComponent from '../../SelectComponent';
import MultiSelectComponent from '../../MultiSelectComponent';
import CheckboxComponent from '../../CheckboxComponent';
import Heading from '../../Heading';

import cross from '../../../data/cross.svg';

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

const FunnelV3 = () => {
  const [eventTypeOptions, setEventTypeOptions] = useState();
  const [eventTypeAttrOptions, setEventTypeAttrOptions] = useState([]);
  const [keyOptions, setKeyOptions] = useState([]);

  const [filteredEventTypes, setFilteredEventTypes] = useState([]);

  const [keyNames, setKeyNames] = useState([]);
  const [selectedKeyName, setSelectedKeyName] = useState();
  const [selectedEventTypes, setSelectedEventTypes] = useState([]);

  const [selectedEventKeyId, setSelectedEventKeyId] = useState();

  const [isAllEventsSelected, setIsAllEventsSelected] = useState(false);

  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const [option, setOption] = useState();
  const [panelLoading, setPanelLoading] = useState(false);
  const [workflowLoaded, setWorkflowLoaded] = useState(false);

  const [filterValue, setFilterValue] = useState();
  const [tableData, setTableData] = useState();

  const [searchString, setSearchString] = useState();
  const [searchResponseMessage, setSearchResponseMessage] = useState('');

  const { isOpen, toggle } = useToggle();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState();
  const [validationError, setValidationError] = useState();
  const [loading, setLoading] = useState(false);

  const [refreshWorkflow, setRefreshWorkflow] = useState();

  const fetchFunnel_v3 = API.useGetFunnelV3();
  const getEntityOptions = API.useEntityCreateOptions();

  let sampleSankeyChartOptions = {
    backgroundColor: '#fff',
    title: {
      subtext: 'Funnel View',
      left: 'center'
    },
    series: [
      {
        type: 'sankey',
        left: 50.0,
        top: 100.0,
        right: 150.0,
        bottom: 25.0,
        lineStyle: {
          color: 'source',
          curveness: 0.5
        },
        itemStyle: {
          color: '#1f77b4',
          borderColor: '#1f77b4'
        },
        label: {
          color: 'rgba(0,0,0,0.7)',
          fontFamily: 'Arial',
          fontSize: 10
        }
      }
    ],
    tooltip: {
      trigger: 'item'
    }
  };

  useEffect(() => {
    setPanelLoading(true);
  }, []);

  const handleAttributeChange = id => {
    setSelectedEventTypes([]);

    setSelectedKeyName(id);
    const filteredKeyOptions = keyOptions.filter(item => item.key == id);

    let x = [];
    for (const idx in filteredKeyOptions) {
      x.push({
        id: filteredKeyOptions[idx].event_type.id,
        label: filteredKeyOptions[idx].event_type.name
      });
    }
    setFilteredEventTypes(x);
  };

  const loadingCb = () => {
    handleSubmit();
  };

  const onNodesChange = useCallback(
    changes => setNodes(nds => applyNodeChanges(changes, nds)),
    [setNodes]
  );

  const onEdgesChange = useCallback(
    changes => setEdges(eds => applyEdgeChanges(changes, eds)),
    [setEdges]
  );

  useEffect(() => {
    if (panelLoading) {
      setWorkflowLoaded(false);
      setTableData([]);
      fetchFunnel_v3(
        {
          filter_value: filterValue
        },
        res => {
          console.log(res.data);

          if (!res.data?.stages) {
            toggleError();
            setSubmitError('No data found');
          } else {
            setTableData(res.data?.stages);
          }

          // const processedData = processWorkflowData(res.data);

          // const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
          //   processedData.processedNodes,
          //   processedData.processedEdges,
          //   'LR'
          // );

          // setNodes(layoutedNodes);
          // setEdges(layoutedEdges);

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

  const handleEventTypeChange = ids => {
    setSelectedEventTypes(ids);
  };

  const handleIsAllEventsSelectedChange = e => {
    if (isAllEventsSelected) {
      setSelectedEventTypes([]);
    } else {
      setSelectedEventTypes(filteredEventTypes.map(x => x.id));
    }

    setIsAllEventsSelected(!isAllEventsSelected);
  };

  const handleFilterChange = val => {
    setFilterValue(val);
  };

  return (
    <div>
      <Heading heading="Pipeline" onTimeRangeChangeCb={loadingCb} onRefreshCb={loadingCb} />

      <div className={styles['container']}>
        <div className={styles['eventTypeSelectionSection']}>
          <ValueComponent
            valueType={'STRING'}
            onValueChange={handleFilterChange}
            value={filterValue}
            placeHolder={'Enter connectorId'}
          />

          <button className={styles['submitButton']} onClick={handleSubmit}>
            Filter
          </button>
        </div>
      </div>

      <div className={styles['container']}></div>

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
          {/*<ReactFlow
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
          </ReactFlow>*/}
          {tableData && <DataToTable data={tableData} />}
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

export default FunnelV3;
