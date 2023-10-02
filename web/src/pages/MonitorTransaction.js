import { useParams } from 'react-router-dom';
import { useCallback, useEffect, useState } from 'react';
import API from '../API';
import { CircularProgress, Divider, Grid } from '@mui/material';
import Heading from '../components/Heading';
import MonitorTransactionCard from '../components/MonitorTransactions/MonitorTransactionCard';
import EventsTimeline from '../components/Events/EventsTimeline';
import EventsTimelineCard from '../components/Events/EventsTimelineCard';

const MonitorTransaction = () => {
  let { id, tab } = useParams();

  const [loading, setLoading] = useState(true);
  const [monitorTransaction, setMonitorTransaction] = useState({});
  const [fetchedMonitorTransaction, setFetchedMonitorTransaction] = useState(false);
  const fetchMonitorTransactions = API.useGetMonitorTransactions();

  const [monitorTransactionEvents, setMonitorTransactionEvents] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [fetchedMonitorTransactionEvents, setFetchedMonitorTransactionEvents] = useState(false);

  const fetchMonitorTransactionEvents = API.useGetMonitorsTransactionsEvents();

  const loadingCb = useCallback(() => {
    setLoading(true);
    setFetchedMonitorTransaction(false);
  }, [loading]);

  useEffect(() => {
    if (loading) {
      fetchMonitorTransactions(
        null,
        {
          transaction_ids: [id]
        },
        [],
        resp => {
          if (resp.data?.monitor_transactions?.length > 0) {
            setMonitorTransaction(resp.data?.monitor_transactions[0]);
          }
          if (resp.data?.alerts?.length > 0) {
            setAlerts(resp.data?.alerts);
          }
          setFetchedMonitorTransaction(true);
          setLoading(false);
        },
        err => {
          setLoading(false);
          setFetchedMonitorTransaction(true);
        },
        false
      );

      fetchMonitorTransactionEvents(
        id,
        resp => {
          setMonitorTransactionEvents(resp.data?.events);
          setFetchedMonitorTransactionEvents(true);
        },
        err => {
          setFetchedMonitorTransactionEvents(true);
        },
        false
      );
    }
  }, [loading]);

  return (
    <>
      <Heading
        subHeading="Monitor Transaction"
        heading={loading ? <CircularProgress size={20} /> : `${monitorTransaction?.transaction}`}
        onRefreshCb={loadingCb}
      />
      <div className={'p-1'}>
        {fetchedMonitorTransaction ? (
          <MonitorTransactionCard monitorTransaction={monitorTransaction} alerts={alerts} />
        ) : null}
      </div>

      <div className={'p-1'}>
        <EventsTimelineCard events={monitorTransactionEvents} />
      </div>
    </>
  );
};

export default MonitorTransaction;
