import ReactECharts from 'echarts-for-react';
import React, { useState, useEffect } from 'react';
import styles from '../index.module.css';

import { getLabelName } from '../utils';
import { extractLiteralValue } from '../../../utils/utils';

import dayjs from 'dayjs';

const BarChart = ({ metricData, panelData, showTitle }) => {
  const [chartOptions, setChartOptions] = useState({});

  useEffect(() => {
    let xaxisArray = [];
    let legend = [];
    let data = [];

    if (metricData[0].metadata.is_timeseries) {
      let timerange = metricData[0].metadata.time_range;
      let start_time = Number(timerange.time_geq);
      let end_time = Number(timerange.time_lt);

      let resolution = Number(metricData[0].metadata.resolution);

      let timestamps = [];

      while (start_time < end_time) {
        timestamps.push(start_time);
        xaxisArray.push(dayjs.unix(start_time).format('HH:mm'));
        start_time += resolution;
      }

      for (const item of metricData[0].labeled_data) {
        let seriesData = [];
        let timeseries_data = item.alias_data_map.metric_1.timeseries_data;

        for (const idx in xaxisArray) {
          let matching_td_data = timeseries_data.find(
            item => timestamps[idx] === Number(item.timestamp)
          );
          if (matching_td_data) {
            seriesData.push(extractLiteralValue(matching_td_data.value));
          } else {
            seriesData.push(null);
          }
        }

        let series = {
          type: 'bar',
          label: { show: true, position: 'top' },
          emphasis: { focus: 'series' },
          data: seriesData
        };

        if (item.labels || item.label_group) {
          let label_name = getLabelName(item);
          legend.push(label_name);
          series['name'] = label_name;
        }

        data.push(series);
      }
    } else {
      let metric_name = metricData[0].metadata.metric_alias_selector_map.metric_1.function;
      let seriesData = [];

      for (const item of metricData[0].labeled_data) {
        let metric_value = item.alias_data_map.metric_1.value;

        seriesData.push(extractLiteralValue(metric_value));

        if (item.labels || item.label_group) {
          let label_name = getLabelName(item);
          xaxisArray.push(label_name);
        } else {
          xaxisArray.push(metric_name);
        }
      }

      let series = {
        type: 'bar',
        label: { show: true, position: 'top' },
        emphasis: { focus: 'series' },
        data: seriesData
      };
      data.push(series);
    }

    let updatedChartOptions = {
      xAxis: {
        type: 'category',
        data: xaxisArray
      },
      tooltip: {
        trigger: 'axis'
      },
      yAxis: {
        type: 'value'
      },
      series: data,
      grid: {
        y: 200
      }
    };

    if (legend.length) {
      updatedChartOptions['legend'] = {
        data: legend,
        itemGap: 10,
        orient: 'horizontal'
      };
    }

    if (panelData.meta_info?.name && showTitle) {
      updatedChartOptions['title'] = {
        text: panelData.meta_info.name
      };
    }

    setChartOptions(updatedChartOptions);
  }, [metricData]);

  return (
    <div className={styles['tableChart']}>
      <ReactECharts option={chartOptions} notMerge={true} className={styles['reactChart']} />
    </div>
  );
};

export default BarChart;
