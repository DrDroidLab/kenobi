import { Link, useNavigate, useParams } from 'react-router-dom';
import API from '../../API';
import { useCallback, useEffect, useState } from 'react';
import PanelPlot from '../Dashboard/PanelPlot';
import useTimeRange from '../../hooks/useTimeRange';

import SelectComponent from '../SelectComponent';
import cross from '../../data/cross.svg';

import styles from './index.module.css';

const EventTypeMetrics = ({ eventTypeDefinition, refreshMetrics }) => {
  const eventTypeId = eventTypeDefinition.event_type.id;
  const resolutionMap = {
    600: 60,
    1800: 180,
    3600: 300,
    10800: 900,
    43200: 3600,
    86400: 7200
  };

  const { timerange, getTimeRange } = useTimeRange();

  const [eventAttributeMetricPanelConfigs, setEventAttributeMetricPanelConfigs] = useState([]);

  const [groupByAttributes, setGroupByAttributes] = useState(
    eventTypeDefinition.event_type.keys.map(item => ({ id: item.key, label: item.key }))
  );
  const [selectedGroupByAttribute, setSelectedGroupByAttribute] = useState();

  const [refreshEventTypeMetrics, setRefreshEventTypeMetrics] = useState(true);

  const onRemove = id => {
    setSelectedGroupByAttribute(null);
  };

  const handleGroupByAttributeChange = id => {
    setSelectedGroupByAttribute(id);
  };

  const refreshMetricData = () => {
    const { time_geq, time_lt } = getTimeRange();
    let resolution = resolutionMap[time_lt - time_geq];

    if (!resolution) {
      resolution = Math.ceil((time_lt - time_geq) / 15 / 60) * 60;
    }

    let countEventMetricPanelConfig = {
      context: 'EVENT',
      metric_expressions: [
        {
          filter: {
            op: 'AND',
            filters: [
              {
                lhs: {
                  column_identifier: {
                    name: 'event_type_id'
                  }
                },
                op: 'EQ',
                rhs: {
                  literal: {
                    literal_type: 'ID',
                    id: {
                      type: 'LONG',
                      long: eventTypeId
                    }
                  }
                }
              }
            ]
          },
          selectors: [
            {
              function: 'COUNT',
              expression: {
                column_identifier: {
                  name: 'event_type_id'
                }
              }
            }
          ],
          resolution: resolution,
          is_timeseries: true
        }
      ]
    };

    if (selectedGroupByAttribute) {
      countEventMetricPanelConfig['metric_expressions'][0]['group_by'] = [
        {
          attribute_identifier: {
            name: selectedGroupByAttribute,
            path: 'event_attribute'
          }
        }
      ];
    }

    let configs = [];
    configs.push({
      meta_info: { name: 'Event Count' },
      data: { chart: { type: 'bar', chart_metric_expression: countEventMetricPanelConfig } }
    });

    const eventLongKeys = eventTypeDefinition.event_type.keys.filter(
      item => item.key_type === 'LONG'
    );

    for (let i = 0; i < eventLongKeys?.length; i++) {
      let title = 'Average -> ' + eventLongKeys[i].key;
      let chart_type = 'line';
      let config = {
        context: 'EVENT',
        metric_expressions: [
          {
            filter: {
              op: 'AND',
              filters: [
                {
                  lhs: {
                    column_identifier: {
                      name: 'event_type_id'
                    }
                  },
                  op: 'EQ',
                  rhs: {
                    literal: {
                      literal_type: 'ID',
                      id: {
                        type: 'LONG',
                        long: eventTypeId
                      }
                    }
                  }
                }
              ]
            },
            selectors: [
              {
                function: 'AVG',
                expression: {
                  attribute_identifier: {
                    name: eventLongKeys[i].key,
                    path: 'event_attribute'
                  }
                }
              }
            ],
            resolution: resolution,
            is_timeseries: true
          }
        ]
      };

      if (selectedGroupByAttribute) {
        config['metric_expressions'][0]['group_by'] = [
          {
            attribute_identifier: {
              name: selectedGroupByAttribute,
              path: 'event_attribute'
            }
          }
        ];
      }

      configs.push({
        meta_info: { name: title },
        data: { chart: { type: chart_type, chart_metric_expression: config } }
      });
    }

    setEventAttributeMetricPanelConfigs(configs);
  };

  useEffect(() => {
    refreshMetricData();
    setRefreshEventTypeMetrics(!refreshEventTypeMetrics);
  }, [selectedGroupByAttribute]);

  useEffect(() => {
    refreshMetricData();
    setRefreshEventTypeMetrics(!refreshEventTypeMetrics);
  }, [refreshMetrics]);

  return (
    <div>
      <div className={styles['container']}>
        <div className={styles['heading']}>
          <div className={styles['eventList']}>
            <SelectComponent
              data={groupByAttributes}
              placeholder="Select grouping attribute"
              onSelectionChange={handleGroupByAttributeChange}
              selected={selectedGroupByAttribute}
            />
            {selectedGroupByAttribute && (
              <img
                className={styles['crossIcon']}
                src={cross}
                alt="cancel"
                width="18px"
                height="18px"
                onClick={onRemove}
              />
            )}
          </div>
        </div>

        {eventAttributeMetricPanelConfigs.map(item => (
          <PanelPlot panelData={item} refresh={refreshEventTypeMetrics} showTitle={true} />
        ))}
      </div>
    </div>
  );
};

export default EventTypeMetrics;
