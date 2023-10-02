import { Link } from 'react-router-dom';
import { Button } from '@mui/material';
import React from 'react';

const CreateTriggerLink = ({ entity_id }) => {
  const handleCreateTriggerClick = () => {
    window?.analytics?.track('Create Entity Trigger Button Clicked');
  };

  const createTriggerLink = '/entity/' + entity_id + '/triggers/create';

  return (
    <Link to={createTriggerLink}>
      <button
        className="text-sm bg-violet-600 hover:bg-violet-700 px-4 py-2  rounded-lg"
        onClick={handleCreateTriggerClick}
        style={{ color: 'white', marginTop: '0px', marginRight: '10px' }}
      >
        + Create Trigger
      </button>
      {/* <Button variant="contained" style={{ backgroundColor: '#9553FE'}}>
        + Create Trigger
      </Button> */}
    </Link>
  );
};
export default CreateTriggerLink;
