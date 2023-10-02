import {
  Timeline,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineItem,
  TimelineSeparator
} from '@mui/lab';
import EventCard from './EventCard';
import styles from './index.module.css';

const EventsTimeline = ({ events }) => {
  return (
    <Timeline className={styles['timeline']}>
      {events?.map(elem => {
        return (
          <>
            <TimelineItem>
              <TimelineSeparator>
                <TimelineDot />
                <TimelineConnector />
              </TimelineSeparator>
              <TimelineContent>
                <EventCard eventData={elem} />
              </TimelineContent>
            </TimelineItem>
          </>
        );
      })}
    </Timeline>
  );
};

export default EventsTimeline;
