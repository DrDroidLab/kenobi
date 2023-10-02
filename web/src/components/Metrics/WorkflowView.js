import React, { useEffect, useState } from 'react';
import SwitchTabs from '../components/WorkflowViewTabs/SwitchTabs';
import { useLocation } from 'react-router-dom';
import API from '../API';

const WorkflowView = () => {
  const location = useLocation();
  const workflow_id = location.state.workflow_id;

  const [responseData, setResponseData] = useState({});
  const [isResponseReceived, setIsResponseReceived] = useState(false);
  const fetchWorkflowDefinition = API.useFetchWorkflowDefinition();
  useEffect(() => {
    fetchWorkflowDefinition(workflow_id, response => {
      setResponseData(response.data.workflow_definition);
      setIsResponseReceived(true);
    });
  }, []);

  return (
    <div>
      {isResponseReceived ? (
        <>
          <SwitchTabs input={responseData} />
        </>
      ) : (
        <p style={{ marginLeft: '20px' }}>Loading Workflow view...</p>
      )}
    </div>
  );
};

export default WorkflowView;
