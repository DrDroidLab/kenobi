import { Link } from 'react-router-dom';
import { Button } from '@mui/material';
import React from 'react';

const CreateEntityLink = () => {
  const handleCreateEntityClick = () => {
    window?.analytics?.track('Create Entity Button Clicked');
  };
  return (
    <Link to="/entity/create">
      <button
        className="text-sm bg-violet-600 hover:bg-violet-700 px-4 py-2  rounded-lg"
        onClick={handleCreateEntityClick}
        style={{ color: 'white', marginTop: '0px', marginRight: '10px' }}
      >
        + Create Entity
      </button>
      {/* <Button variant="contained" style={{ backgroundColor: '#9553FE'}}>
        + Create Monitor
      </Button> */}
    </Link>
  );
};
export default CreateEntityLink;
