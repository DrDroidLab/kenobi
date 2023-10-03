import { Button, Grid, Typography } from '@mui/material';
import logo from '../../data/logo.png';
import { Link } from 'react-router-dom';

const NoExistingEntity = () => {
  return (
    <>
      <div className="justify-center w-full items-center flex flex-col py-8">
        <img src={logo} alt="logo" className="h-20 mb-4 " />
        <div className="text-sm text-gray-500 mb-2 text-center">No entity discovered yet</div>
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
};

export default NoExistingEntity;