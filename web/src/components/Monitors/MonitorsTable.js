import {
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Button
} from '@mui/material';
import MonitorLink from './MonitorLink';
import React, { useState } from 'react';
import PaginatedTable from '../PaginatedTable';
import NoExistingMonitor from './NoExistingMonitor';
import useToggle from '../../hooks/useToggle';
import MonitorActionOverlay from './MonitorActionOverlay';

const MonitorsTableRender = ({ data, loading, refreshTable }) => {
  const { isOpen: isMonitorActionOpen, toggle } = useToggle();
  const [monitorActionId, setMonitorActionId] = useState();

  const handleActionClick = id => () => {
    setMonitorActionId(id);
    toggle();
  };
  return (
    <>
      {loading ? <LinearProgress /> : null}
      <Table stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell className="font-bold text-black">Name</TableCell>
            <TableCell className="font-bold text-black">Events</TableCell>
            <TableCell className="font-bold text-black">Status</TableCell>
            <TableCell className="font-bold text-black">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data?.map(item => (
            <TableRow
              key={item.id}
              sx={{
                '&:last-child td, &:last-child th': { border: 0 }
              }}
            >
              <TableCell component="th" scope="row">
                <MonitorLink monitor={item} style={{ color: 'rgb(149 83 254)' }} />
              </TableCell>
              <TableCell align="left">
                <Chip
                  label={item.primary_event_key.event_type.name}
                  // color="success"
                  style={{ backgroundColor: 'lightgreen' }}
                  sx={{ marginRight: 1 }}
                />
                <span> &rarr;</span>
                <Chip
                  label={item.secondary_event_key.event_type.name}
                  // color="secondary"
                  style={{ backgroundColor: 'lightblue' }}
                  sx={{ marginLeft: 1 }}
                />
              </TableCell>
              <TableCell align="left">
                <Chip
                  label={item.is_active ? 'Enabled' : 'Disabled'}
                  style={{ backgroundColor: item.is_active ? '#7FFFD4	' : 'lightgrey' }}
                />
              </TableCell>
              <TableCell align="left">
                <button onClick={handleActionClick(item.id)} style={{ color: 'rgb(149 83 254)' }}>
                  {item.is_active ? 'Disable' : 'Enable'}
                </button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {!data?.length ? <NoExistingMonitor /> : null}
      <MonitorActionOverlay
        data={data}
        id={monitorActionId}
        isOpen={isMonitorActionOpen}
        toggleOverlay={toggle}
        onRefresh={refreshTable}
      />
    </>
  );
};

const MonitorCardTableRenderer = ({ data, loading }) => (
  <>
    {loading ? <LinearProgress /> : null}
    <Table stickyHeader>
      <TableHead>
        <TableRow>
          <TableCell className="font-bold text-black">Name</TableCell>
          <TableCell className="font-bold text-black">Events</TableCell>
          <TableCell className="font-bold text-black">Status</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {data?.map(item => (
          <TableRow
            key={item.id}
            sx={{
              '&:last-child td, &:last-child th': { border: 0 }
            }}
          >
            <TableCell component="th" scope="row">
              <MonitorLink monitor={item} style={{ color: 'rgb(149 83 254)' }} />
            </TableCell>
            <TableCell align="left">
              <Chip
                label={item.primary_event_key.event_type.name}
                // color="success"
                style={{ backgroundColor: 'lightgreen' }}
                sx={{ marginRight: 1 }}
              />
              <span> &rarr;</span>
              <Chip
                label={item.secondary_event_key.event_type.name}
                // color="secondary"
                style={{ backgroundColor: 'lightblue' }}
                sx={{ marginLeft: 1 }}
              />
            </TableCell>
            <TableCell align="left">
              <Chip
                label={item.is_active ? 'Enabled' : 'Disabled'}
                style={{ backgroundColor: item.is_active ? '#7FFFD4	' : 'lightgrey' }}
              />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
    {!data?.length ? <NoExistingMonitor /> : null}
  </>
);

const MonitorsTable = ({
  monitors,
  total,
  pageSize,
  pageUpdateCb,
  tableContainerStyles,
  isCard = false
}) => {
  return (
    <PaginatedTable
      renderTable={isCard ? MonitorCardTableRenderer : MonitorsTableRender}
      data={monitors}
      total={total}
      pageSize={pageSize}
      tableContainerStyles={tableContainerStyles ? tableContainerStyles : {}}
      pageUpdateCb={pageUpdateCb}
    />
  );
};

export default MonitorsTable;
