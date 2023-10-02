import EventTypeKeyCard from '../EventType/EventKeyCard';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import styles from './index.module.css';

const MonitorCard = ({ monitor }) => {
  return (
    <div className={styles['eventKeys']}>
      <EventTypeKeyCard
        alias={'P'}
        heading={'Primary'}
        event_type_key={monitor?.primary_event_key}
      />
      <ArrowForwardIcon />
      <EventTypeKeyCard
        alias={'S'}
        heading={'Secondary'}
        event_type_key={monitor?.secondary_event_key}
      />
    </div>
  );
};

export default MonitorCard;
