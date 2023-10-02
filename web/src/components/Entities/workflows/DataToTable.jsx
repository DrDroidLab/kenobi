import React from 'react';
import { LinearProgress, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';

import styles from './index.module.css';

const DataToTable = ({ data }) => {
  return (
    <div className={styles['stages']}>
      {data.map(stage => (
        <Table aria-label="events table" size="small" className={styles['tableBorder']}>
          <TableHead>
            <TableRow>
              <TableCell className={styles['tableTitle']} align="left">
                <b>{stage.stage}</b>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {stage.events?.map(ev =>
              ev.child_events ? (
                <TableRow className={styles['tableRow']}>
                  {ev.child_events.map(cn => (
                    <TableCell align="left" className={styles['tableCell']}>
                      <i>{cn.event_name}</i>
                      <br></br>
                      <b>{cn.unique_records_count}</b>
                    </TableCell>
                  ))}
                </TableRow>
              ) : (
                <TableRow className={styles['tableRow']}>
                  <TableCell align="left">
                    <i>{ev.event_name}</i>
                    <br></br>
                    <b>{ev.unique_records_count}</b>
                  </TableCell>
                </TableRow>
              )
            )}
          </TableBody>
        </Table>
      ))}
    </div>
  );
};

export default DataToTable;
