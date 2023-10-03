import {
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Chip,
  Button
} from '@mui/material';

import React, { useState } from 'react';

import InfoIcon from '@mui/icons-material/Info';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';

import API from '../../API';

import DeleteIcon from '@mui/icons-material/Delete';

import { Link } from 'react-router-dom';
import PaginatedTable from '../PaginatedTable';
import NoExistingDashboard from './NoExistingDashboard';
import styles from './index.module.css';

import useToggle from '../../hooks/useToggle';

import EditIcon from '@mui/icons-material/Edit';

import DashboardActionOverlay from './DashboardActionOverlay';

import dayjs from 'dayjs';

const DashboardTableRender = ({ data, loading, refreshTable }) => {
  const { isOpen: isActionOpen, toggle } = useToggle();
  const [actionDashName, setActionDashName] = useState();

  const handleActionClick = dashName => () => {
    setActionDashName(dashName);
    toggle();
  };

  return (
    <>
      {loading ? <LinearProgress /> : null}
      <Table stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell className={styles['tableTitle']}>Name</TableCell>
            <TableCell className={styles['tableTitle']}>Panel Types</TableCell>
            <TableCell className={styles['tableTitle']}>Actions</TableCell>
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
                <Link to={`/dashboard/${btoa(item?.name)}`} className={styles['link']}>
                  {item.name}
                </Link>
              </TableCell>
              <TableCell component="th" scope="row">
                {item.panels.map((panel, index) =>
                  panel.data.type ? (
                    <Chip
                      key={index}
                      label={panel.data.type}
                      style={{ backgroundColor: '#ebebeb ' }}
                      className={styles['chip']}
                    />
                  ) : (
                    <Chip
                      key={index}
                      label={'CHART'}
                      style={{ backgroundColor: '#ebebeb ' }}
                      className={styles['chip']}
                    />
                  )
                )}
              </TableCell>
              <TableCell component="th" scope="row">
                <Button onClick={handleActionClick(item.name)}>
                  <Tooltip title="Delete">
                    <IconButton aria-label="delete">
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {!data?.length ? <NoExistingDashboard /> : null}
      <DashboardActionOverlay
        dash_name={actionDashName}
        isOpen={isActionOpen}
        toggleOverlay={toggle}
        onRefresh={refreshTable}
      />
    </>
  );
};

const DashboardTableCardRender = ({ data, loading, refreshTable }) => {
  return (
    <>
      {loading ? <LinearProgress /> : null}
      <Table stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell className={styles['tableTitle']}>Name</TableCell>
            <TableCell className={styles['tableTitle']}>Panel Types</TableCell>
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
                <Link to={`/dashboard/${btoa(item?.name)}`} className={styles['link']}>
                  {item.name}
                </Link>
              </TableCell>
              <TableCell component="th" scope="row">
                {item.panels.map((panel, index) =>
                  panel.data.type ? (
                    <Chip
                      key={index}
                      label={panel.data.type}
                      style={{ backgroundColor: '#ebebeb ' }}
                      className={styles['chip']}
                    />
                  ) : (
                    <Chip
                      key={index}
                      label={'CHART'}
                      style={{ backgroundColor: '#ebebeb ' }}
                      className={styles['chip']}
                    />
                  )
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {!data?.length ? <NoExistingDashboard /> : null}
    </>
  );
};

const DashboardTable = ({
  dashList,
  total,
  pageSize,
  pageUpdateCb,
  tableContainerStyles,
  isCard
}) => {
  return (
    <PaginatedTable
      renderTable={isCard ? DashboardTableCardRender : DashboardTableRender}
      data={dashList}
      total={total}
      pageSize={pageSize}
      pageUpdateCb={pageUpdateCb}
      tableContainerStyles={tableContainerStyles ? tableContainerStyles : {}}
    />
  );
};

export default DashboardTable;
