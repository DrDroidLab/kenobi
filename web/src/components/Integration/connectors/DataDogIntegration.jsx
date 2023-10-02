import { useEffect, useState } from 'react';
import API from '../../../API';
import Heading from '../../../components/Heading';
import SelectComponent from '../../SelectComponent';
import ValueComponent from '../../ValueComponent';

import { useNavigate } from 'react-router-dom';
import Toast from '../../../components/Toast';
import useToggle from '../../../hooks/useToggle';

import { groupedData2 } from '../../../utils/CreateMonitor';

import styles from '../../../css/createMonitor.module.css';

const DataDogIntegration = () => {
  const [apiKey, setApiKey] = useState();
  const [appKey, setAppKey] = useState();

  const [savedKeys, setSavedKeys] = useState(false);

  const [validationError, setValidationError] = useState();
  const { isOpen, toggle } = useToggle();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState();

  const fetchIntegrationKeys = API.useGetIntegrationKeys();
  const deleteIntegrationKeys = API.useDeleteIntegrationKeys();
  const saveIntegrationKeys = API.useSaveIntegrationKeys();

  const navigate = useNavigate();

  useEffect(() => {
    fetchIntegrationKeys(
      { connector_type: 12 },
      res => {
        if (res.data.connector_keys) {
          setAppKey(res.data.connector_keys.find(x => x.key_type == 'DATADOG_APP_KEY')?.key);
          setApiKey(res.data.connector_keys.find(x => x.key_type == 'DATADOG_API_KEY')?.key);
          setSavedKeys(true);
        } else {
          console.log('No Keys found');
        }
      },
      err => {
        console.error(err);
      }
    );
  }, []);

  const handleApiKeyChange = val => {
    setApiKey(val);
  };

  const handleAppKeyChange = val => {
    setAppKey(val);
  };

  const handleSave = () => {
    saveIntegrationKeys(
      {
        connector_type: 12,
        connector_keys: [
          { key_type: 2, key: appKey },
          { key_type: 3, key: apiKey }
        ]
      },
      res => {
        setSavedKeys(true);

        if (res.data.message) {
          alert(res.data.message);
          return;
        }
      },
      err => {
        console.error(err);
      }
    );
  };

  const handleDelete = () => {
    deleteIntegrationKeys(
      { connector_type: 12 },
      res => {
        setAppKey('');
        setApiKey('');
        setSavedKeys(false);

        if (res.data.message) {
          alert(res.data.message);
          return;
        }
      },
      err => {
        console.error(err);
      }
    );
  };

  return (
    <>
      <Heading
        heading={'Datadog Integration Setup'}
        onTimeRangeChangeCb={false}
        onRefreshCb={false}
      />

      <div className={styles['container']}>
        <div className={styles['heading']}>
          Datadog Keys{' '}
          <div style={{ fontSize: '15px' }}>
            (See how to get them ->{' '}
            <a
              style={{ color: '#9553fe' }}
              href="https://docs.datadoghq.com/account_management/api-app-keys/"
              target="_blank"
            >
              Datadog Docs
            </a>
            )
          </div>
        </div>
        <div className={styles['eventTypeSelectionSection']}>
          <div className={styles['content']}>API Key</div>
          <ValueComponent
            valueType={'STRING'}
            onValueChange={handleApiKeyChange}
            value={apiKey}
            placeHolder={'Enter Api Key'}
            length={500}
          />
        </div>
        <div className={styles['eventTypeSelectionSection']}>
          <div className={styles['content']}>App Key</div>
          <ValueComponent
            valueType={'STRING'}
            onValueChange={handleAppKeyChange}
            value={appKey}
            placeHolder={'Enter App Key'}
            length={500}
          />
        </div>
      </div>
      <button
        className="text-xs bg-white hover:bg-violet-500 hover:color-white-500 py-1 px-1 border border-gray-400 rounded shadow"
        onClick={handleSave}
        style={{
          marginLeft: '12px',
          marginBottom: '12px'
        }}
      >
        Save
      </button>
      {savedKeys && (
        <button
          className="text-xs bg-white hover:bg-violet-500 hover:color-white-500 py-1 px-1 border border-gray-400 rounded shadow"
          onClick={handleDelete}
          style={{
            marginLeft: '12px',
            marginBottom: '12px'
          }}
        >
          Delete
        </button>
      )}
      <Toast
        open={!!isOpen}
        severity="info"
        message={validationError}
        handleClose={() => toggle()}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      />
      <Toast
        open={!!IsError}
        severity="error"
        message={submitError}
        handleClose={() => toggleError()}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      />
    </>
  );
};

export default DataDogIntegration;
