import React, { useState } from 'react';
import {
  LinearProgress,
  Table,
  Collapse,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Drawer,
  Box
} from '@mui/material';
import { Link } from 'react-router-dom';
import styles from './index.module.css';
import dayjs from 'dayjs';
import ArrowDown from '../../data/arrow-down.svg';
import cx from 'classnames';

import InfoIcon from '@mui/icons-material/Info';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';

import SearchIcon from '@mui/icons-material/Search';

const Chips = ({ alertList }) => {
  return (
    <>
      {alertList.map((item, index) => (
        <a href={`/alerts/${item.alert_id}/`}>
          <span key={index} className={styles['chip-alert']}>
            {item.trigger_name}
          </span>
        </a>
      ))}
    </>
  );
};

const EntityInstanceRow = ({ entity_instance }) => {
  const { event, timestamp, transaction_event_type_mapping, alerts } = entity_instance;
  const [expanded, setExpanded] = useState(false);

  const transactionCount = transaction_event_type_mapping
    ? transaction_event_type_mapping.length
    : 0;

  const togglePanel = () => {
    setExpanded(!expanded);
  };

  return (
    <React.Fragment>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
        <TableCell>
          <button onClick={() => togglePanel()}>
            <img
              width="20px"
              height="20px"
              src={ArrowDown}
              className={cx(styles['arrow-down-icon'], {
                [styles['open']]: expanded
              })}
            />
          </button>
        </TableCell>
        <TableCell align="left" component="th" scope="row">
          {event.event_type.name}
        </TableCell>
        <TableCell align="left" component="th" scope="row">
          {dayjs.unix(timestamp / 1000).format('YYYY-MM-DD HH:mm:ss')}
        </TableCell>
      </TableRow>
      {expanded ? (
        <TableRow>
          <TableCell className={styles['kvCell']} colSpan={6}>
            <Table aria-label="events table" size="small">
              <TableHead>
                <TableRow>
                  <TableCell className={styles['tableTitle']} align="left">
                    Attribute&nbsp;
                  </TableCell>
                  <TableCell className={styles['tableTitle']} align="left">
                    Value&nbsp;
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {event.kvs?.map(row => (
                  <TableRow>
                    <TableCell className={styles['tableData']} align="left">
                      {row.key}&nbsp;
                    </TableCell>
                    <TableCell className={styles['tableData']} align="left">
                      {row.value.string_value ||
                        row.value.int_value ||
                        row.value.bool_value?.toString() ||
                        row.value.double_value}
                      &nbsp;
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableCell>
        </TableRow>
      ) : null}
    </React.Fragment>
  );
};

const EntityInstanceDetail = ({ loading, data }) => {
  return (
    <>
      {loading ? <LinearProgress /> : null}
      <Table aria-label="events table" size="small">
        <TableHead>
          <TableRow>
            <TableCell />
            <TableCell className={styles['tableTitle']} align="left">
              <b>Event&nbsp;</b>
            </TableCell>
            <TableCell className={styles['tableTitle']} align="left">
              <b>Created at&nbsp;</b>
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data?.map(row => (
            <EntityInstanceRow entity_instance={row} key={row} />
          ))}
        </TableBody>
      </Table>
    </>
  );
};

export default EntityInstanceDetail;
