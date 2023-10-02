import moment from 'moment';
import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import API from '../API';
import Heading from '../components/Heading';
import SuspenseLoader from '../components/Skeleton/SuspenseLoader';
import TableSkeleton from '../components/Skeleton/TableLoader';
import { EVENT_TYPES, EVENT_TYPE_DISPLAY, TRANSACTIONS_TYPE } from '../constants';
import logo from '../data/black_logo_beta.png';
import { DataGrid } from '@mui/x-data-grid';

function getLocalTimeFromEpoch(epochSeconds) {
  if (typeof epochSeconds !== 'number') {
    epochSeconds = parseInt(epochSeconds);
  }

  const milliseconds = epochSeconds * 1000; // Convert seconds to milliseconds
  const localDate = new Date(milliseconds);

  // Get local timezone date and time as a string
  const year = localDate.getFullYear();
  const month = String(localDate.getMonth() + 1).padStart(2, '0'); // Month is zero-based
  const day = String(localDate.getDate()).padStart(2, '0');
  const hours = String(localDate.getHours()).padStart(2, '0');
  const minutes = String(localDate.getMinutes()).padStart(2, '0');
  const seconds = String(localDate.getSeconds()).padStart(2, '0');

  // Create the formatted string
  const localDatetimeString = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;

  return localDatetimeString;
}

function formatDuration(seconds) {
  if (seconds < 0) {
    throw new Error('Input must be a non-negative integer.');
  }

  if (seconds === 0) {
    return '0 seconds';
  }

  // Calculate the number of hours, minutes, and seconds
  const hours = Math.floor(seconds / 3600);
  seconds %= 3600;
  const minutes = Math.floor(seconds / 60);
  seconds %= 60;

  // Create an array to store the time components
  const components = [];

  // Add components with proper pluralization
  if (hours > 0) {
    components.push(`${hours} ${hours === 1 ? 'hour' : 'hours'}`);
  }
  if (minutes > 0) {
    components.push(`${minutes} ${minutes === 1 ? 'minute' : 'minutes'}`);
  }
  if (seconds > 0) {
    components.push(`${seconds} ${seconds === 1 ? 'second' : 'seconds'}`);
  }

  // Join the components into a human-readable string
  if (components.length === 1) {
    return components[0];
  } else if (components.length === 2) {
    return components.join(' and ');
  } else {
    return components.slice(0, -1).join(', ') + `, and ${components[components.length - 1]}`;
  }
}

const Alert = () => {
  let { alertId } = useParams();
  const [alertData, setAlertData] = useState({});
  const [eventPairData, setEventPairData] = useState([]);
  const [alertType, setAlertType] = useState('');
  const [triggerName, setTriggerName] = useState();
  const [loading, setLoading] = useState(false);
  const fetchAlertDetail = API.useGetAlertDetailData();
  const fetchAlertMonitorTransactions = API.useGetAlertMonitorTransactions();

  const renderKeyValuePair = (key, value) => {
    return (
      <div className="flex sm:flex-1 flex-row p-0 mr-8">
        <span className="text-gray-500 text-xs leading-4 mr-2">{key} </span>
        <span className="text-gray-800 text-xs leading-4">{value}</span>
      </div>
    );
  };

  const columns = [
    {
      field: 'created_at',
      headerName: 'Event Occured at',
      flex: 1,
      valueGetter: params => {
        return moment.unix(params?.row?.created_at).fromNow();
      }
    },
    {
      field: 'primary_event_name',
      headerName: 'Events',
      flex: 1,
      valueGetter: params => {
        const transactionType = params.row.type;
        if (transactionType === TRANSACTIONS_TYPE.DELAYED_TRANSACTION) {
          return `${params.row.primary_event_name} -> ${params.row.secondary_event_name}`;
        }
        return `${params.row.primary_event_name}`;
      }
    },
    {
      field: 'transaction',
      headerName: 'Primary Key Value',
      flex: 1,
      renderCell: params => {
        return (
          <Link
            to={`/monitor-transactions/${params.row.id}/`}
            className="text-violet-500 hover:underline"
          >
            {params.row.transaction}
          </Link>
        );
      }
    }
  ];

  const describeAlertReason = () => {
    if (alertType === EVENT_TYPES.PER_EVENT) {
      const entity_trigger_rule_type = alertData.entity_trigger.definition.rule_type;

      if (entity_trigger_rule_type === 'EVENT_OCCURS') {
        return (
          <span>
            Event {alertData.stats.event_name} was received for entity{' '}
            {alertData.entity_trigger.entity_name} with {alertData.stats.event_key_name} ->{' '}
            {alertData.stats.entity_instance_value}
          </span>
        );
      } else if (entity_trigger_rule_type === 'EVENT_COUNT') {
        const time_interval = alertData.entity_trigger.definition.trigger_rule_config.time_interval;

        const threshold_count =
          alertData.entity_trigger.definition.trigger_rule_config.threshold_count;
        let threshold_count_str = threshold_count + ' times';
        if (threshold_count == '1') {
          threshold_count_str = 'once';
        }

        return (
          <span>
            Event {alertData.stats.event_name} was received more than {threshold_count_str} within{' '}
            {formatDuration(time_interval)} for entity {alertData.entity_trigger.entity_name} with{' '}
            {alertData.stats.event_key_name} -> {alertData.stats.entity_instance_value}
          </span>
        );
      } else if (entity_trigger_rule_type === 'LAST_EVENT') {
        const time_interval = alertData.entity_trigger.definition.trigger_rule_config.time_interval;

        return (
          <span>
            No event was received for {formatDuration(time_interval)} after event{' '}
            {alertData.stats.event_name} occurred at{' '}
            {getLocalTimeFromEpoch(alertData.stats.event_timestamp)} for entity{' '}
            {alertData.entity_trigger.entity_name} with {alertData.stats.event_key_name} ->{' '}
            {alertData.stats.entity_instance_value}
          </span>
        );
      } else {
        return <span></span>;
      }
    }

    if (alertType === EVENT_TYPES.MISSING_EVENT) {
      let secondary_event_name = eventPairData[0].secondary_event_name;
      let primary_event_name = eventPairData[0].primary_event_name;
      const id = eventPairData[0].id;
      let delay = alertData.trigger.definition.missing_event_trigger.transaction_time_threshold;
      let key = alertData.trigger.monitor.primary_event_key.key;
      let keyValue = eventPairData[0].transaction;
      return (
        <span>
          Event {secondary_event_name} did not occur after {primary_event_name} for {delay} seconds
          for {key} -&#8827;{' '}
          <Link to={`/monitor-transactions/${id}/`} className="text-violet-500 hover:underline">
            {keyValue}
          </Link>
        </span>
      );
    }

    if (alertType === EVENT_TYPES.DELAYED_EVENT) {
      let secondary_event_name = eventPairData[0].secondary_event_name;
      let primary_event_name = eventPairData[0].primary_event_name;
      let delay = alertData.trigger.definition.delayed_event_trigger.transaction_time_threshold;
      let threshold = alertData.trigger.definition.delayed_event_trigger.trigger_threshold;
      let key = alertData.trigger.monitor.primary_event_key.key;
      return `Event ${secondary_event_name} did not occur for ${delay} seconds after ${primary_event_name} for the same ${key} for ${threshold}% of cases`;
    }

    return '';
  };

  useEffect(() => {
    setLoading(true);
    fetchAlertDetail(
      alertId,
      respAlertData => {
        setAlertData(respAlertData.data?.alert_detail);
        const { trigger, entity_trigger } = respAlertData.data?.alert_detail;

        if (trigger) {
          setTriggerName(trigger.name);
          fetchAlertMonitorTransactions(
            alertId,
            response => {
              const monitortransactionsData = response?.data?.monitor_transactions;
              const eventPairs = monitortransactionsData.map(monitorTransaction => ({
                id: monitorTransaction?.monitor_transaction?.id,
                type: monitorTransaction?.type,
                created_at: monitorTransaction?.monitor_transaction?.created_at,
                transaction: monitorTransaction?.monitor_transaction?.transaction,
                primary_event_name: trigger.monitor.primary_event_key?.event_type?.name,
                secondary_event_name: trigger.monitor.secondary_event_key?.event_type?.name
              }));
              setEventPairData(eventPairs);
              setAlertType(trigger.definition?.type);
              setLoading(false);
            },
            error => {
              setLoading(false);
              console.error('Error while fetching monitor transaction');
            }
          );
        } else {
          setTriggerName(entity_trigger.name);
          setAlertType(entity_trigger.definition?.type);
          setLoading(false);
        }
      },
      error => {
        setLoading(false);
        console.error('Error while fetching alert details data');
      }
    );
  }, []);

  return (
    <>
      <div className="py-2 px-3 border-b border-gray-300 bg-white flex sm:hidden">
        <img src={logo} alt="Logo" style={{ width: '129px' }} />
      </div>
      <Heading heading={`Alert / #${alertId}`}></Heading>
      <SuspenseLoader loading={!!loading} loader={<TableSkeleton />}>
        <div className="flex flex-col items-start p-0 m-3">
          {alertData.trigger
            ? alertType && (
                <div className="border border-gray-200 rounded bg-white flex flex-row flex-wrap items-start py-2 px-3 w-full mb-2 sm:h-full h-24">
                  {renderKeyValuePair('Monitor', alertData?.trigger?.monitor?.name)}
                  {renderKeyValuePair('Primary Event', eventPairData?.[0]?.primary_event_name)}
                  {renderKeyValuePair('Secondary Event', eventPairData?.[0]?.secondary_event_name)}
                </div>
              )
            : alertType && (
                <div className="border border-gray-200 rounded bg-white flex flex-row flex-wrap items-start py-2 px-3 w-full mb-2 sm:h-full h-24">
                  {renderKeyValuePair('Entity', alertData?.entity_trigger?.entity_name)}
                  {renderKeyValuePair(
                    'Event',
                    alertData?.entity_trigger?.definition.trigger_rule_config?.event_name
                  )}
                </div>
              )}

          {alertData.trigger
            ? alertType && (
                <div className="border border-gray-200 rounded bg-white flex flex-row flex-wrap items-start py-2 px-3 w-full mb-2 sm:h-full h-24">
                  {renderKeyValuePair('Trigger ', triggerName)}
                  {renderKeyValuePair('Trigger Type', EVENT_TYPE_DISPLAY[alertType])}
                  {renderKeyValuePair('Alert Time', moment(alertData?.triggered_at).fromNow())}
                </div>
              )
            : alertType && (
                <div className="border border-gray-200 rounded bg-white flex flex-row flex-wrap items-start py-2 px-3 w-full mb-2 sm:h-full h-24">
                  {renderKeyValuePair('Trigger ', triggerName)}
                  {renderKeyValuePair('Trigger Type', EVENT_TYPE_DISPLAY[alertType])}
                  {renderKeyValuePair('Alert Time', moment(alertData?.triggered_at).fromNow())}
                </div>
              )}

          {alertType && (
            <div className="border border-gray-200 rounded bg-white flex flex-row flex-wrap items-start py-2 px-3 w-full mb-2 sm:h-full h-24">
              {renderKeyValuePair('Trigger Condition', describeAlertReason())}
            </div>
          )}
          {alertType === EVENT_TYPES.DELAYED_EVENT && (
            <>
              <div className="border border-gray-200 rounded bg-white flex flex-row flex-wrap items-start py-2 px-3 w-full mb-2 sm:h-full h-24">
                {renderKeyValuePair(
                  'Evaluation Interval',
                  `${alertData?.trigger?.definition?.delayed_event_trigger?.resolution} secs`
                )}
                {renderKeyValuePair(
                  'Primary events occured',
                  alertData?.stats?.total_transaction_count
                )}
                {renderKeyValuePair(
                  'Secondary event missed',
                  alertData?.stats?.missed_transaction_count
                )}
                {renderKeyValuePair('Median Delay Time', alertData?.stats?.median_delay)}
              </div>
              <div className="border border-gray-200 bg-white flex flex-row items-start py-2 px-3 w-full">
                <span className="text-gray-600 text-xs leading-4">All Events Pair</span>
              </div>
              <div className="border border-gray-200 bg-white flex flex-row items-start w-full h-fit sm:flex hidden">
                <DataGrid
                  sx={{
                    '.MuiDataGrid-columnSeparator': {
                      display: 'none'
                    },
                    '&.MuiDataGrid-root': {
                      border: 'none'
                    },
                    '.MuiDataGrid-columnHeaderTitle': {
                      fontStyle: 'normal',
                      fontWeight: '400',
                      fontFamily: 'Inter',
                      fontSize: '12px',
                      lineHeight: '150%',
                      color: '#6B7280'
                    },
                    '.MuiDataGrid-cellContent': {
                      fontStyle: 'normal',
                      fontWeight: '400',
                      fontFamily: 'Inter',
                      fontSize: '12px',
                      lineHeight: '150%',
                      color: '#000'
                    },
                    '.MuiDataGrid-row:hover': {
                      backgroundColor: 'white'
                    }
                  }}
                  hideFooter
                  autoHeight
                  disableColumnMenu
                  sortable={false}
                  hideFooterPagination
                  rows={eventPairData}
                  columns={columns.map(column => ({
                    ...column,
                    sortable: false
                  }))}
                  headerHeight={34}
                  rowHeight={32}
                  getRowId={params => params?.id}
                  disableSelectionOnClick
                />
              </div>
              <div className="border border-gray-200 rounded bg-white flex flex-row flex-wrap items-start py-2 px-3 w-full mb-2 sm:hidden flex">
                <div className="flex sm:flex-1 flex-row p-1">
                  <span className="text-gray-500 text-xs">
                    List of Events will get displayed in desktop version.
                  </span>
                </div>
              </div>
            </>
          )}
        </div>
      </SuspenseLoader>
      {/* <Toast
        open={toastOpen}
        handleClose={handleCloseToast}
        message={toastMsg}
        severity={'error'}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      /> */}
    </>
  );
};

export default Alert;
