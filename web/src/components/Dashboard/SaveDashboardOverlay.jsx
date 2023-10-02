import React from 'react';
import { useCallback, useEffect, useState } from 'react';
import Overlay from '../../components/Overlay';
import ValueComponent from '../ValueComponent';
import API from '../../API';
import styles from './index.module.css';

const SaveDashboardOverlay = ({ isOpen, close, saveCallback }) => {
  const [name, setName] = useState();

  const handleSuccess = ({ name }) => {
    saveCallback(name);
  };

  return (
    <>
      {isOpen && (
        <Overlay visible={isOpen}>
          <div className={styles['saveOverlay']}>
            <div className={styles['dashName']}>
              <ValueComponent
                valueType={'STRING'}
                onValueChange={val => setName(val)}
                value={name}
                placeHolder={'Enter Dashboard name'}
                length={300}
              />
            </div>
            <div className={styles['actions']}>
              <button className={styles['submitButton']} onClick={() => close()}>
                Cancel
              </button>

              <button
                className={styles['submitButton']}
                onClick={() => handleSuccess({ name })}
                style={{
                  marginLeft: '12px'
                }}
              >
                Save
              </button>
            </div>
          </div>
        </Overlay>
      )}
    </>
  );
};

export default SaveDashboardOverlay;
