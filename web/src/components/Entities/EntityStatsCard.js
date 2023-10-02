import styles from './index.module.css';
import redCross from '../../data/red-cross.webp';
import greenTick from '../../data/green-tick.png';

const EntityStatsCard = ({ entityStats }) => {
  return (
    <div className={styles['entityStats']}>
      <div className={styles['stat']}>
        <div className={styles['statName']}>Health</div>
        <div className={styles['statValue']}>
          <img
            className={styles['crossIcon']}
            src={entityStats?.has_alerts ? redCross : greenTick}
            alt="cancel"
            width="18px"
            height="18px"
          />
        </div>
      </div>
      <div className={styles['vl']}></div>
      <div className={styles['stat']}>
        <div className={styles['statName']}>Events</div>
        <div className={styles['statValue']}>{entityStats?.event_count}</div>
      </div>
      <div className={styles['vl']}></div>
      <div className={styles['stat']}>
        <div className={styles['statName']}>Monitor Transactions</div>
        <div className={styles['statValue']}>{entityStats?.transaction_count}</div>
      </div>
    </div>
  );
};

export default EntityStatsCard;
