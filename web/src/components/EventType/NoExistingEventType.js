import { Button, Grid, Typography } from '@mui/material';
import logo from '../../data/logo.png';
import { Link } from 'react-router-dom';

const NoExistingEventType = () => {
  return (
    <>
      <div className="justify-center w-full items-center flex flex-col py-8">
        <img src={logo} alt="logo" className="h-20 mb-4 " />
        <div className="text-sm text-gray-500 mb-2 text-center">No event types discovered yet</div>
        <div>
          <Link to="https://docs.drdroid.io" target="_blank">
            <div
              variant="contained"
              className="text-sm rounded-lg py-2 px-2 cursor-pointer border-violet-600 text-violet-600 dura hover:text-violet-700 underline flex"
            >
              Check Documentation
            </div>
          </Link>
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
            No Event Types discovered yet
          </Typography>
        </Grid>
        <Grid item>
          <Link to="https://docs.drdroid.io" target="_blank">
            <Button variant="contained" style={{ backgroundColor: '#9553FE' }}>
              Check Documentation
            </Button>
          </Link>
        </Grid>
      </Grid>
    </>
  );
};

export default NoExistingEventType;
