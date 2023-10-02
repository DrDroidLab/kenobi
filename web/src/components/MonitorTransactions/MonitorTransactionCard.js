import React, { useState } from 'react';
import MonitorLink from '../Monitors/MonitorLink';
import { Divider } from '@mui/material';
import { renderTimestamp } from '../../utils/DateUtils';
import styles from './index.module.css';

import ErrorOutlineOutlinedIcon from '@mui/icons-material/ErrorOutlineOutlined';

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

const MonitorTransactionCard = ({ monitorTransaction, alerts }) => {
  return (
    <div className={styles['monitorStats']}>
      <h2 className={styles['title']}>Transaction Details</h2>
      <Divider />
      <div className={styles['statsContainer']}>
        <div className={styles['stat']}>
          <div className={styles['statName']}>Monitor</div>
          <div className={styles['statValue']}>
            <MonitorLink monitor={monitorTransaction?.monitor} />
          </div>
        </div>
        <div className={styles['vl']}></div>
        <div className={styles['stat']}>
          <div className={styles['statName']}>Status</div>
          <div className={styles['statValue']}>{monitorTransaction?.status}</div>
        </div>
        <div className={styles['vl']}></div>
        <div className={styles['stat']}>
          <div className={styles['statName']}>Created at</div>
          <div className={styles['statValue']}>
            {renderTimestamp(monitorTransaction?.created_at)}
          </div>
        </div>
        <div className={styles['vl']}></div>
        <div className={styles['stat']}>
          <div className={styles['statName']}>Triggered Alerts</div>
          <div className={styles['statValue']}>
            {alerts?.length ? <Chips alertList={alerts} /> : ''}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MonitorTransactionCard;
