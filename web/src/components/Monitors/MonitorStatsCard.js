import styles from './index.module.css';

const MonitorStatsCard = ({ monitorStats }) => {
  return (
    <div className={styles['monitorStats']}>
      <div className={styles['stat']}>
        <div className={styles['statName']}>
          <span className={styles['alias']}>{'P'}</span> Event count
        </div>
        <div className={styles['statValue']}>{monitorStats?.transaction_count}</div>
      </div>
      <div className={styles['vl']}></div>
      <div className={styles['stat']}>
        <div className={styles['statName']}>
          <span className={styles['alias']}>{'S'}</span> Event count
        </div>
        <div className={styles['statValue']}>{monitorStats?.finished_transaction_count}</div>
      </div>
      <div className={styles['vl']}></div>
      <div className={styles['stat']}>
        <div className={styles['statName']}>Avg Delay (Finished transactions)</div>
        <div className={styles['statValue']}>{monitorStats?.transaction_avg_delay} s</div>
      </div>
      <div className={styles['vl']}></div>
      <div className={styles['stat']}>
        <div className={styles['statName']}>p95 delay (Finished transactions)</div>
        <div className={styles['statValue']}>{monitorStats?.percentiles?.p95} s</div>
      </div>
      <div className={styles['vl']}></div>
      <div className={styles['stat']}>
        <div className={styles['statName']}>p99 delay (Finished transactions)</div>
        <div className={styles['statValue']}>{monitorStats?.percentiles?.p99} s</div>
      </div>
    </div>
  );
};

export default MonitorStatsCard;
