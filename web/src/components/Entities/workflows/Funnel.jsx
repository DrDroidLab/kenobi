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
import useDidMountEffect from '../../../hooks/useDidMountEffect';
import { Dashboard } from '@mui/icons-material';
import DropoffOverlay from './DropoffOverlay';

import useTimeRange from '../../../hooks/useTimeRange';

const nodeTypes = { eventNode: EventNode };
const edgeTypes = { transactionEdge: TransactionEdge };

const Funnel = ({ funnelConfig = {}, refresh, name = '' }) => {
  const { getTimeRange } = useTimeRange();
  const {
    event_key_name = '',
    event_type_ids = [],
    filter_key_name = '',
    filter_value = ''
  } = funnelConfig;

  const [eventTypeOptions, setEventTypeOptions] = useState();
  const [eventTypeAttrOptions, setEventTypeAttrOptions] = useState([]);
  const [keyOptions, setKeyOptions] = useState([]);

  const [filteredEventTypes, setFilteredEventTypes] = useState([]);
  const [keyNames, setKeyNames] = useState([]);
  const [selectedKeyName, setSelectedKeyName] = useState(event_key_name);
  const [selectedEventTypes, setSelectedEventTypes] = useState(event_type_ids);
  const [selectedEventTypeNames, setSelectedEventTypeNames] = useState();

  const [selectedFilterKeyName, setSelectedFilterKeyName] = useState(filter_key_name);
  const [filterValue, setFilterValue] = useState(filter_value);

  const [selectedEventKeyId, setSelectedEventKeyId] = useState();

  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const [option, setOption] = useState();
  const [panelLoading, setPanelLoading] = useState(false);
  const [workflowLoaded, setWorkflowLoaded] = useState(false);

  const [searchString, setSearchString] = useState();
  const [searchResponseMessage, setSearchResponseMessage] = useState('');

  const { isOpen, toggle } = useToggle();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState();
  const [validationError, setValidationError] = useState();
  const [loading, setLoading] = useState(false);

  const [isSaveDashboardOverlayOpen, setIsSaveDashboardOverlayOpen] = useState(false);

  const [optionsLoading, setOptionsLoading] = useState(false);

  const { isOpen: isDropOffDialogOpen, toggle: toggleDropOffDialog } = useToggle();
  const [dialogLoading, setDialogLoading] = useState(false);

  const [previousNodeCount, setPreviousNodeCount] = useState();
  const [distributions, setDistributions] = useState([]);

  const [dropOffData, setDropOffData] = useState();

  const [isFunnelEdit, setFunnelIsEdit] = useState(!!Object.keys(funnelConfig).length);
  const navigate = useNavigate();

  const fetchFunnel = API.useGetFunnelV2();
  const fetchFunnelEdit = API.useGetFunnelEditV2();
  const getEntityOptions = API.useEntityCreateOptions();
  const saveDashboard = API.useSaveDashboardData();
  const getFunnelEventTypeDistribution = API.useFunnelEventTypeDistribution();

  useEffect(() => {
    setOptionsLoading(true);
    getEntityOptions(
      res => {
        setOptionsLoading(false);
        setKeyOptions(res.data.entity_options?.event_key_options);

        let entityOptions = groupedData3(res);
        let c = entityOptions[0];
        setEventTypeOptions(c);
        let d = entityOptions[1];
        setEventTypeAttrOptions(d);

        const keys = Array.from(getKeyNames(res));
        let keyNameList = [];
        for (const idx in keys) {
          keyNameList.push({ id: keys[idx], label: keys[idx] });
        }
        setKeyNames(keyNameList);

        if (selectedKeyName) {
          const filteredKeyOptions = res.data.entity_options?.event_key_options.filter(
            item => item.key == selectedKeyName
          );
          let funnelEvents = [];
          for (const idx in filteredKeyOptions) {
            funnelEvents.push({
              id: filteredKeyOptions[idx].event_type.id,
              label: filteredKeyOptions[idx].event_type.name
            });
          }
          setFilteredEventTypes(funnelEvents);
          setPanelLoading(true);
        }
      },
      err => {
        setOptionsLoading(false);
        console.error(err);
      }
    );
  }, []);

  useEffect(() => {
    if (panelLoading) {
      if (selectedKeyName && selectedEventTypes.length >= 2) {
        setWorkflowLoaded(false);
        setNodes([]);
        setEdges([]);
        if (!isFunnelEdit) {
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
                setSubmitError('No funnel found');
                toggleError(true);
              }

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
              setSubmitError('No funnel found');
              toggleError(true);
            }

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
    }
  }, [panelLoading]);

  const handleFilterAttributeChange = id => {
    setFilterValue('');
    setSelectedFilterKeyName(id);
  };

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

  const onEdgeClick = (event, edge) => {
    setDialogLoading(true);
    const { data } = edge;
    setDropOffData(data);
    getFunnelEventTypeDistribution(
      {
        start_event_type_id: data.start_node_id,
        end_event_type_id: data.end_node_id,
        funnel_key_name: data.funnel_key_name,
        filter_key_name: data.selectedFilterKeyName,
        filter_value: data.filterValue,
        funnel_event_type_ids: data.selectedEventTypes
      },
      res => {
        setDialogLoading(false);
        const { previous_node_count, funnel_event_type_distribution } = res.data;
        setPreviousNodeCount(previous_node_count);
        setDistributions(funnel_event_type_distribution);
        toggleDropOffDialog();
      },
      err => {
        setDialogLoading(false);
      }
    );
  };
  const onEdgesChange = changes => {
    setEdges(eds => applyEdgeChanges(changes, eds));
  };

  const handleSubmit = () => {
    if (!isFunnelEdit) {
      /// validation for create flow of funnel
      const timeRange = getTimeRange();
      const { time_geq, time_lt } = timeRange;
      if (time_lt - time_geq > 3600) {
        toggle(true);
        setValidationError('Time range should be less than or equal to an hour');
        return;
      }
    }
    if (selectedEventTypes.length > 8) {
      toggle(true);
      setValidationError('Only upto 8 events allowed');
      return;
    }
    if (selectedEventTypes.length < 2) {
      toggle(true);
      setValidationError('Minimum 2 events required');
      return;
    }
    setPanelLoading(true);
  };

  useDidMountEffect(() => {
    setPanelLoading(true);
  }, [refresh]);

  const handleEventTypeNamesChange = val => {
    setSelectedEventTypeNames(val);
    const inputIds = val.split(',').map(idStr => idStr.trim());
    const idMap = {};
    let extractedIds = [];

    for (const element of filteredEventTypes) {
      idMap[element.label] = element.id;
    }

    for (const id of inputIds) {
      if (idMap[id]) {
        extractedIds.push(idMap[id]);
      }
    }

    setSelectedEventTypes(extractedIds);
  };

  const handleEventTypeChange = ids => {
    setSelectedEventTypes(ids);
  };

  const handleFilterValueChange = val => {
    setFilterValue(val);
  };

  const handleSubmitSave = () => {
    if (selectedKeyName && selectedEventTypes.length > 8) {
      toggle(true);
      setValidationError('Only upto 8 events allowed');
      return;
    }

    if (selectedKeyName && selectedEventTypes.length < 2) {
      toggle(true);
      setValidationError('Minimum 2 events required');
      return;
    }

    setIsSaveDashboardOverlayOpen(true);
  };

  const handleSaveWithName = name => {
    setIsSaveDashboardOverlayOpen(false);

    let panelData = {
      type: 4,
      funnel: {
        event_key_name: selectedKeyName,
        event_type_ids: selectedEventTypes,
        filter_key_name: selectedFilterKeyName,
        filter_value: filterValue
      }
    };
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

  const handleDropoffDialogClose = () => {
    toggleDropOffDialog(false);
  };
  return (
    <div>
      <Backdrop sx={{ zIndex: theme => theme.zIndex.drawer, position: 'absolute' }} open={loading}>
        <CircularProgress />
      </Backdrop>
      {Object.keys(funnelConfig).length === 0 && (
        <Heading heading="Funnel" onTimeRangeChangeCb={loadingCb} onRefreshCb={loadingCb} />
      )}
      <SuspenseLoader loading={optionsLoading} loader={<TableSkeleton noOfLines={6} />}>
        <div className={styles['container']}>
          <div className={styles['eventTypeSelectionSection']}>
            <div className={styles['content-centre']}>Funnel Attribute</div>
            <SelectComponent
              data={keyNames}
              placeholder="Select attribute"
              onSelectionChange={id => handleAttributeChange(id)}
              selected={selectedKeyName}
              className={styles['selectList']}
              searchable={true}
              disabled={isFunnelEdit}
            />
            {selectedKeyName && (
              <>
                <div className={styles['content-centre']}>Funnel Events</div>
                <MultiSelectComponent
                  data={filteredEventTypes}
                  placeholder="Select Events for the funnel"
                  onSelectionChange={handleEventTypeChange}
                  selectedValues={selectedEventTypes || []}
                  className={styles['selectList']}
                  searchable={true}
                  disabled={isFunnelEdit}
                />
              </>
            )}
          </div>

          {selectedEventTypes.length >= 2 && (
            <div className={styles['eventTypeSelectionSection']}>
              <div className={styles['content-centre']}>Filter</div>
              <SelectComponent
                data={keyNames}
                placeholder="Select attribute"
                onSelectionChange={id => handleFilterAttributeChange(id)}
                selected={selectedFilterKeyName}
                className={styles['selectList']}
                searchable={true}
              />
              <p>=</p>
              {selectedFilterKeyName && (
                <ValueComponent
                  valueType={'STRING'}
                  onValueChange={handleFilterValueChange}
                  value={filterValue}
                  placeHolder={'Enter filter value'}
                />
              )}
            </div>
          )}

          {selectedEventTypes.length >= 2 && selectedKeyName && (
            <div className={styles['eventTypeSelectionSection']}>
              <button className={styles['submitButton']} onClick={handleSubmit}>
                See Funnel
              </button>
              {!isFunnelEdit && (
                <button className={styles['submitButton']} onClick={handleSubmitSave}>
                  Save
                </button>
              )}
            </div>
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
              onEdgeClick={onEdgeClick}
              fitView
            >
              <Controls showInteractive={false} />
              <Background color="#f3f3f5" />
            </ReactFlow>
          </SuspenseLoader>
        </div>
      </SuspenseLoader>

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
      <SaveDashboardOverlay
        isOpen={isSaveDashboardOverlayOpen}
        close={() => setIsSaveDashboardOverlayOpen(false)}
        saveCallback={handleSaveWithName}
      />
      <DropoffOverlay
        isOpen={isDropOffDialogOpen}
        previousNodeCount={previousNodeCount}
        distributions={distributions}
        clickedEdgeData={dropOffData}
        onClose={handleDropoffDialogClose}
      />
      <Backdrop
        sx={{ zIndex: theme => theme.zIndex.drawer, position: 'fixed', top: '0px', left: '0px' }}
        open={dialogLoading}
      >
        <CircularProgress />
      </Backdrop>
    </div>
  );
};

export default Funnel;
