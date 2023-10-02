import React, { useEffect } from 'react';
import { FrigadeChecklist, useUser } from '@frigade/react';

const Checklist = () => {
  const { setUserId } = useUser();

  useEffect(() => {
    const userId = localStorage.getItem('email');
    setUserId(userId);
  }, []);
  return (
    <div>
      <FrigadeChecklist
        flowId="flow_zl4DcdKqqnszzUG2"
        title="Getting started"
        type="inline"
        checklistStyle="inline"
      />
    </div>
  );
};

export default Checklist;
