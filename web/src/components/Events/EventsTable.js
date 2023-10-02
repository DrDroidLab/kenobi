import {
  Box,
  Collapse,
  IconButton,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
  TableSortLabel
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import dayjs from 'dayjs';
import EventTypeLink from '../EventType/EventTypeLink';
import functions from '../../utils/Utility';
import React, { useState } from 'react';
import { visuallyHidden } from '@mui/utils';

const EventRow = ({ event }) => {
  const [open, setOpen] = useState(false);

  return (
    <React.Fragment>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
        <TableCell>
          <IconButton aria-label="expand row" size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowDownIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell component="th" scope="row" align="left">
          {event?.id}
        </TableCell>
        <TableCell align="left">
          {dayjs.unix(event?.timestamp).format('YYYY-MM-DD HH:mm:ss')}
        </TableCell>
        <TableCell align="left">
          <EventTypeLink event_type={event?.event_type} style={{ color: 'rgb(126 35 206)' }} />
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <Typography variant="h6" gutterBottom component="div">
                Attributes
              </Typography>
              <Table size="small" aria-label="purchases">
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <b>Key</b>
                    </TableCell>
                    <TableCell>
                      <b>Value</b>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>{functions.renderEventKvs(event)}</TableBody>
              </Table>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </React.Fragment>
  );
};

const EventsTable = ({
  loading,
  data,
  onSortChange,
  orderData = {
    orderByName: undefined,
    order: undefined
  }
}) => {
  const { orderByName, order } = orderData;
  return (
    <>
      {loading ? <LinearProgress /> : null}
      <Table aria-label="events table" size="small">
        <TableHead>
          <TableRow>
            <TableCell />
            <TableCell style={{ color: 'black', fontWeight: 'bold' }} align="left">
              <b>Event Id&nbsp;</b>
            </TableCell>
            <TableCell
              style={{ color: 'black', fontWeight: 'bold' }}
              align="left"
              sortDirection={orderByName === 'timestamp_in_seconds' ? order : false}
            >
              {typeof orderByName !== 'undefined' ? (
                <TableSortLabel
                  active={orderByName === 'timestamp_in_seconds'}
                  direction={orderByName === 'timestamp_in_seconds' ? order : 'asc'}
                  onClick={() =>
                    onSortChange({
                      orderByName: 'timestamp_in_seconds',
                      orderByType: 'TIMESTAMP'
                    })
                  }
                >
                  <b>Timestamp&nbsp;</b>
                  {orderByName === 'timestamp_in_seconds' ? (
                    <Box component="span" sx={visuallyHidden}>
                      {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                    </Box>
                  ) : null}
                </TableSortLabel>
              ) : (
                <b>Timestamp&nbsp;</b>
              )}
            </TableCell>
            <TableCell style={{ color: 'black', fontWeight: 'bold' }} align="left">
              <b>Event Type&nbsp;</b>
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data?.map(row => (
            <EventRow event={row} key={row.id} />
          ))}
        </TableBody>
      </Table>
    </>
  );
};

export default EventsTable;
