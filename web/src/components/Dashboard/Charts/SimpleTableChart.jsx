import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Box,
  Paper,
  TableContainer
} from '@mui/material';
import React, { useState, useEffect, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from '../index.module.css';

import API from '../../../API';

import ReactECharts from 'echarts-for-react';
import ValueComponent from '../../ValueComponent';

import { extractLiteralValue } from '../../../utils/utils';

import { extractValue, extractLabelName } from '../utils';

import dayjs from 'dayjs';
import useTimeRange from '../../../hooks/useTimeRange';
import CheckboxComponent from '../../CheckboxComponent';

const SimpleTableChart = ({ metricData, panelData, showTitle }) => {
  const { getTimeRange } = useTimeRange();
  const [finalData, setFinalData] = useState([]);
  const [viewData, setViewData] = useState([]);
  const [searchString, setSearchString] = useState('');
  const [groupingLabels, setGroupingLabels] = useState([]);
  const labelsMapping = panelData.data.chart.labels_mapping;
  const chartContext = panelData.data.chart.chart_metric_expression.context;
  const monitorId =
    panelData?.data?.chart?.chart_metric_expression?.metric_expressions?.[0]?.filter?.filters?.[0]
      ?.rhs?.literal?.id?.long;

  const fetchEventQuerySave = API.useEventQuerySave();
  const navigate = useNavigate();

  useEffect(() => {
    if (metricData[0].metadata.is_timeseries) {
      return;
    }

    let labels = metricData[0].metadata.labels_metadata
      ? metricData[0].metadata.labels_metadata.map(item => extractLabelName(item))
      : [];

    let metricName = metricData[0].metadata.metric_alias_selector_map.metric_1.function;
    setGroupingLabels([...labels, metricName]);

    let data = [];

    metricData[0].labeled_data.forEach(item => {
      let processedData = [];
      let labelList = item.labels
        ? item.labels.map(x =>
            x.display_value ? { value: x.display_value } : { value: extractValue(x.value) }
          )
        : [];
      let metricValue = extractValue(item.alias_data_map.metric_1.value);

      let filterQuery = [];
      for (const idx in labels) {
        filterQuery.push({
          op: 'EQ',
          lhs: {
            attribute_identifier: {
              name: labels[idx],
              path: 'event_attribute',
              type: 'STRING'
            }
          },
          rhs: {
            literal: {
              literal_type: 'STRING',
              string: labelList[idx].value
            }
          }
        });
      }

      processedData = [
        ...labelList,
        { value: metricValue, is_metric: true, filterQuery: filterQuery }
      ];
      data.push(processedData);
    });

    setFinalData(data);
    setViewData(data);
  }, [metricData]);

  const handleSearch = val => {
    setSearchString(val);
    let filteredData = finalData.filter(item => {
      return item.slice(0, -1).join(' ').toLowerCase().includes(val.toLowerCase());
    });
    setViewData(filteredData);
  };

  const handleMetricClick = filterQuery => {
    let metricFilterQuery = [
      panelData?.data?.chart?.chart_metric_expression?.metric_expressions?.[0]?.filter?.filters?.[0]
    ];
    if (Array.isArray(filterQuery) && filterQuery.length > 0)
      filterQuery.map(query => {
        metricFilterQuery.push(query);
      });
    let searchPayload = { query_request: { filter: { filters: metricFilterQuery, op: 'AND' } } };

    fetchEventQuerySave(
      searchPayload,
      res => {
        console.log(searchPayload);
        let savedQueryId = res.data?.query_context_id;
        // const pathParams = chartContext === 'EVENT' ? '/events' : `/monitors/${monitorId}`;
        let url = `/events?id=${savedQueryId}&startTime=${getTimeRange().time_geq}&endTime=${
          getTimeRange().time_lt
        }`;
        window.open(url, '_blank', 'noopener,noreferrer');
      },
      err => {
        console.log('Error while saving query', err);
      }
    );
  };

  return (
    <div className={styles['tableChart']}>
      {finalData ? (
        <div className={styles['searchBox']}>
          <ValueComponent
            valueType={'STRING'}
            onValueChange={handleSearch}
            value={searchString}
            placeHolder={'Search...'}
          />
          <span className={styles['dataCount']}>{`Found ${viewData?.length} results`}</span>
          {/* <CheckboxComponent label="Auto Refresh" onChange={handleAutoRefreshChange} /> */}
        </div>
      ) : (
        ''
      )}
      <TableContainer component={Paper} sx={{ height: '100vh' }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              {groupingLabels.map(item => (
                <TableCell className={styles['tableTitle']}>
                  {labelsMapping
                    ? labelsMapping.find(t => t.name === item)
                      ? labelsMapping.find(t => t.name === item).value
                      : item
                    : item}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {viewData?.map((item, index) => (
              <TableRow
                key={index}
                sx={{
                  '&:last-child td, &:last-child th': { border: 0 }
                }}
              >
                {item.map((value, idx) => (
                  <TableCell component="th" scope="row" className={styles['tableData']}>
                    {value.is_metric &&
                      (chartContext === 'EVENT' ? (
                        <span
                          style={{
                            fontWeight: 500,
                            textDecoration: 'underline',
                            color: '#9553fe',
                            cursor: 'pointer'
                          }}
                          onClick={() => handleMetricClick(value.filterQuery)}
                        >
                          {value.value}
                        </span>
                      ) : (
                        <span
                          style={{
                            fontWeight: 500
                          }}
                        >
                          {value.value}
                        </span>
                      ))}
                    {!value.is_metric && <span>{value.value}</span>}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};

export default SimpleTableChart;
