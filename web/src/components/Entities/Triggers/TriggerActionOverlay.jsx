import React, { useCallback, useEffect, useState } from 'react';
import Overlay from '../../Overlay';
import API from '../../../API';
import styles from './index.module.css';
import { CircularProgress } from '@mui/material';

const TriggerActionOverlay = ({
  entity_trigger_id,
  entity_trigger_name,
  isOpen,
  toggleOverlay,
  onRefresh
}) => {
  const [loading, setLoading] = useState(false);

  const deactivateTrigger = API.useDeactivateEntityTrigger();

  const handleSuccess = () => {
    setLoading(true);
    deactivateTrigger(
      {
        entity_trigger_id: entity_trigger_id
      },
      response => {
        if (response.data.success) {
          onRefresh();
        }
        setLoading(false);
        toggleOverlay();
      },
      () => {
        setLoading(false);
        toggleOverlay();
      }
    );
  };

  return (
    <>
      {isOpen && (
        <Overlay visible={isOpen}>
          <div className={styles['actionOverlay']}>
            <header className="text-gray-500">Delete {entity_trigger_name}?</header>
            <div className={styles['actions']}>
              <button className={styles['submitButton']} onClick={toggleOverlay}>
                Cancel
              </button>
              <button
                className={styles['submitButtonRight']}
                sx={{ marginLeft: '5px' }}
                onClick={() => handleSuccess()}
              >
                Yes
              </button>
              {loading ? (
                <CircularProgress
                  style={{
                    marginLeft: '12px',
                    marginBottom: '12px'
                  }}
                  size={20}
                />
              ) : (
                ''
              )}
            </div>
          </div>
        </Overlay>
      )}
    </>
  );
};

export default TriggerActionOverlay;
