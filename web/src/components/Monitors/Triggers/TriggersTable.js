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
import React, { useState } from 'react';
import PaginatedTable from '../../PaginatedTable';
import NoExistingTrigger from './NoExistingTrigger';
import useToggle from '../../../hooks/useToggle';
import MonitorActionOverlay from '../MonitorActionOverlay';

import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';

import EditIcon from '@mui/icons-material/Edit';
import styles from './index.module.css';

const TriggersTableRender = ({ data, loading, refreshTable, params }) => {
  const { isOpen: isMonitorActionOpen, toggle } = useToggle();
  const [monitorActionId, setMonitorActionId] = useState();

  const monitor_id = params?.monitor_id;

  const handleVisibilityIconClick = id => {
    window?.analytics?.track(`Trigger update ${id}`, {
      $triggerId: id
    });
  };

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
            <TableCell className="font-bold text-black">Type</TableCell>
            <TableCell className="font-bold text-black">Delay (seconds)</TableCell>
            <TableCell className="font-bold text-black">Threshold (%)</TableCell>
            <TableCell className="font-bold text-black">Evaluation Interval (minutes)</TableCell>
            <TableCell className="font-bold text-black">Actions</TableCell>
            <TableCell className="font-bold text-black">Status</TableCell>
            <TableCell></TableCell>
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
                {item.trigger.name}
              </TableCell>
              <TableCell component="th" scope="row">
                {item.trigger.definition.type === 'MISSING_EVENT'
                  ? 'Per Event'
                  : 'Aggregated Events'}
              </TableCell>
              <TableCell align="left">
                {item.trigger.definition.type === 'MISSING_EVENT'
                  ? item.trigger.definition.missing_event_trigger.transaction_time_threshold
                  : item.trigger.definition.delayed_event_trigger.transaction_time_threshold}
              </TableCell>
              <TableCell align="left">
                {item.trigger.definition.type === 'MISSING_EVENT'
                  ? '-'
                  : item.trigger.definition.delayed_event_trigger.trigger_threshold + '%'}
              </TableCell>
              <TableCell align="left">
                {item.trigger.definition.type === 'MISSING_EVENT'
                  ? '-'
                  : item.trigger.definition.delayed_event_trigger.resolution / 60}
              </TableCell>
              <TableCell align="left">
                {item.notifications?.length >= 1
                  ? item.notifications[0].channel === 'SLACK'
                    ? 'Slack Alert'
                    : 'Email Alert'
                  : ''}
              </TableCell>
              <TableCell align="left">
                <Chip
                  label={item.trigger.is_active ? 'Active' : 'Inactive'}
                  style={{ backgroundColor: item.trigger.is_active ? '#7FFFD4 ' : 'lightgrey' }}
                />
              </TableCell>
              <TableCell align="left">
                <a href={`/monitors/${monitor_id}/triggers/${item?.trigger.id}/update`}>
                  <Tooltip title="Edit">
                    <IconButton className={styles['toolTip']}>
                      <EditIcon onClick={() => handleVisibilityIconClick(item?.trigger.id)} />
                    </IconButton>
                  </Tooltip>
                </a>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {!data?.length ? <NoExistingTrigger monitor_id={monitor_id} /> : null}
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

const TriggersTable = ({
  triggers,
  total,
  params,
  pageSize,
  pageUpdateCb,
  tableContainerStyles
}) => {
  return (
    <PaginatedTable
      renderTable={TriggersTableRender}
      data={triggers}
      total={total}
      pageSize={pageSize}
      tableContainerStyles={tableContainerStyles ? tableContainerStyles : {}}
      pageUpdateCb={pageUpdateCb}
      params={params}
    />
  );
};

export default TriggersTable;
