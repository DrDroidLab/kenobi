import {
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TableSortLabel,
  Box
} from '@mui/material';
import React from 'react';
import PaginatedTable from '../PaginatedTable';
import MonitorTransactionLink from './MonitorTransactionLink';
import { renderTimestamp } from '../../utils/DateUtils';
import NoExistingMonitorTransaction from './NoExistingMonitorTransaction';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { visuallyHidden } from '@mui/utils';

const MonitorsTransactionTableRender = ({ loading, data, onSortChange, orderData }) => {
  const { orderByName, order } = orderData;

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
    if (days > 0) {
      return `${days} days `;
    }
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

  const statusMap = { SECONDARY_RECEIVED: 'Finished', PRIMARY_RECEIVED: 'Active' };

  return (
    <>
      {loading ? <LinearProgress /> : null}
      <Table stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell style={{ color: 'black', fontWeight: 'bold' }}>Transaction Value</TableCell>
            <TableCell align="left" style={{ color: 'black', fontWeight: 'bold' }}>
              <b>Transaction Age&nbsp;</b>
            </TableCell>
            <TableCell
              align="left"
              style={{ color: 'black', fontWeight: 'bold' }}
              sortDirection={orderByName === 'transaction_time' ? order : false}
            >
              {typeof orderByName !== 'undefined' ? (
                <TableSortLabel
                  active={orderByName === 'transaction_time'}
                  direction={orderByName === 'transaction_time' ? order : 'asc'}
                  onClick={() => {
                    const isAsc = orderByName === 'transaction_time' && order === 'asc';
                    onSortChange({
                      orderByName: 'transaction_time',
                      order: isAsc ? 'desc' : 'asc'
                    });
                  }}
                >
                  <b>Transaction Time&nbsp;</b>
                  {orderByName === 'transaction_time' ? (
                    <Box component="span" sx={visuallyHidden}>
                      {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                    </Box>
                  ) : null}
                </TableSortLabel>
              ) : (
                <b>Transaction Time&nbsp;</b>
              )}
            </TableCell>
            <TableCell align="left" style={{ color: 'black', fontWeight: 'bold' }}>
              Status
            </TableCell>
            <TableCell
              align="left"
              style={{ color: 'black', fontWeight: 'bold' }}
              sortDirection={orderByName === 'created_at' ? order : false}
            >
              {typeof orderByName !== 'undefined' ? (
                <TableSortLabel
                  active={orderByName === 'created_at'}
                  direction={orderByName === 'created_at' ? order : 'asc'}
                  onClick={() => {
                    const isAsc = orderByName === 'created_at' && order === 'asc';
                    onSortChange({
                      orderByName: 'created_at',
                      order: isAsc ? 'desc' : 'asc'
                    });
                  }}
                >
                  <b>Created At&nbsp;</b>
                  {orderByName === 'created_at' ? (
                    <Box component="span" sx={visuallyHidden}>
                      {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                    </Box>
                  ) : null}
                </TableSortLabel>
              ) : (
                <b>Created At&nbsp;</b>
              )}
            </TableCell>
            <TableCell align="left" style={{ color: 'black', fontWeight: 'bold' }}>
              Alerted
            </TableCell>
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
              <TableCell component="th" scope="row">
                <MonitorTransactionLink
                  monitor_transaction={item?.monitor_transaction}
                  style={{ color: 'rgb(149 83 254)' }}
                />
              </TableCell>
              <TableCell align="left">
                {timeElapsed(item?.monitor_transaction.transaction_age)}
              </TableCell>
              <TableCell align="left">
                {timeElapsed(item?.stats?.transaction_time) || '-'}
              </TableCell>
              <TableCell align="left">
                {statusMap[item?.monitor_transaction.status]
                  ? statusMap[item?.monitor_transaction.status]
                  : item?.monitor_transaction.status}
              </TableCell>
              <TableCell align="left">
                {renderTimestamp(item?.monitor_transaction.created_at)}
              </TableCell>
              <TableCell align="left">
                {item?.monitor_transaction.has_alerts ? (
                  <ErrorOutlineIcon style={{ color: 'red' }} />
                ) : null}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {!data?.length ? <NoExistingMonitorTransaction /> : null}
    </>
  );
};

const MonitorTransactionsTable = ({
  monitor_transactions,
  total,
  pageSize,
  pageUpdateCb,
  tableContainerStyles,
  onSortChange,
  orderData
}) => {
  return (
    <PaginatedTable
      renderTable={MonitorsTransactionTableRender}
      data={monitor_transactions}
      total={total}
      pageSize={pageSize}
      tableContainerStyles={tableContainerStyles ? tableContainerStyles : {}}
      pageUpdateCb={pageUpdateCb}
      onSortChange={onSortChange}
      orderData={orderData}
    />
  );
};

export default MonitorTransactionsTable;
