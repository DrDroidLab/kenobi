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

const NewRelicIntegration = () => {
  const [apiKey, setApiKey] = useState();
  const [appId, setAppId] = useState();

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
      { connector_type: 18 },
      res => {
        if (res.data.connector_keys) {
          setApiKey(res.data.connector_keys.find(x => x.key_type == 'NEWRELIC_API_KEY')?.key);
          setAppId(res.data.connector_keys.find(x => x.key_type == 'NEWRELIC_APP_ID')?.key);
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

  const handleAppIdChange = val => {
    setAppId(val);
  };

  const handleSave = () => {
    saveIntegrationKeys(
      {
        connector_type: 18,
        connector_keys: [
          { key_type: 4, key: apiKey },
          { key_type: 5, key: appId }
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
      { connector_type: 18 },
      res => {
        setAppId('');
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
        heading={'NewRelic Integration Setup'}
        onTimeRangeChangeCb={false}
        onRefreshCb={false}
      />

      <div className={styles['container']}>
        <div className={styles['heading']}>
          NewRelic Keys{' '}
          <div style={{ fontSize: '15px' }}>
            (See how to get them ->{' '}
            <a
              style={{ color: '#9553fe' }}
              href="https://docs.newrelic.com/docs/apis/intro-apis/new-relic-api-keys/"
              target="_blank"
            >
              NewRelic Docs
            </a>
            )
          </div>
        </div>
        <div className={styles['eventTypeSelectionSection']}>
          <div className={styles['content']}>API Key (User)</div>
          <ValueComponent
            valueType={'STRING'}
            onValueChange={handleApiKeyChange}
            value={apiKey}
            placeHolder={'Enter Api Key'}
            length={500}
          />
        </div>
        <div className={styles['eventTypeSelectionSection']}>
          <div className={styles['content']}>Account ID</div>
          <ValueComponent
            valueType={'STRING'}
            onValueChange={handleAppIdChange}
            value={appId}
            placeHolder={'Enter Account ID'}
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

export default NewRelicIntegration;
