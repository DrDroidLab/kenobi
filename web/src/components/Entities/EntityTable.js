import { LinearProgress, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';
import { Link } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import styles from './index.module.css';
import redCross from '../../data/red-cross.webp';
import greenTick from '../../data/green-tick.png';

import API from '../../API';
import PaginatedTable from '../../components/PaginatedTable';
import SuspenseLoader from '../../components/Skeleton/SuspenseLoader';
import TableSkeleton from '../../components/Skeleton/TableLoader';

import InfoIcon from '@mui/icons-material/Info';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';

import ArrowDown from '../../data/arrow-down.svg';
import cx from 'classnames';
import ReportProblemIcon from '@mui/icons-material/ReportProblem';

import EntityInstanceDetail from './EntityInstanceDetail';

const Chips = ({ alertList }) => {
  return (
    <>
      {alertList.map((item, index) => (
        <a href={`/alerts/${item.alert_id}/`}>
          <span key={index} className={styles['chip-alert']}>
            {item.entity_trigger_name}
          </span>
        </a>
      ))}
    </>
  );
};

const EntityRow = ({ entity }) => {
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);

  const [entityInstanceTimeline, setEntityInstanceTimeline] = useState([]);
  const fetchEntityInstanceTimeline = API.useGetInstanceTimeline();

  const togglePanel = () => {
    setExpanded(!expanded);
    setLoading(true);

    if (!expanded) {
      fetchEntityInstanceTimeline(
        entity.entity_instance.id,
        pageMeta,
        response => {
          setLoading(false);
          setTotal(response.data?.meta?.total_count);
          setEntityInstanceTimeline(response.data?.entity_instance_timeline_records);
        },
        err => {
          setLoading(false);
        }
      );
    }
  };

  const [total, setTotal] = useState(0);
  const [pageMeta, setPageMeta] = useState({ limit: 10, offset: 0 });

  return (
    <React.Fragment>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
        <TableCell>
          <Tooltip title="See events for this entity">
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
          </Tooltip>
        </TableCell>
        <TableCell align="left" component="th" scope="row">
          {entity.entity_instance.instance}
        </TableCell>
        <TableCell align="left" component="th" scope="row">
          {entity.stats.event_count}
        </TableCell>
        <TableCell align="left" component="th" scope="row">
          {entity.stats.alerts?.length ? <Chips alertList={entity.stats.alerts} /> : ''}
        </TableCell>
      </TableRow>
      {expanded ? (
        <TableRow>
          <TableCell className={styles['kvCell']} colSpan={12}>
            <SuspenseLoader loading={!!loading} loader={<TableSkeleton noOfLines={3} />}>
              {entityInstanceTimeline?.length > 0 ? (
                <PaginatedTable
                  renderTable={EntityInstanceDetail}
                  data={entityInstanceTimeline}
                  total={total}
                  pageSize={pageMeta ? pageMeta?.limit : 10}
                />
              ) : null}
            </SuspenseLoader>
          </TableCell>
        </TableRow>
      ) : null}
    </React.Fragment>
  );
};

const EntityTable = ({ loading, data }) => {
  return (
    <>
      {loading ? <LinearProgress /> : null}
      <Table aria-label="events table" size="small">
        <TableHead>
          <TableRow>
            <TableCell />
            <TableCell className={styles['tableTitle']} align="left">
              <b>Instance&nbsp;</b>
              <Tooltip title="The attribute value with which all events in the entity are joined">
                <IconButton className={'p-2'}>
                  <InfoIcon />
                </IconButton>
              </Tooltip>
            </TableCell>
            <TableCell className={styles['tableTitle']} align="left">
              <b># Events&nbsp;</b>
              <Tooltip title="Number of events for this entity instance">
                <IconButton className={styles['toolTip']}>
                  <InfoIcon />
                </IconButton>
              </Tooltip>
            </TableCell>
            <TableCell className={styles['tableTitle']} align="left">
              <b>Alerts&nbsp;</b>
              <Tooltip title="Shows any alerts raised for this entity">
                <IconButton className={styles['toolTip']}>
                  <InfoIcon />
                </IconButton>
              </Tooltip>
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data?.map(row => (
            <EntityRow entity={row} key={row.entity_instance.id} />
          ))}
        </TableBody>
      </Table>
    </>
  );
};

export default EntityTable;
