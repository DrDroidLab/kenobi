import { CardContent, CardHeader, Chip, Grid, Card } from '@mui/material';
import EventKeyTable from './EventKeyTable';

import styles from './index.module.css';

const EventTypeDefinition = ({ eventTypeDefinition }) => {
  return (
    <Grid container direction="column" spacing={2}>
      <Grid item>
        <Card>
          <CardHeader title="Keys" />
          <EventKeyTable eventKeyList={eventTypeDefinition?.event_type?.keys} />
        </Card>
      </Grid>

      <Grid item>
        <Card>
          <CardHeader title={'Sources'} />
          <CardContent>
            {eventTypeDefinition?.event_type?.event_sources?.map((source, idx) => (
              <Chip label={source} key={idx} className={styles['sourceChip']} />
            ))}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default EventTypeDefinition;
