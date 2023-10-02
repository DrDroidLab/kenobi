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
import MonitorActionOverlay from '../../Monitors/MonitorActionOverlay';

import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';

import EditIcon from '@mui/icons-material/Edit';
import styles from './index.module.css';

const timeElapsed = seconds => {
  let time = Math.ceil(seconds);
  let days = Math.floor(time / (3600 * 24));
  time -= days * 3600 * 24;
  let hrs = Math.floor(time / 3600);
  time -= hrs * 3600;
  let mnts = Math.floor(time / 60);
  time -= mnts * 60;
  let scnds = time;
  let res = '';
  if (hrs > 0) {
    return `${hrs} hrs `;
  }
  if (mnts > 0) {
    return `${mnts} mins `;
  }
  if (scnds > 0) {
    return `${scnds} secs `;
  }
  return res;
};

const TriggersTableRender = ({ data, loading, refreshTable, params }) => {
  const { isOpen: isTriggerActionOpen, toggle } = useToggle();
  const [triggerActionId, setTriggerActionId] = useState();

  const entity_id = params?.entity_id;

  const handleVisibilityIconClick = id => {
    window?.analytics?.track(`Entity Trigger update ${id}`, {
      $triggerId: id
    });
  };

  const handleActionClick = id => () => {
    setTriggerActionId(id);
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
            <TableCell className="font-bold text-black">Rule</TableCell>
            <TableCell className="font-bold text-black">Event</TableCell>
            <TableCell className="font-bold text-black">Time Interval</TableCell>
            <TableCell className="font-bold text-black">Threshold Count</TableCell>
            <TableCell className="font-bold text-black">Actions</TableCell>
            <TableCell className="font-bold text-black">Status</TableCell>
            <TableCell></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data?.map(item => (
            <TableRow
              key={item.trigger?.id}
              sx={{
                '&:last-child td, &:last-child th': { border: 0 }
              }}
            >
              <TableCell component="th" scope="row">
                {item.trigger?.name}
              </TableCell>
              <TableCell component="th" scope="row">
                {item.trigger?.definition.type}
              </TableCell>
              <TableCell align="left">{item.trigger?.definition.rule_type}</TableCell>
              <TableCell align="left">
                {item.trigger?.definition.trigger_rule_config.event_name}
              </TableCell>
              <TableCell align="left">
                {timeElapsed(item.trigger?.definition.trigger_rule_config.time_interval)}
              </TableCell>
              <TableCell align="left">
                {item.trigger?.definition.trigger_rule_config.threshold_count}
              </TableCell>
              <TableCell align="left">
                {item.notifications?.length >= 1
                  ? item.notifications[0]?.channel === 'SLACK'
                    ? 'Slack Alert'
                    : 'Email Alert'
                  : ''}
              </TableCell>
              <TableCell align="left">
                <Chip
                  label={item?.trigger?.is_active ? 'Active' : 'Inactive'}
                  style={{ backgroundColor: item?.trigger?.is_active ? '#7FFFD4 ' : 'lightgrey' }}
                />
              </TableCell>
              <TableCell align="left">
                <a href={`/entity/${entity_id}/triggers/${item?.trigger?.id}/update`}>
                  <Tooltip title="Edit">
                    <IconButton className={styles['toolTip']}>
                      <EditIcon onClick={() => handleVisibilityIconClick(item?.trigger?.id)} />
                    </IconButton>
                  </Tooltip>
                </a>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {!data?.length ? <NoExistingTrigger monentity_iditor_id={entity_id} /> : null}
      <MonitorActionOverlay
        data={data}
        id={triggerActionId}
        isOpen={isTriggerActionOpen}
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
