import React, { useEffect, useState } from 'react';
// import Container from 'react-bootstrap/Container';
// import Row from 'react-bootstrap/Row';
// import Col from 'react-bootstrap/Col';
// import Button from 'react-bootstrap/Button';
// import ReactECharts from 'echarts-for-react';
import '../../css/create-metrics.css';
import SaveMetricsName from './SaveMetricsName';
import { useParams } from 'react-router-dom';
import API from '../../API';

import dayjs from 'dayjs';

import Spinner from '../Spinner';

// import { DatePicker, Space } from 'antd';
// const { RangePicker } = DatePicker;

function CreateMetrics() {
  const { workFlowId } = useParams();

  const [modalShow, setModalShow] = React.useState(false);

  const [filterResponseData, setFilterResponseData] = useState({});
  const [isFilterResponseReceived, setIsFilterResponseReceived] = useState(false);
  const [isChartResponseReceived, setIsChartResponseReceived] = useState(false);
  const [stateList, setStateList] = useState([]);
  const [attributeList, setAttributeList] = useState([]);
  const [aggregationList, setAggregationList] = useState([]);
  const [selectedState, setSelectedState] = useState('');
  const [selectedAttribute, setSelectedAttribute] = useState('');
  const [selectedAggregation, setSelectedAggregation] = useState('');
  const [selectedResolution, setSelectedResolution] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('');
  const [selectedChartType, setSelectedChartType] = useState('');
  const [chartSeries, setChartSeries] = useState('');
  const [xaxisArray, setxaxisArray] = useState('');
  const [workFlowName, setworkFlowName] = useState('');
  const [filters, setFilters] = useState({});
  const [loading, setLoading] = useState(true);

  const dateFormat = 'YYYY-MM-DD';

  let getCurrentTime = offset => {
    const now = new Date();

    if (offset) {
      now.setMinutes(now.getMinutes() - 30);
    }

    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hour = String(now.getHours()).padStart(2, '0');
    const minute = String(now.getMinutes()).padStart(2, '0');
    const second = String(now.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
  };

  const options = {
    grid: { top: 20, right: 40, bottom: 20, left: 40 },
    xAxis: {
      type: 'category',
      data: xaxisArray
    },
    yAxis: {
      type: 'value'
    },
    // legend: {
    //   left: 'left'
    // },
    series: chartSeries,
    tooltip: {
      trigger: 'axis'
    }
  };

  const fetchMetricFilters = API.useFetchMetricsFilters();
  const fetchChartData = API.useFetchChartData();

  useEffect(() => {
    fetchMetricFilters(workFlowId, response => {
      setFilterResponseData(response.data.simple_metric_options);
      setIsFilterResponseReceived(true);
      setStateList(response.data.simple_metric_options.state_options);
      setAggregationList(response.data.simple_metric_options.global_aggregation_options);
      setworkFlowName(response.data.simple_metric_options.workflow_name);
    });
  }, []);

  let handleStateChange = e => {
    setSelectedState(e.target.value);
    setSelectedAttribute('');
    stateList.map(val => {
      if (val.state_id === e.target.value) {
        console.log('val found');
        setAttributeList(val.attribute_options);
        console.log(val);
      }
      return val;
    });
  };

  let handleDateTimeRangeChange = (d, ds) => {
    setDateTimeRange(ds);
  };

  let handleAttributeChange = e => {
    setSelectedAttribute(e.target.value);
  };

  let handleAggregationChange = e => {
    setSelectedAggregation(e.target.value);
  };

  let handleResolutionChange = e => {
    setSelectedResolution(e.target.value);
  };

  let handleGroupChange = e => {
    setSelectedGroup(e.target.value);
  };

  let handleChartTypeChange = e => {
    setSelectedChartType(e.target.value);
  };

  const last30MinsStr = [getCurrentTime(30), getCurrentTime()];
  const last30Mins = [
    dayjs(last30MinsStr[0], 'YYYY-MM-DD HH:mm:ss'),
    dayjs(last30MinsStr[1], 'YYYY-MM-DD HH:mm:ss')
  ];
  const [selectedDateTimeRange, setDateTimeRange] = useState(last30MinsStr);

  let applyFilter = () => {
    if (!selectedState) {
      alert('please select state');
      return;
    }
    if (!selectedDateTimeRange) {
      alert('please select a Date Time range');
      return;
    }

    let start_time = new Date(selectedDateTimeRange[0]).getTime() / 1000;
    let end_time = new Date(selectedDateTimeRange[1]).getTime() / 1000;

    let data = {
      metric_expressions: [
        {
          metric_type: 'SIMPLE_METRIC',
          simple_metric: {
            selector: {
              workflow_id: workFlowId,
              state_id: selectedState
            },
            tr: {
              time_geq: start_time,
              time_lt: end_time
            },
            group_by: [
              {
                attribute: selectedGroup ? selectedGroup : null
              }
            ],
            resolution: selectedResolution ? selectedResolution : null,
            function: selectedAggregation ? selectedAggregation : null,
            key: selectedAttribute ? selectedAttribute : null,
            is_timeseries: selectedChartType === 'pie' ? false : true
          }
        }
      ]
    };
    setFilters(data);
    setLoading(true);
    fetchChartData(data, response => {
      formatChartData(response.data.metric_data[0].simple_metric_data.data);
      setIsChartResponseReceived(true);
    });
  };

  let formatDate = eTime => {
    let md = new Date(parseInt(eTime) * 1000);

    let hours = md.getHours().toString().padStart(2, '0');
    let minutes = md.getMinutes().toString().padStart(2, '0');

    return hours + ':' + minutes;
  };

  let formatChartData = data => {
    let seriesData = [];
    let xaxisArray = [];
    if (data.length === 0) {
      setLoading(false);
      return;
    }

    for (let index = 0; index < data.length; index++) {
      let seriesObj = {};
      seriesObj.data = [];
      seriesObj.type = selectedChartType ? selectedChartType : 'line';
      if (selectedChartType === 'area') {
        seriesObj.type = 'line';
        seriesObj.stack = 'Total';
        seriesObj.emphasis = { focus: 'series' };
        seriesObj.areaStyle = {};
      }

      if (selectedChartType === 'bar') {
        seriesObj.stack = 'Total';
        seriesObj.emphasis = { focus: 'series' };
      }

      if (data[index]?.labels?.length > 0) {
        seriesObj.name =
          data[index].labels[0].attribute.key + '-' + data[index].labels[0].attribute.value;
      } else {
        seriesObj.name = selectedAttribute;
      }
      let ts_data_points = data[index].timeseries_data.ts_data_points;

      let start_time = new Date(selectedDateTimeRange[0]).getTime() / 1000;
      let end_time = new Date(selectedDateTimeRange[1]).getTime() / 1000;

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
            start_time = start_time + parseInt(selectedResolution);
            break;
          }
          start_time = start_time + parseInt(selectedResolution);
        }
      }

      seriesData.push(seriesObj);
    }
    setChartSeries(seriesData);
    setxaxisArray(xaxisArray);
    setLoading(false);
  };

  let savePanel = () => {
    setModalShow(true);
  };

  return (
    <Container>
      <Row>
        <Col className="pageHead">
          <h1>
            Create Metrics for - <small>{workFlowName}</small>
          </h1>
        </Col>
        <Col></Col>
        <Col>
          <RangePicker
            defaultValue={last30Mins}
            showTime
            format="YYYY-MM-DD HH:mm:ss"
            size="large"
            separator
            placeholder={['Start', 'End']}
            suffixIcon
            style={{
              height: 'auto',
              width: 'auto',
              borderRadius: '5px',
              borderWidth: '2px',
              borderColor: 'black',
              color: 'black',
              cursor: 'pointer',
              fontSize: '17px',
              margin: '5px',
              padding: '5px',
              fontWeight: '700'
            }}
            onChange={handleDateTimeRangeChange}
          />
        </Col>
      </Row>
      <Row>
        <Col lg="4" className="metrics-filter-wrap">
          <Row className="metrics-filter-row">
            <Col lg="12" className="filter-heading">
              Select State and Attribute // {selectedAttribute}
            </Col>
            <Col className="inputWrap">
              <label>State</label>
              <select value={selectedState} onChange={handleStateChange}>
                <option defaultValue="choose"> Select State</option>
                {stateList.map(val => (
                  <option value={val.state_id} key={val.state_id}>
                    {val.state_name}
                  </option>
                ))}
              </select>
            </Col>
            <Col className="inputWrap">
              <label>Attribute</label>
              <select value={selectedAttribute} onChange={handleAttributeChange}>
                <option>Select Attribute</option>
                {attributeList.map(val => (
                  <option value={val.attribute} key={val.attribute}>
                    {val.attribute}
                  </option>
                ))}
              </select>
            </Col>
          </Row>
          <Row className="metrics-filter-row">
            <Col lg="12" className="filter-heading">
              Select Aggregation function and resolution{' '}
            </Col>
            <Col className="inputWrap">
              <label>Aggregation</label>
              <select value={selectedAggregation} onChange={handleAggregationChange}>
                <option>Select Aggregation</option>
                {aggregationList?.map(val => (
                  <option value={val} key={val}>
                    {val}
                  </option>
                ))}
              </select>
            </Col>
            <Col className="inputWrap">
              <label>Resolution</label>
              <select value={selectedResolution} onChange={handleResolutionChange}>
                <option>Select Resolution</option>
                <option value="60">1 min</option>
                <option value="300">5 min</option>
                <option value="600">10 min</option>
                <option value="1800">30 min</option>
                <option value="3600">1 hr</option>
                <option value="14400">6 hr</option>
                <option value="86400">1 day</option>
              </select>
            </Col>
          </Row>
          <Row className="metrics-filter-row">
            <Col lg="12" className="filter-heading">
              Others
            </Col>
            <Col className="inputWrap">
              <label>Group by</label>
              <select value={selectedGroup} onChange={handleGroupChange}>
                <option>Select Group by Attribute</option>
                {attributeList.map(val => (
                  <option value={val.attribute} key={val.attribute}>
                    {val.attribute}{' '}
                  </option>
                ))}
              </select>
            </Col>
            <Col className="inputWrap">
              <label>Chart type</label>
              <select value={selectedChartType} onChange={handleChartTypeChange}>
                <option>Select Chart Type</option>
                <option value="line">Line Chart</option>
                <option value="area">Area Chart</option>
                <option value="bar">Bar Chart</option>
              </select>
            </Col>
          </Row>
          <Row className="metrics-filter-row">
            <Col className="inputWrap">
              <Button variant="primary" onClick={applyFilter}>
                Apply
              </Button>
            </Col>
          </Row>
        </Col>
        <Col>
          <Row>
            <Col className="graph-wrap">
              {isChartResponseReceived ? (
                loading ? (
                  <Spinner />
                ) : (
                  // <ReactECharts option={options} style={{ height: '400px' }} />
                  <></>
                )
              ) : (
                <div className="applyFilterMessage">Apply filters to view chart.</div>
              )}
            </Col>
          </Row>
          <Row>
            <Col className="save-button-wrap">
              {isChartResponseReceived ? (
                <Button variant="primary" onClick={savePanel}>
                  Save Panel
                </Button>
              ) : (
                ''
              )}
            </Col>
          </Row>
        </Col>
      </Row>
      <SaveMetricsName
        filterdata={filters}
        workflow_id={workFlowId}
        selectedChartType={selectedChartType}
        show={modalShow}
        onHide={() => setModalShow(false)}
      />
    </Container>
  );
}

export default CreateMetrics;
