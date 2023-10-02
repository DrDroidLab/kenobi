import { Link } from 'react-router-dom';
import { Button } from '@mui/material';
import React from 'react';

const CreateMonitorLink = () => {
  const handleCreateMonitorClick = () => {
    window?.analytics?.track('Create Monitor Button Clicked');
  };
  return (
    <Link to="/monitors/create">
      <button
        className="text-sm bg-violet-600 hover:bg-violet-700 px-4 py-2  rounded-lg"
        onClick={handleCreateMonitorClick}
        style={{ color: 'white', marginTop: '0px', marginRight: '10px' }}
      >
        + Create Monitor
      </button>
      {/* <Button variant="contained" style={{ backgroundColor: '#9553FE'}}>
        + Create Monitor
      </Button> */}
    </Link>
  );
};
export default CreateMonitorLink;
