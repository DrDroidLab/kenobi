import { useCallback, useEffect, useState } from 'react';
import API from '../../API';
import { useNavigate } from 'react-router-dom';
import styles from './index.module.css';
import SimpleTableChart from './Charts/SimpleTableChart';
import LineChart from './Charts/LineChart';
import AreaChart from './Charts/AreaChart';
import BarChart from './Charts/BarChart';

import dayjs from 'dayjs';

import SuspenseLoader from '../../components/Skeleton/SuspenseLoader';
import TableSkeleton from '../../components/Skeleton/TableLoader';

import { CircularProgress } from '@mui/material';
import Backdrop from '@mui/material/Backdrop';
import CheckboxComponent from '../CheckboxComponent';
import useToggle from '../../hooks/useToggle';
import Toast from '../Toast';

const createTimeRangeContext = timeRange => {
  let timeRangeContext = '';
  let format = 'hh:mm a';
  if (timeRange) {
    if (timeRange.time_lt - timeRange.time_geq >= 43200) {
      format = 'DD MMM, hh:mm a';
    }
    timeRangeContext = `Showing results from ${dayjs
      .unix(timeRange.time_geq)
      .format(format)} to ${dayjs.unix(timeRange.time_lt).format(format)}`;
  }
  return timeRangeContext;
};

const PanelPlot = ({ panelData, refresh, showTitle, startTime }) => {
  const [panelLoading, setPanelLoading] = useState(false);
  const [metricsLoading, setMetricsLoading] = useState(false);
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState('');
  const [timeRangeContext, setTimeRangeContext] = useState('');

  const [asyncMetricResponses, setAsyncMetricResponses] = useState([]);
  const [complexTablePanelMetricsData, setComplexTablePanelMetricsData] = useState();
  const [metricsLength, setMetricsLength] = useState();

  const [metricResponse, setMetricResponse] = useState([]);
  const getMetrics = API.useGetMetrics();

  const [autoRefresh, setAutoRefresh] = useState(false);

  const handleMetricsData = () => {
    if (asyncMetricResponses) {
      const metrics_data = asyncMetricResponses;

      setMetricResponse(metrics_data.map(m => m.md[0]));
      setTimeRangeContext(createTimeRangeContext(metrics_data[0].tc));

      setPanelLoading(false);
      setMetricsLoading(false);
    }
  };

  const fetchMetrics = async (context, metric_expression, startTime) => {
    return new Promise((resolve, reject) => {
      const requestData = {
        context: context,
        metric_expressions: [metric_expression]
      };
      if (startTime) {
        requestData.timeRange = {
          time_geq: startTime,
          time_lt: Math.floor(Date.now() / 1000)
        };
      }
      getMetrics(
        requestData,
        res => {
          resolve({ md: res.data?.metric_data, tc: res.data?.metric_data[0].metadata.time_range });
        },
        err => {
          console.error(err);
          setMetricResponse([]);
          reject(err);
        }
      );
    });
  };

  useEffect(() => {
    if (asyncMetricResponses.filter(item => item).length === metricsLength) {
      handleMetricsData();
    }
  }, [asyncMetricResponses]);

  useEffect(() => {
    let chart_type = panelData?.data?.chart?.type;
    let panelConfig = panelData?.data?.chart?.chart_metric_expression;
    if (panelConfig) {
      setMetricsLoading(true);
      let metric_expressions = panelConfig.metric_expressions;
      setMetricsLength(metric_expressions.length);

      const fetchMetricsData = async () => {
        try {
          const responses = await Promise.all(
            metric_expressions.map(me => fetchMetrics(panelConfig.context, me, startTime))
          );

          const data = await Promise.all(responses);
          setAsyncMetricResponses(data);
        } catch (error) {
          setMetricsLoading(false);
          setPanelLoading(false);
          toggleError(true);
          setSubmitError(error.err);
          setAsyncMetricResponses([]);
          console.error('Error:', error);
        }
      };
      fetchMetricsData();
    }
  }, [refresh]);

  useEffect(() => {
    let intervalId;
    if (autoRefresh) {
      intervalId = setInterval(() => {
        let chart_type = panelData?.data?.chart?.type;
        let panelConfig = panelData?.data?.chart?.chart_metric_expression;
        if (panelConfig) {
          let metric_expressions = panelConfig.metric_expressions;
          setMetricsLength(metric_expressions.length);

          const fetchMetricsData = async () => {
            try {
              const responses = await Promise.all(
                metric_expressions.map(me => fetchMetrics(panelConfig.context, me))
              );

              const data = await Promise.all(responses);
              setAsyncMetricResponses(data);
            } catch (error) {
              setAsyncMetricResponses([]);
              console.error('Error:', error);
            }
          };
          fetchMetricsData();
        }
      }, 120000);
      return () => clearInterval(intervalId);
    }
  }, [autoRefresh]);

  const getRender = item => {
    let chart_type = panelData.data.chart.type ? panelData.data.chart.type : 'line';

    if (chart_type?.toLowerCase() == 'simple_table') {
      return <SimpleTableChart metricData={item} panelData={panelData} showTitle={showTitle} />;
    } else if (chart_type?.toLowerCase() == 'line') {
      return <LineChart metricData={item} panelData={panelData} showTitle={showTitle} />;
    } else if (chart_type?.toLowerCase() == 'area') {
      return <AreaChart metricData={item} panelData={panelData} showTitle={showTitle} />;
    } else if (chart_type?.toLowerCase() == 'bar') {
      return <BarChart metricData={item} panelData={panelData} showTitle={showTitle} />;
    } else {
      return <LineChart metricData={item} panelData={panelData} showTitle={showTitle} />;
    }
  };

  const handleAutoRefreshChange = e => {
    setAutoRefresh(e.target.checked);
  };

  return (
    <>
      <div>
        {/* <SuspenseLoader loading={!!panelLoading} loader={<TableSkeleton />}> */}
        <>
          <SuspenseLoader loading={!!metricsLoading} loader={<TableSkeleton />}>
            {metricResponse.length > 0 && metricResponse[0]?.labeled_data?.length > 0 ? (
              <>
                <div className={styles['panel__heading']}>
                  <div className={styles['timeRangeContext']}>{timeRangeContext}</div>
                  <CheckboxComponent
                    label="Auto Refresh (2 minutes)"
                    onChange={handleAutoRefreshChange}
                    value={autoRefresh}
                    name={autoRefresh}
                  />
                </div>
                <div>{getRender(metricResponse)}</div>
              </>
            ) : (
              <div>
                <span className={styles['content']}>No Chart Available</span>
              </div>
            )}
            {complexTablePanelMetricsData && (
              <>
                <div className={styles['panel__heading']}>
                  <div className={styles['timeRangeContext']}>{timeRangeContext}</div>
                  <CheckboxComponent
                    label="Auto Refresh (2 minutes)"
                    onChange={handleAutoRefreshChange}
                    value={autoRefresh}
                    name={autoRefresh}
                  />
                </div>
                <div>{getRender(metricResponse)}</div>
              </>
            )}
          </SuspenseLoader>
          <Toast
            open={!!IsError}
            severity="error"
            message={submitError}
            handleClose={() => toggleError(false)}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
          />
        </>
        {/* </SuspenseLoader> */}
      </div>
    </>
  );
};

export default PanelPlot;
