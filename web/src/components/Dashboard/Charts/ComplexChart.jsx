import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Box,
  TableContainer,
  Paper
} from '@mui/material';
import React, { useState, useEffect } from 'react';
import styles from '../index.module.css';

import { Link, useNavigate } from 'react-router-dom';

import API from '../../../API';

import ValueComponent from '../../ValueComponent';

import useTimeRange from '../../../hooks/useTimeRange';

function formatEpochTimestampToLocalTimeString(epochTimestamp) {
  const timestampMilliseconds = parseInt(epochTimestamp) * 1000;

  const date = new Date(timestampMilliseconds);

  const options = {
    month: 'short', // Short month name (e.g., Sep)
    day: 'numeric',
    hour: '2-digit', // Two-digit hours (e.g., 09)
    minute: '2-digit', // Two-digit minutes (e.g., 30)
    hour12: false // Use 12-hour format with "am" and "pm"
  };

  const localTimeString = date.toLocaleString(undefined, options);

  return localTimeString;
}

const ComplexTableChart = ({ metricData, showTitle }) => {
  const { getTimeRange } = useTimeRange();
  const [searchString, setSearchString] = useState('');

  const [finalData, setFinalData] = useState([]);
  const [viewData, setViewData] = useState(finalData);

  const [sortedLabels, setSortedLabels] = useState([]);

  const fetchEventQuerySave = API.useEventQuerySave();

  const navigate = useNavigate();

  useEffect(() => {
    if (metricData) {
      let firstRow = metricData.rows[0];
      setSortedLabels(firstRow.columns.map(x => x.label));

      setViewData(metricData.rows);
      setFinalData(metricData.rows);
    }
  }, [metricData]);

  const handleSearch = val => {
    setSearchString(val);
    let filteredData = finalData.filter(item => {
      let labels = item.columns.map(label => {
        return label.element.element_value;
      });
      return labels.join(' ').toLowerCase().includes(val.toLowerCase());
    });
    setViewData(filteredData);
  };

  const handleMetricClick = filter_query => {
    let searchPayload = {
      query_request: { filter: { filters: JSON.parse(filter_query), op: 'AND' } }
    };

    fetchEventQuerySave(
      searchPayload,
      res => {
        let savedQueryId = res.data?.query_context_id;
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
        </div>
      ) : (
        ''
      )}
      <TableContainer component={Paper} sx={{ height: '100vh' }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              {sortedLabels.map(item => (
                <TableCell className={styles['tableTitle']}>{item}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {viewData?.map((item, index) => (
              <TableRow
                key={index}
                style={{
                  '&:last-child td, &:last-child th': { border: 0 }
                }}
              >
                {item.columns.map(x =>
                  x.element.element_value ? (
                    <TableCell component="th" scope="row" className={styles['tableData']}>
                      <p
                        style={{
                          backgroundColor: x.element.fill_color,
                          padding: '4px',
                          borderRadius: '5px',
                          fontSize: '13px'
                        }}
                      >
                        {x.element.element_type == 'timestamp'
                          ? formatEpochTimestampToLocalTimeString(x.element.element_value)
                          : x.element.element_value}
                      </p>
                    </TableCell>
                  ) : (
                    <TableCell
                      component="th"
                      scope="row"
                      align="center"
                      className={styles['tableData']}
                    >
                      <Table stickyHeader>
                        <TableBody>
                          {x.element.computed_metrics ? (
                            x.element.computed_metrics.map((i, idx) => (
                              <TableRow
                                key={idx}
                                sx={{
                                  '&:last-child td, &:last-child th': { border: 0 }
                                }}
                              >
                                <TableCell
                                  component="th"
                                  scope="row"
                                  className={styles['tableData']}
                                >
                                  <span
                                    style={{
                                      fontWeight: 500,
                                      textDecoration: 'underline',
                                      color: '#9553fe',
                                      cursor: 'pointer'
                                    }}
                                    onClick={() => handleMetricClick(i.filter_query)}
                                  >
                                    {i.metric_label}
                                  </span>
                                </TableCell>
                                <TableCell
                                  component="th"
                                  scope="row"
                                  className={styles['tableData']}
                                >
                                  {i.metric_value}
                                </TableCell>
                              </TableRow>
                            ))
                          ) : (
                            <p></p>
                          )}
                        </TableBody>
                      </Table>
                    </TableCell>
                  )
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};

export default ComplexTableChart;
