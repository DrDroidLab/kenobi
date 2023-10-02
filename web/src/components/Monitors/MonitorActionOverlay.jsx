import React from 'react';
import Overlay from '../../components/Overlay';
import API from '../../API';
import styles from './index.module.css';

const MonitorActionOverlay = ({ data, id, isOpen, toggleOverlay, onRefresh }) => {
  const updateMonitors = API.useUpdateMonitors();
  const handleSuccess =
    ({ data, id }) =>
    () => {
      const item = data?.find(item => item.id === id);
      updateMonitors(
        {
          id: item.id,
          primary_event_key_id: item.primary_event_key.id,
          secondary_event_key_id: item.secondary_event_key.id,
          is_active: !item.is_active
        },
        response => {
          if (response.data.success) {
            onRefresh();
          }
          toggleOverlay();
        },
        () => {
          toggleOverlay();
        }
      );
    };
  return (
    <>
      {isOpen && (
        <Overlay visible={isOpen}>
          <div className={styles['monitorActionOverlay']}>
            <header className="text-gray-500">Are you sure, you want to toggle the action?</header>
            <div className={styles['actions']}>
              <button className={styles['mr-3']} onClick={toggleOverlay}>
                Cancel
              </button>
              <button onClick={handleSuccess({ data, id })}>Yes</button>
            </div>
          </div>
        </Overlay>
      )}
    </>
  );
};

export default MonitorActionOverlay;
