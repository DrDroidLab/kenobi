import { Grid, Typography } from '@mui/material';
import logo from '../../data/no-data-alert-icon.png';
import CreateMonitorLink from './CreateMonitorLink';

const NoExistingMonitor = () => {
  return (
    <>
      <div className="justify-center w-full items-center flex flex-col py-8">
        <img src={logo} alt="logo" className="h-20 mb-4 " />
        <div className="text-sm text-gray-500 mb-2 text-center">No monitors created yet</div>
        <div>
          <CreateMonitorLink />
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
            No Monitors created yet
          </Typography>
        </Grid>
        <Grid item>
          <CreateMonitorLink />
        </Grid>
      </Grid>
    </>
  );
};

export default NoExistingMonitor;
