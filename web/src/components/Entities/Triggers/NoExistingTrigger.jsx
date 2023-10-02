import { Grid, Typography } from '@mui/material';
import logo from '../../../data/no-data-alert-icon.png';
import CreateTriggerLink from './CreateTriggerLink';

const NoExistingTrigger = ({ entity_id }) => {
  return (
    <>
      <div className="justify-center w-full items-center flex flex-col py-8">
        <img src={logo} alt="logo" className="h-20 mb-4 " />
        <div className="text-sm text-gray-500 mb-2 text-center">
          No triggers created yet for this Entity
        </div>
      </div>
    </>
  );
  return (
    <>
      <Grid container direction="column" justifyContent="center" alignItems="center">
        <Grid item>
          <img src={logo} alt="logo" className="h-40 " />
        </Grid>
        <Grid item>
          <Typography
            style={{
              color: 'grey'
            }}
          >
            No Triggers created yet for this Entity
          </Typography>
        </Grid>
      </Grid>
    </>
  );
};

export default NoExistingTrigger;
