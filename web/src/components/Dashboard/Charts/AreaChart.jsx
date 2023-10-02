import ReactECharts from 'echarts-for-react';
import React, { useState, useEffect } from 'react';
import styles from '../index.module.css';

import { getLabelName } from '../utils';

import { extractLiteralValue } from '../../../utils/utils';

import dayjs from 'dayjs';

const AreaChart = ({ metricData, panelData, showTitle }) => {
  const [chartOptions, setChartOptions] = useState({});

  useEffect(() => {
    let timerange = metricData[0].metadata.time_range;
    let start_time = Number(timerange.time_geq);
    let end_time = Number(timerange.time_lt);

    let resolution = Number(metricData[0].metadata.resolution);

    if (!metricData[0].metadata.is_timeseries) {
      return;
    }

    let xaxisArray = [];
    let timestamps = [];

    while (start_time < end_time) {
      timestamps.push(start_time);
      xaxisArray.push(dayjs.unix(start_time).format('HH:mm'));
      start_time += resolution;
    }

    let data = [];
    let legend = [];

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

      let series = { type: 'line', data: seriesData, areaStyle: {}, stack: 'Total' };

      if (item.labels || item.label_group) {
        let label_name = getLabelName(item);
        legend.push(label_name);
        series['name'] = label_name;
      }

      series['emphasis'] = {
        focus: 'series'
      };

      data.push(series);
    }

    let updatedChartOptions = {
      xAxis: {
        type: 'category',
        data: xaxisArray,
        boundaryGap: false
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
      updatedChartOptions['legend'] = { data: legend };
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
      <ReactECharts className={styles['reactChart']} option={chartOptions} notMerge={true} />
    </div>
  );
};

export default AreaChart;
