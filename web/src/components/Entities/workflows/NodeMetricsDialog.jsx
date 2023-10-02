import React, { useEffect, useState } from 'react';

import API from '../../../API';

import SuspenseLoader from '../../../components/Skeleton/SuspenseLoader';
import TableSkeleton from '../../../components/Skeleton/TableLoader';

import LineChart from '../../Dashboard/Charts/LineChart';

import styles from './index.module.css';

function NodeMetricsDialog({ config, onClose }) {
  const getWorkflowNodeMetrics = API.useGetWorkflowNodeMetrics();

  const [nodeName, setNodeName] = useState();
  const [nodeMetrics, setNodeMetrics] = useState([]);
  const [compareTo, setCompareTo] = useState();

  const [metricsLoading, setMetricsLoading] = useState(false);

  useEffect(() => {
    setNodeName(JSON.parse(config).config.name);

    setMetricsLoading(true);
    getWorkflowNodeMetrics(
      { workflow_config: config },
      res => {
        let processed_node_metrics = [];
        for (const idx in res.data.metric_time_series) {
          if (!res.data.metric_time_series[idx].current_series) {
            continue;
          }

          const data = res.data.metric_time_series[idx].current_series;
          const p_data = res.data.metric_time_series[idx].past_series;

          let minTimestamp = parseInt(data[0].timestamp);
          let maxTimestamp = parseInt(data[0].timestamp);
          let resolution = parseInt(data[1].timestamp / 1000) - parseInt(data[0].timestamp / 1000);

          // Iterate through the data array
          for (const item of data) {
            const timestamp = parseInt(item.timestamp);

            // Update minTimestamp if the current timestamp is smaller
            if (timestamp < minTimestamp) {
              minTimestamp = timestamp;
            }

            // Update maxTimestamp if the current timestamp is larger
            if (timestamp > maxTimestamp) {
              maxTimestamp = timestamp;
            }
          }

          let node_metric = {};
          node_metric['metadata'] = {
            resolution: resolution,
            is_timeseries: 1,
            time_range: {
              time_geq: parseInt(minTimestamp / 1000),
              time_lt: parseInt(maxTimestamp / 1000)
            }
          };
          node_metric['labeled_data'] = [
            {
              label_group: res.data.metric_time_series[idx].metric_name,
              alias_data_map: {
                metric_1: {
                  timeseries_data: data.map((x, i) => {
                    return { timestamp: parseInt(x.timestamp / 1000), value: { double: x.value } };
                  })
                }
              }
            }
          ];

          if (p_data) {
            node_metric['labeled_data'][0]['alias_data_map']['metric_1']['past_timeseries_data'] =
              p_data.map((x, i) => {
                return { timestamp: parseInt(x.timestamp / 1000), value: { double: x.value } };
              });
          }

          processed_node_metrics.push({
            series: [node_metric],
            metric_name: res.data.metric_time_series[idx].metric_name,
            metric_source: res.data.metric_time_series[idx].metric_source
          });
        }

        setNodeMetrics(processed_node_metrics);
        setMetricsLoading(false);
      },
      err => {
        console.error(err);
      }
    );
  }, []);

  return (
    <div className={styles['modal-overlay']}>
      <div className={styles['modal']}>
        <button className={styles['close-button']} onClick={onClose}>
          X
        </button>
        <h1 className={styles['modal-title']}>{'Metrics -> ' + nodeName}</h1>
        <SuspenseLoader loading={!!metricsLoading} loader={<TableSkeleton noOfLines={10} />}>
          <div className={styles['modal-content']}>
            <div className={styles['grid-container']}>
              {nodeMetrics.map((metric, index) => {
                return (
                  <div className={styles['grid-item']} key={index}>
                    <LineChart
                      metricData={metric.series}
                      panelData={{
                        meta_info: { name: metric.metric_name + ' (' + metric.metric_source + ')' }
                      }}
                      showTitle={1}
                    />
                  </div>
                );
              })}
            </div>
          </div>
        </SuspenseLoader>
      </div>
    </div>
  );
}

export default NodeMetricsDialog;
