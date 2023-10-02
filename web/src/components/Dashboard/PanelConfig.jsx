import { useState } from 'react';
import API from '../../API';
import SelectComponent from '../SelectComponent';
import CheckboxComponent from '../CheckboxComponent';
import SaveDashboardOverlay from './SaveDashboardOverlay';
import GroupComponent from '../GroupComponent';
import { transformToAPIPayload, transformToQueryBuilderPayload } from '../../utils/utils';
import { useNavigate } from 'react-router-dom';
import Toast from '../Toast';
import useToggle from '../../hooks/useToggle';
import {
  intervalOptions,
  metricTypes,
  nonTimeSeriesViewOptions,
  timeSeriesViewOptions
} from './constants';
import styles from './index.module.css';
import { transformEventQueryOptionsToSelectOptions } from '../Events/utils';
import FilterComponent from '../FilterComponent';
import useNode from '../../hooks/useNode.ts';
import SuspenseLoader from '../Skeleton/SuspenseLoader';
import TableSkeleton from '../Skeleton/TableLoader';
import { validatePayload } from '../../utils/QueryBuilder';
import AccordionComponent from '../AccordionComponent';
import cx from 'classnames';
import InfoIcon from '@mui/icons-material/Info';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';

const PanelConfig = ({ onVisualize }) => {
  const [queryBuilderPayload, setQueryBuilderPayload] = useState({
    op: 'AND',
    filters: []
  });
  const [metricOptions, setMetricOptions] = useState();
  const [loading, setLoading] = useState(false);
  const { insertNode, deleteNode, updateNode } = useNode();
  const [expression, setExpression] = useState({});
  const [aggregationFunctionOptions, setAggregationFunctionOptions] = useState([]);
  const [selectedMetricType, setSelectedMetricType] = useState();
  const [selectedAggregatedFunction, setSelectedAggregatedFunction] = useState();
  const [selectedAttribute, setSelectedAttribute] = useState();
  const [selectedGroupByAttributes, setSelectedGroupByAttributes] = useState([]);
  const [selectedResolution, setSelectedResolution] = useState();
  const [selectedViewOption, setSelectedViewOption] = useState();
  const [isTimeSeriesShown, setIsTimeSeriesShown] = useState(true);

  const [groupItems, setGroupItems] = useState([]);
  const [isTimeSeries, setIsTimeSeries] = useState(false);

  const [validationError, setValidationError] = useState();
  const { isOpen, toggle } = useToggle();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState();

  const [viewOptions, setViewOptions] = useState(timeSeriesViewOptions);

  const [isSaveDashboardOverlayOpen, setIsSaveDashboardOverlayOpen] = useState(false);
  const [expanded, setExpanded] = useState(true);

  const fetchMetricGlobalOptions = API.useGetGlobalMetricOptions();
  const saveDashboard = API.useSaveDashboardData();

  const navigate = useNavigate();

  const handleMetricTypeChange = id => {
    setSelectedMetricType(id);
    setLoading(true);
    fetchMetricGlobalOptions(
      id,
      res => {
        setLoading(false);
        const { default_metric_expression, metric_options } = res.data;
        const { attribute_options, aggregation_function_options, column_options } = metric_options;
        const transformedOptions = transformEventQueryOptionsToSelectOptions({
          column_options: column_options,
          attribute_options: attribute_options
        });
        const transformedPayload = transformToQueryBuilderPayload(
          {
            filter: {
              op: 'AND'
            }
          },
          transformedOptions
        );
        setMetricOptions(transformedOptions);
        setQueryBuilderPayload(transformedPayload);
        const aggregateSelectOption = aggregation_function_options.map(item => ({
          id: item.aggregation_function,
          label: item.aggregation_function,
          supports_empty_expression_selector: item.supports_empty_expression_selector
        }));
        setAggregationFunctionOptions(aggregateSelectOption);
        setExpression({});
        setSelectedAggregatedFunction();
        setSelectedAttribute(null);
        setSelectedResolution(300);
        setSelectedViewOption('BAR');
        setIsTimeSeries(true);
      },
      err => {
        setLoading(false);
        setSubmitError(err);
        console.error(err);
      }
    );
  };

  const handleAggregationFunctionChange = id => {
    setSelectedAggregatedFunction(id);
    setSelectedAttribute(null);
  };

  const handleSelectedAttributeChange = (id, item) => {
    const { optionType, type, path = undefined } = item;
    const expression = {
      [optionType]: {
        name: id,
        type: type,
        path: path
      }
    };
    setSelectedAttribute(id);
    setExpression(expression);
  };

  const handleResolutionChange = id => {
    setSelectedResolution(Number(id));
  };

  const handleViewOptionChange = id => {
    setSelectedViewOption(id);
  };

  const handleSaveWithName = panelName => {
    setIsSaveDashboardOverlayOpen(false);
    const queryAPIPayload = transformToAPIPayload(queryBuilderPayload);
    const groupByAPIPayload = groupItems.map(group => {
      return {
        [group.optionType]: {
          name: group.itemLabel,
          path: group.optionType === 'attribute_identifier' ? 'event_attribute' : undefined,
          type: group.type
        }
      };
    });

    const payload = {
      chart: {
        type: selectedViewOption,
        chart_metric_expression: {
          context: selectedMetricType,
          metric_expressions: Array(1).fill({
            filter: queryAPIPayload.filter,
            group_by: groupByAPIPayload,
            is_timeseries: isTimeSeries,
            resolution: selectedResolution,
            selectors: Array(1).fill({
              expression: expression,
              function: selectedAggregatedFunction
            })
          })
        }
      },
      type: 2
    };
    setLoading(true);
    saveDashboard(
      {
        dashboard: {
          name: panelName,
          panels: [{ meta_info: { name: panelName }, data: payload }]
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

  const handleSubmitSave = e => {
    e.stopPropagation();
    const valError = validatePayload(queryBuilderPayload);
    if (valError) {
      setValidationError(valError);
      toggle();
      return;
    }
    if (groupItems.length > 0) {
      const checkItemLabel = groupItems.some(group => !group.hasOwnProperty('itemLabel'));
      if (checkItemLabel) {
        setValidationError('Please select Group By to proceed');
        toggle();
        return;
      }
    }
    if (!selectedMetricType) {
      setValidationError('Please select metric type to proceed');
      toggle();
      return;
    }
    if (!selectedAggregatedFunction) {
      setValidationError('Please select Aggregation to proceed');
      toggle();
      return;
    }

    if (!selectedAttribute) {
      setValidationError('Please select data to proceed');
      toggle();
      return;
    }

    if (isTimeSeries) {
      if (!selectedResolution) {
        setValidationError('Please resolution to proceed');
        toggle();
        return;
      }
    }
    setIsSaveDashboardOverlayOpen(true);
  };

  const handleSubmitVisualize = () => {
    const valError = validatePayload(queryBuilderPayload);
    if (valError) {
      setValidationError(valError);
      toggle();
      return;
    }
    if (groupItems.length > 0) {
      const checkItemLabel = groupItems.some(group => !group.hasOwnProperty('itemLabel'));
      if (checkItemLabel) {
        setValidationError('Please select Group By to proceed');
        toggle();
        return;
      }
    }
    if (!selectedAggregatedFunction) {
      setValidationError('Please select Aggregation to proceed');
      toggle();
      return;
    }

    if (!selectedAttribute) {
      setValidationError('Please select data to proceed');
      toggle();
      return;
    }

    if (isTimeSeries) {
      if (!selectedResolution) {
        setValidationError('Please resolution to proceed');
        toggle();
        return;
      }
    }
    const queryAPIPayload = transformToAPIPayload(queryBuilderPayload);
    const groupByAPIPayload = groupItems.map(group => {
      return {
        [group.optionType]: {
          name: group.itemLabel,
          path: group.optionType === 'attribute_identifier' ? 'event_attribute' : undefined,
          type: group.type
        }
      };
    });

    const payload = {
      chart: {
        type: selectedViewOption,
        chart_metric_expression: {
          context: selectedMetricType,
          metric_expressions: Array(1).fill({
            filter: queryAPIPayload.filter,
            group_by: groupByAPIPayload,
            is_timeseries: isTimeSeries,
            resolution: selectedResolution,
            selectors: Array(1).fill({
              expression: expression,
              function: selectedAggregatedFunction
            })
          })
        }
      },
      type: 2
    };
    onVisualize(payload);
    setExpanded(!expanded);
  };

  const handleTimeSeriesCheckboxChange = () => {
    if (isTimeSeries) {
      setSelectedResolution();
      if (selectedGroupByAttributes.filter(item => item.selectedAttribute != '').length >= 2) {
        setSelectedViewOption('SIMPLE_TABLE');
      } else {
        setSelectedViewOption('BAR');
        setViewOptions(nonTimeSeriesViewOptions);
      }
    } else {
      setViewOptions(timeSeriesViewOptions);
      if (selectedViewOption == 'SIMPLE_TABLE') {
        setSelectedViewOption('BAR');
      }
    }
    setIsTimeSeries(!isTimeSeries);
    setSelectedResolution();
  };

  const handleAdd = ({ id, isGroup }) => {
    const tree = insertNode({
      tree: queryBuilderPayload,
      id: id,
      isGroup: isGroup
    });
    setQueryBuilderPayload({ ...tree });
  };

  const handleUpdate = ({ id, type, value, isGroup }) => {
    const tree = updateNode({ tree: queryBuilderPayload, id, value, type, isGroup });
    setQueryBuilderPayload({ ...tree });
  };

  const handleDelete = ({ id, isGroup }) => {
    const tree = deleteNode({
      tree: queryBuilderPayload,
      id,
      isGroup
    });
    setQueryBuilderPayload({ ...tree });
  };

  const handleGroupItem = items => {
    if (items.length > 1) {
      setIsTimeSeriesShown(false);
      setIsTimeSeries(false);
      setSelectedResolution();
      setViewOptions([
        {
          label: 'Table Chart',
          id: 'SIMPLE_TABLE'
        }
      ]);
      setSelectedViewOption('SIMPLE_TABLE');
    } else {
      setIsTimeSeriesShown(true);
      setIsTimeSeries(true);
      setSelectedResolution(300);
      setViewOptions(timeSeriesViewOptions);
      setSelectedViewOption('BAR');
    }
    setGroupItems([...items]);
  };

  const handleExpandedChange = () => {
    setExpanded(!expanded);
  };
  return (
    <div>
      <AccordionComponent
        title="Configuration"
        headerComponent={
          <button className={styles['secondary-btn']} onClick={handleSubmitSave}>
            Save to Dashboard
          </button>
        }
        expanded={expanded}
        onExpandedChange={handleExpandedChange}
      >
        <div className={styles['row__container']}>
          <div className="">
            <div className={cx(styles['content'])}>Select Metric Type</div>
            <div className={styles['select__container']}>
              <SelectComponent
                data={metricTypes}
                placeholder="Select metric type"
                onSelectionChange={handleMetricTypeChange}
                selected={selectedMetricType}
              />
            </div>
          </div>
        </div>

        <SuspenseLoader loader={<TableSkeleton />} loading={!!loading}>
          {metricOptions && (
            <>
              <div className={styles['row__container']}>
                <div>
                  <div className={styles['content']}>Aggregation</div>
                  <div className={styles['select__container']}>
                    <SelectComponent
                      data={aggregationFunctionOptions}
                      placeholder="Select aggregation function"
                      onSelectionChange={id => handleAggregationFunctionChange(id)}
                      selected={selectedAggregatedFunction}
                      searchable={true}
                    />
                  </div>
                </div>
                <div>
                  <div className={styles['content']}>Data</div>
                  <div className={styles['select__container']}>
                    <SelectComponent
                      data={metricOptions}
                      placeholder="Select data to aggregate"
                      onSelectionChange={handleSelectedAttributeChange}
                      selected={selectedAttribute}
                      searchable={true}
                    />
                  </div>
                </div>
              </div>
              <FilterComponent
                filter={queryBuilderPayload}
                options={metricOptions}
                onAdd={handleAdd}
                onUpdate={handleUpdate}
                onDelete={handleDelete}
                isGroupEnabled={false}
                containerClassName={styles['filter__container']}
                queryBuilderClassName={styles['query__builder']}
                headerName={'Filter'}
              />
              <div className={styles['row__container']}>
                <div>
                  <div className={styles['content']}>
                    <span>Group By</span>
                    <Tooltip title="You can view as Table Chart only for more than 1 Group By">
                      <IconButton className="p-0.5" style={{ size: 'small' }}>
                        <InfoIcon />
                      </IconButton>
                    </Tooltip>
                  </div>
                  <GroupComponent
                    options={metricOptions}
                    groupItems={groupItems}
                    onGroupItemAdd={handleGroupItem}
                    onGroupItemUpdate={handleGroupItem}
                    onGroupItemDelete={handleGroupItem}
                  />
                </div>
              </div>
              <div className={styles['row__container']}>
                <div>
                  <div className={styles['content']}>View as</div>
                  <div className={styles['select__container']}>
                    <SelectComponent
                      data={viewOptions}
                      placeholder="Select View format"
                      onSelectionChange={handleViewOptionChange}
                      selected={selectedViewOption}
                    />
                  </div>
                </div>
                {isTimeSeriesShown && (
                  <>
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center'
                      }}
                    >
                      <div className={styles['select__container']}>
                        <CheckboxComponent
                          label="Is Timeseries?"
                          checked={isTimeSeries}
                          onChange={handleTimeSeriesCheckboxChange}
                        />
                      </div>
                    </div>

                    {isTimeSeries && (
                      <div>
                        <div className={styles['content']}>Interval</div>
                        <div className={styles['select__container']}>
                          <SelectComponent
                            data={intervalOptions}
                            placeholder="Select aggregation interval"
                            onSelectionChange={id => handleResolutionChange(id)}
                            selected={selectedResolution}
                          />
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>

              <div className={styles['config_panel__action__container']}>
                <button className={styles['viz-button']} onClick={handleSubmitVisualize}>
                  Visualize
                </button>
              </div>
            </>
          )}
        </SuspenseLoader>
      </AccordionComponent>
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
    </div>
  );
};

export default PanelConfig;
