import { CardContent, CardHeader, Chip, Grid, Typography, Card } from '@mui/material';

const AlertDefinition = ({ alertDefinition }) => {
  return (
    <Grid container direction="column" spacing={2}>
      <Grid item>
        <Card></Card>
      </Grid>

      <Grid item>
        <Card>
          <CardHeader title={'Sources'} />
          <CardContent></CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default AlertDefinition;
