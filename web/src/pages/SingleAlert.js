import { Link, useNavigate, useParams } from 'react-router-dom';
import Heading from '../components/Heading';
import API from '../API';
import { useCallback, useEffect, useState } from 'react';
import EventTypeDefinition from '../components/EventType/EventTypeDefinition';
import { TabContext, TabPanel } from '@mui/lab';
import { Tab, Button, Paper, Chip } from '@mui/material';
import EventCard from '../components/Events/EventCard';

import { CircularProgress } from '@mui/material';
import moment from 'moment';

import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import Table from '@mui/material/Table';
import Divider from '@mui/material/Divider';
import TableRow from '@mui/material/TableRow';
import TableHead from '@mui/material/TableHead';
import TableBody from '@mui/material/TableBody';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import CardContent from '@mui/material/CardContent';
import { styled, useTheme } from '@mui/material/styles';
import TableContainer from '@mui/material/TableContainer';
import TableCell from '@mui/material/TableCell';

const CalcWrapper = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  '&:not(:last-of-type)': {
    marginBottom: theme.spacing(3)
  }
}));

const SingleAlert = () => {
  let { id } = useParams();
  let navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [isAlertDataFetched, setIsAlertDataFetched] = useState(false);
  const [isAlertReasonFetched, setIsAlertReasonFetched] = useState(false);
  const [alertReason, setAlertReason] = useState('');
  const [monitorName, setMonitorName] = useState('');
  const [monitorId, setMonitorId] = useState(0);

  const [primaryEventData, setPrimaryEventData] = useState({});
  const [isPrimaryEventData, setIsPrimaryEventData] = useState(false);

  const [headerColor, setHeaderColor] = useState('red');

  const [alertData, setAlertData] = useState({});
  const fetchAlertData = API.useGetAlertData();
  const fetMonitorTransactionEvents = API.useGetMonitorsTransactionsEvents();

  function extractValue(v) {
    if (v.int_value) {
      return v.int_value;
    } else if (v.string_value) {
      return v.string_value;
    } else if (v.double_value) {
      return v.double_value;
    } else {
      return v;
    }
  }

  function extractEvent(s_event) {
    let obj = {};
    obj.name = s_event.event_type.name;
    obj.timestamp = s_event.timestamp;
    obj.payload = {};
    for (var i = 0; i < s_event.kvs.length; i++) {
      let keyname = s_event.kvs[i].key;
      obj.payload[keyname] = extractValue(s_event.kvs[i].value);
    }
    return obj;
  }

  function findPrimaryEvent(e_id, events) {
    for (let i = 0; i < events.length; i++) {
      if (events[i].event_type.id === e_id) {
        return events[i];
      }
    }
    return {};
  }

  function findEventKeyValue(e_id, key, events) {
    for (let i = 0; i < events.length; i++) {
      if (events[i].event_type.id === e_id) {
        for (let j = 0; j < events[i].kvs.length; j++) {
          if (events[i].kvs[j].key === key) {
            return extractValue(events[i].kvs[j].value);
          }
        }
      }
    }
    return '';
  }

  useEffect(() => {
    if (loading) {
      fetchAlertData(id, response => {
        if (response.data?.alerts?.length > 0) {
          setAlertData(response.data?.alerts[0]);
          setIsAlertDataFetched(true);
          if (response.data?.alerts[0].trigger?.definition.type === 'MISSING_EVENT') {
            setMonitorId(response.data?.alerts[0].triggered_by.monitor.id);
            setMonitorName(response.data?.alerts[0].triggered_by.monitor.name);
            let monitorTransactionId = response.data?.alerts[0].triggered_by.id;
            let monitorThreshold =
              response.data?.alerts[0].trigger?.definition.missing_event_trigger
                .transaction_time_threshold;
            let monitor = response.data?.alerts[0].trigger?.monitor;
            let primaryEventTypeId = monitor.primary_event_key.event_type.id;
            let primaryEventKey = monitor.primary_event_key.key;
            let secondaryEventTypeId = monitor.secondary_event_key.event_type.id;
            let primaryEventName = monitor.primary_event_key.event_type.name;
            let secondaryEventName = monitor.secondary_event_key.event_type.name;
            fetMonitorTransactionEvents(monitorTransactionId, response => {
              let transactionEvents = response.data?.events;
              let primaryEventKeyValue = findEventKeyValue(
                primaryEventTypeId,
                primaryEventKey,
                transactionEvents
              );
              setPrimaryEventData(findPrimaryEvent(primaryEventTypeId, transactionEvents));
              setIsPrimaryEventData(true);
              setAlertReason(
                `Missed ${primaryEventName} -> ${secondaryEventName} for more than ${monitorThreshold.toString()} seconds for ${primaryEventKey} => ${primaryEventKeyValue}`
              );
              setIsAlertReasonFetched(true);
              setLoading(false);
            });
          } else {
            setMonitorId(response.data?.alerts[0].trigger.monitor.id);
            setMonitorName(response.data?.alerts[0].trigger.monitor.name);
            let monitorTransactionId = response.data?.alerts[0].triggered_by.id;
            let monitorTimeThreshold =
              response.data?.alerts[0].trigger?.definition.delayed_event_trigger
                .transaction_time_threshold;
            let monitorResolution =
              response.data?.alerts[0].trigger?.definition.delayed_event_trigger.resolution;
            let monitorThreshold =
              response.data?.alerts[0].trigger?.definition.delayed_event_trigger.trigger_threshold;
            let monitor = response.data?.alerts[0].trigger?.monitor;
            let primaryEventName = monitor.primary_event_key.event_type.name;
            let secondaryEventName = monitor.secondary_event_key.event_type.name;
            setAlertReason(
              `${monitorThreshold.toString()}% of ${primaryEventName} -> ${secondaryEventName} missed for more than ${monitorTimeThreshold.toString()} seconds in the last ${monitorResolution.toString()} seconds`
            );
            setIsAlertReasonFetched(true);
            setLoading(false);
          }
        }
      });
    }
  }, [loading]);

  return (
    <Grid
      container
      style={{
        backgroundColor: '#f9fafc',
        // marginBottom: "-1000px ",
        paddingLeft: '20px'
      }}
    >
      <Grid item xs={12} md={9}>
        <Box
          component="div"
          sx={{
            borderRadius: '12px',
            overflow: 'hidden',
            marginTop: '10px'
          }}
        >
          <Box
            component="div"
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '20px'
            }}
          >
            <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
              Alert Details
            </Typography>
          </Box>
          {/* <Divider /> */}
        </Box>
      </Grid>

      {isAlertReasonFetched ? (
        <Grid item>
          <Card>
            <CardContent>
              <Grid container>
                <Grid item>
                  <Typography variant="body2">Monitor</Typography>
                  <Link to={`/monitors/${monitorId}`}>
                    <Typography variant="h5" sx={{ fontWeight: 600 }}>
                      {monitorName}
                    </Typography>
                  </Link>
                  <br></br>

                  <Typography variant="body2">Timestamp</Typography>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {moment(new Date(alertData?.triggered_at)).format('YYYY-MM-DD HH:mm:ss')}
                  </Typography>
                  <br></br>

                  {alertReason ? (
                    <>
                      <Typography variant="body2">Trigger</Typography>
                      <Typography variant="h5">
                        <i>{alertReason}</i>
                      </Typography>
                      <br></br>
                    </>
                  ) : (
                    ''
                  )}

                  {isPrimaryEventData ? (
                    <>
                      <Typography variant="body2" sx={{ mb: 0.5 }}>
                        Primary Event
                      </Typography>
                      <EventCard eventData={primaryEventData} />
                      <br></br>
                    </>
                  ) : (
                    ''
                  )}
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      ) : (
        <CircularProgress />
      )}
    </Grid>
  );
};

export default SingleAlert;
