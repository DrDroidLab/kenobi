import EventTypeLink from './EventTypeLink';
import styles from './index.module.css';

const EventTypeKeyCard = ({ alias, heading, event_type_key }) => {
  return (
    <div className={styles['keyCard']}>
      <span className={styles['alias']}>{alias} </span>
      <EventTypeLink event_type={event_type_key?.event_type} />
      <span className={styles['keyName']}>{event_type_key?.key}</span>
    </div>
  );
};

export default EventTypeKeyCard;
