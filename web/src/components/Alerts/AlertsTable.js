import {
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow
} from '@mui/material';
import { Link } from 'react-router-dom';

import moment from 'moment';
import PaginatedTable from '../PaginatedTable';
import MonitorLink from '../Monitors/MonitorLink';
import EntityLink from '../Entities/EntityLink';
import NoExistingEventType from '../EventType/NoExistingEventType';
import NoExistingAlert from './NoExistingAlert';

const AlertsTableRender = ({ data, loading }) => {
  const handleVisibilityIconClick = id => {
    window?.analytics?.track(`Alert load ${id}`, {
      $alertId: id
    });
  };

  return (
    <>
      {loading ? <LinearProgress /> : null}
      <Table stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell style={{ color: 'black', fontWeight: 'bold' }}>Trigger</TableCell>
            <TableCell style={{ color: 'black', fontWeight: 'bold' }}>Source</TableCell>
            <TableCell style={{ color: 'black', fontWeight: 'bold' }}>Alert Type</TableCell>
            <TableCell style={{ color: 'black', fontWeight: 'bold' }}>Events</TableCell>
            <TableCell style={{ color: 'black', fontWeight: 'bold' }}>Timestamp</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data?.map((item, index) => (
            <TableRow
              key={index}
              sx={{
                '&:last-child td, &:last-child th': { border: 0 }
              }}
            >
              <TableCell align="left">
                {item.trigger ? item.trigger.name : item.entity_trigger.name}
              </TableCell>
              <TableCell align="left">
                {item.trigger ? (
                  <MonitorLink
                    monitor={item?.trigger?.monitor_details?.monitor}
                    style={{ color: 'rgb(149 83 254)' }}
                  />
                ) : (
                  <EntityLink
                    entity={{
                      id: item?.entity_trigger?.entity_id,
                      name: item?.entity_trigger?.entity_name
                    }}
                    style={{ color: 'rgb(149 83 254)' }}
                  />
                )}
              </TableCell>
              <TableCell align="left">
                {item?.trigger?.type == 'MISSING_EVENT' ||
                item?.entity_trigger?.definition?.type == 'PER_EVENT'
                  ? 'Per Event Alert'
                  : 'Aggregated Events Alert'}
              </TableCell>
              <TableCell align="left">
                {item.trigger ? (
                  <>
                    <Chip
                      label={item?.trigger?.monitor_details?.primary_event_type.name}
                      // color="success"
                      style={{ backgroundColor: 'lightgreen' }}
                      sx={{ marginRight: 1 }}
                    />
                    <span> &rarr;</span>
                    <Chip
                      label={item?.trigger?.monitor_details?.secondary_event_type.name}
                      // color="secondary"
                      style={{ backgroundColor: 'lightblue' }}
                      sx={{ marginLeft: 1 }}
                    />
                  </>
                ) : (
                  <Chip
                    label={item?.entity_trigger?.definition?.trigger_rule_config?.event_name}
                    // color="success"
                    style={{ backgroundColor: 'lightgreen' }}
                    sx={{ marginRight: 1 }}
                  />
                )}
              </TableCell>
              <TableCell align="left">
                <a href={`/alerts/${item?.id}`} style={{ color: 'rgb(149 83 254)' }}>
                  <button onClick={() => handleVisibilityIconClick(item?.id)}>
                    <u>{moment.unix(item?.triggered_at).fromNow()}</u>
                  </button>
                </a>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {!data?.length ? <NoExistingAlert /> : null}
    </>
  );
};

const AlertsTable = ({ alerts, total, pageSize, pageUpdateCb, tableContainerStyles }) => {
  return (
    <PaginatedTable
      renderTable={AlertsTableRender}
      data={alerts}
      total={total}
      pageSize={pageSize}
      pageUpdateCb={pageUpdateCb}
      tableContainerStyles={tableContainerStyles ? tableContainerStyles : {}}
    />
  );
};

export default AlertsTable;
