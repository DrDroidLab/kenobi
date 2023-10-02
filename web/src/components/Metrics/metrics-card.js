import React, { useEffect, useState } from 'react';
// import Col from 'react-bootstrap/Col';
// import Button from 'react-bootstrap/Button';
// import ReactECharts from 'echarts-for-react';
import '../../css/create-metrics.css';
import API from '../../API';
import CachedIcon from '@mui/icons-material/Cached';

import Spinner from '../Spinner';

const getTimeRange = dtRange => {
  let start_time = new Date(dtRange[0]).getTime();
  let end_time = new Date(dtRange[1]).getTime();

  return { time_geq: start_time, time_lt: end_time };
};

function MetricsCard(props) {
  // console.log(props.data.config.metric_expressions[0].simple_metric.key)
  const [chartSeries, setChartSeries] = useState('');
  const [xaxisArray, setxaxisArray] = useState('');
  const [loading, setLoading] = useState(true);
  const [tr, setTr] = useState(getTimeRange(props.dtRange));
  const fetchChartData = API.useFetchChartData();

  let testName = props.data.config.metric_expressions[0].simple_metric.key;
  let chartType = props.data.config.chart_type;

  const options = {
    grid: { top: 20, right: 40, bottom: 20, left: 40 },
    xAxis: {
      type: 'category',
      data: xaxisArray
    },
    yAxis: {
      type: 'value'
    },
    series: chartSeries,
    tooltip: {
      trigger: 'axis'
    }
  };

  let formatDate = eTime => {
    let md = new Date(parseInt(eTime) * 1000);

    let hours = md.getHours().toString().padStart(2, '0');
    let minutes = md.getMinutes().toString().padStart(2, '0');

    return hours + ':' + minutes;
  };

  let formatChartData = (data, metricName, resolution) => {
    let start_time = new Date(props.dtRange[0]).getTime();
    let end_time = new Date(props.dtRange[1]).getTime();

    let seriesData = [];
    let xaxisArray = [];
    if (data.length === 0) {
      return;
    }
    for (let index = 0; index < data.length; index++) {
      let seriesObj = {};
      seriesObj.data = [];
      seriesObj.type = chartType ? chartType : 'line';
      if (data[index]?.labels?.length > 0) {
        seriesObj.name =
          data[index].labels[0].attribute.key + '-' + data[index].labels[0].attribute.value;
      } else {
        seriesObj.name = metricName;
      }
      let ts_data_points = data[index].timeseries_data.ts_data_points;

      let j = 0;

      while (start_time < end_time) {
        while (j < ts_data_points.length) {
          let timestamp = parseInt(ts_data_points[j].timestamp);
          xaxisArray.push(formatDate(start_time));
          if (timestamp === start_time) {
            seriesObj.data.push(ts_data_points[j].value);
            j++;
          } else {
            seriesObj.data.push(null);
            start_time = start_time + parseInt(resolution);
            break;
          }
          start_time = start_time + parseInt(resolution);
        }

        for (let index = 0; index < data.length; index++) {
          let seriesObj = {};
          seriesObj.data = [];
          seriesObj.type = chartType ? chartType : 'line';
          if (chartType === 'area') {
            seriesObj.type = 'line';
            seriesObj.stack = 'Total';
            seriesObj.emphasis = { focus: 'series' };
            seriesObj.areaStyle = {};
          }

          if (chartType === 'bar') {
            seriesObj.stack = 'Total';
            seriesObj.emphasis = { focus: 'series' };
          }

          if (data[index]?.labels?.length > 0) {
            seriesObj.name =
              data[index].labels[0].attribute.key + '-' + data[index].labels[0].attribute.value;
          } else {
            seriesObj.name = metricName;
          }
          let ts_data_points = data[index].timeseries_data.ts_data_points;

          let start_time = new Date(props.dtRange[0]).getTime() / 1000;
          let end_time = new Date(props.dtRange[1]).getTime() / 1000;

          let j = 0;

          while (start_time < end_time) {
            while (j < ts_data_points.length) {
              let timestamp = parseInt(ts_data_points[j].timestamp);
              let formattedStartTime = formatDate(start_time);
              if (xaxisArray.indexOf(formattedStartTime) === -1) {
                xaxisArray.push(formattedStartTime);
              }

              if (timestamp === start_time) {
                seriesObj.data.push(ts_data_points[j].value);
                j++;
              } else {
                seriesObj.data.push(null);
                start_time = start_time + parseInt(resolution);
                break;
              }
              start_time = start_time + parseInt(resolution);
            }
          }

          seriesData.push(seriesObj);
        }
        setChartSeries(seriesData);
        setxaxisArray(xaxisArray);
        setLoading(false);
      }

      seriesData.push(seriesObj);
    }
    setChartSeries(seriesData);
    setxaxisArray(xaxisArray);
  };

  let getChartData = () => {
    let data = props.data.config;
    let resolution = parseInt(data.metric_expressions[0].simple_metric.resolution);

    if (data.metric_expressions) {
      data.metric_expressions.forEach((expr, idx) => {
        expr.simple_metric.tr = tr;
      });
    }

    fetchChartData(data, response => {
      formatChartData(response.data.metric_data[0].simple_metric_data.data, testName, resolution);
      setLoading(false);
    });
  };

  useEffect(() => {
    if (loading) {
      getChartData();
    }
  }, [loading]);

  useEffect(() => {
    if (!loading) {
      setTr(getTimeRange(props.dtRange));
      setLoading(true);
    }
  }, [props.dtRange]);

  return (
    <>
      <Col className="graph-wrap-list" lg={6}>
        <div>
          <div className="card-head">
            <div>
              <h4>{props.data.name}</h4>
            </div>
            <div>
              <Button
                variant="light"
                onClick={() => setLoading(true)}
                style={{
                  marginRight: '10px'
                }}
              >
                <CachedIcon
                  style={{
                    fontSize: '16px'
                  }}
                />
              </Button>
            </div>
          </div>
          {loading ? <Spinner /> : <></>}
        </div>
      </Col>
    </>
  );
}

export default MetricsCard;
