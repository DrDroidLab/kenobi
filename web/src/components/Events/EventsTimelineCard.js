import { Divider } from '@mui/material';
import EventsTimeline from './EventsTimeline';
import { React } from 'react';
import styles from './index.module.css';

const EventsTimelineCard = ({ events }) => {
  return (
    <div className={styles['monitorStats']}>
      <h2 className={styles['title']}>Events Timeline</h2>
      <Divider />
      <div className={styles['statsContainer']}>
        <EventsTimeline events={events} />
      </div>
    </div>
  );
};

export default EventsTimelineCard;
