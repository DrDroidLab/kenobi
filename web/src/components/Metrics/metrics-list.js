import React, { useState, useEffect } from 'react';
// import Container from 'react-bootstrap/Container';
// import Row from 'react-bootstrap/Row';
// import Col from 'react-bootstrap/Col';
// import Button from 'react-bootstrap/Button';
import '../../css/create-metrics.css';
import { useNavigate } from 'react-router-dom';
import MetricsCard from './metrics-card';
import API from '../../API';

import dayjs from 'dayjs';

import Spinner from '../Spinner';
// import { DatePicker } from 'antd';
// const { RangePicker } = DatePicker;

const MetricsList = ({ workflow_id }) => {
  const [loading, setLoading] = useState(true);
  let navigate = useNavigate();
  const goTocreate = () => {
    navigate(`/${workflow_id}/create-metrics`);
  };
  const [metricsList, setMetricsList] = useState([]);
  const fetchMetricsList = API.useFetchMetricsList();

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

  const last30MinsStr = [getCurrentTime(30), getCurrentTime()];
  const last30Mins = [
    dayjs(last30MinsStr[0], 'YYYY-MM-DD HH:mm:ss'),
    dayjs(last30MinsStr[1], 'YYYY-MM-DD HH:mm:ss')
  ];
  const defaultDateTimeRange = [last30Mins[0].unix(), last30Mins[1].unix()];
  const [dateTimeRange, setDateTimeRange] = useState(defaultDateTimeRange);

  const [dateTimeRangeUpdate, setDateTimeRangeUpdate] = useState(defaultDateTimeRange);

  let handleDateTimeRangeChange = (d, ds) => {
    const dateTime = [dayjs(ds[0], 'YYYY-MM-DD HH:mm:ss'), dayjs(ds[1], 'YYYY-MM-DD HH:mm:ss')];
    const lastEpoch = [dateTime[0].unix(), dateTime[1].unix()];

    setDateTimeRangeUpdate(lastEpoch);
  };

  const applyFilter = () => {
    setDateTimeRange(dateTimeRangeUpdate);
  };

  useEffect(() => {
    fetchMetricsList({ workflow_id: workflow_id }, response => {
      setMetricsList(response.data.panels);
      setLoading(false);
    });
  }, [workflow_id]);

  return (
    <Container>
      <Row>
        <Col className="pageHead">
          <h1>
            Metrics
            <Button onClick={goTocreate}>Create Metrics</Button>
          </h1>
        </Col>
      </Row>
      <Row>
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
          <Button
            onClick={() => applyFilter(dateTimeRange)}
            style={{ marginBottom: '6px', marginLeft: '5px' }}
          >
            Apply
          </Button>
        </Col>
      </Row>
      {loading ? (
        <Spinner />
      ) : (
        <Row>
          {metricsList
            ? metricsList.map(val => (
                <MetricsCard key={val.id} data={val} dtRange={dateTimeRange}></MetricsCard>
              ))
            : 'No metrics'}
        </Row>
      )}
    </Container>
  );
};

export default MetricsList;
