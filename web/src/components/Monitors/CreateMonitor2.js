import { useEffect, useState } from 'react';
import API from '../../API';
import Heading from '../../components/Heading';
import SelectComponent from '../SelectComponent';
import ValueComponent from '../ValueComponent';

import { useNavigate } from 'react-router-dom';
import Toast from '../../components/Toast';
import useToggle from '../../hooks/useToggle';

import { groupedData2 } from '../../utils/CreateMonitor';

import styles from '../../css/createMonitor.module.css';

const CreateMonitor2 = () => {
  const [eventTypeOptions, setEventTypeOptions] = useState();
  const [eventTypeAttrOptions, setEventTypeAttrOptions] = useState([]);

  const [monitorName, setMonitorName] = useState();

  const [primaryAttrOptions, setPrimaryAttrOptions] = useState([]);
  const [primarySelectedEventType, setPrimarySelectedEventType] = useState();
  const [primarySelectedEventAttrType, setPrimarySelectedEventAttrType] = useState();

  const [secondaryAttrOptions, setSecondaryAttrOptions] = useState([]);
  const [secondarySelectedEventType, setSecondarySelectedEventType] = useState();
  const [secondarySelectedEventAttrType, setSecondarySelectedEventAttrType] = useState();

  const [validationError, setValidationError] = useState();
  const { isOpen, toggle } = useToggle();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState();

  const getMonitorOptions = API.useGetMonitorOptions();
  const createMonitor = API.useCreateMonitors();

  const navigate = useNavigate();

  useEffect(() => {
    getMonitorOptions(
      res => {
        let monitorOptions = groupedData2(res);

        let c = monitorOptions[0];
        setEventTypeOptions(c);
        let d = monitorOptions[1];
        setEventTypeAttrOptions(d);
      },
      err => {
        console.error(err);
      }
    );
  }, []);

  const handlePrimaryEventTypeChange = id => {
    const options =
      eventTypeAttrOptions[id]?.map(option => ({
        id: option?.id,
        label: option?.name,
        type: option?.type
      })) || [];
    setPrimarySelectedEventType(id);
    setPrimaryAttrOptions(options);
    setPrimarySelectedEventAttrType(null);

    if (id === secondarySelectedEventType) {
      setValidationError('Select two different events for creating monitor');
      toggle();
    }
  };

  const handleSecondaryEventTypeChange = id => {
    const options =
      eventTypeAttrOptions[id]?.map(option => ({
        id: option?.id,
        label: option?.name,
        type: option?.type
      })) || [];
    setSecondarySelectedEventType(id);
    setSecondaryAttrOptions(options);
    setSecondarySelectedEventAttrType(null);

    if (id === primarySelectedEventType) {
      setValidationError('Select two different events for creating monitor');
      toggle();
    }
  };

  const validateMonitorForm = () => {
    if (primarySelectedEventType === secondarySelectedEventType) {
      return 'Select two different events for creating monitor';
    }
    if (!monitorName) {
      return 'Enter a monitor name';
    }
    if (!primarySelectedEventType) {
      return 'Select a primary event';
    }
    if (!primarySelectedEventAttrType) {
      return 'Select an attribute for the primary event';
    }
    if (!secondarySelectedEventType) {
      return 'Select a secondary event';
    }
    if (!secondarySelectedEventAttrType) {
      return 'Select an attribute for the secondary event';
    }
    return '';
  };

  const handleSubmitSaveAndCreateTrigger = () => {
    let formValidationError = validateMonitorForm();
    if (formValidationError) {
      toggleError();
      setSubmitError(formValidationError);
      return;
    }

    const payload = {
      primary_event_key_id: primarySelectedEventAttrType,
      secondary_event_key_id: secondarySelectedEventAttrType,
      name: monitorName
    };

    createMonitor(payload, response => {
      if (response.data.success) {
        window?.analytics?.track('Monitor Created & Redirecting to Create Triggers');
        const monitor_id = response.data.monitor.id;
        const createTriggerLink = `/monitors/${monitor_id}/triggers/create`;
        navigate(createTriggerLink, { params: { monitor_id: monitor_id } });
      }
    });
  };

  const handleSubmitSave = () => {
    let formValidationError = validateMonitorForm();
    if (formValidationError) {
      toggleError();
      setSubmitError(formValidationError);
      return;
    }

    const payload = {
      primary_event_key_id: primarySelectedEventAttrType,
      secondary_event_key_id: secondarySelectedEventAttrType,
      name: monitorName
    };

    createMonitor(payload, response => {
      if (response.data.success) {
        window?.analytics?.track('Monitor Created');
        navigate('/monitors/' + response.data?.monitor?.id + '/');
      }
    });
  };

  const handlePrimaryAttributeChange = id => {
    setPrimarySelectedEventAttrType(id);
  };

  const handleSecondaryAttributeChange = id => {
    setSecondarySelectedEventAttrType(id);
  };

  const handleMonitorNameChange = val => {
    setMonitorName(val);
  };

  return (
    <>
      <Heading heading={'Create Monitor'} onTimeRangeChangeCb={false} onRefreshCb={false} />
      <div className={styles['container']}>
        <div className={styles['heading']}>
          <div className={styles['content']}>Monitor Name</div>
          <ValueComponent
            valueType={'STRING'}
            onValueChange={handleMonitorNameChange}
            value={monitorName}
            placeHolder={'Enter monitor name'}
          />
        </div>
      </div>

      <div className={styles['container']}>
        <div className={styles['heading']}>
          Events{' '}
          <div className={styles['subHeading']}>
            {' '}
            Select events whose relative behavior you want to monitor. Choose attributes that
            connect them.{' '}
          </div>{' '}
        </div>
        <div className={styles['eventTypeSelectionSection']}>
          <div className={styles['content']}>Primary Event</div>
          {eventTypeOptions && (
            <SelectComponent
              data={eventTypeOptions}
              placeholder="Select event type"
              onSelectionChange={handlePrimaryEventTypeChange}
              selected={primarySelectedEventType}
              searchable={true}
            />
          )}
          {primarySelectedEventType && (
            <>
              <div className={styles['content']}>Select attribute</div>
              <SelectComponent
                data={primaryAttrOptions}
                placeholder="Select attribute"
                onSelectionChange={handlePrimaryAttributeChange}
                selected={primarySelectedEventAttrType}
                className={styles['selectList']}
                searchable={true}
              />
            </>
          )}
        </div>
        <div className={styles['eventTypeSelectionSection']}>
          <div className={styles['content']}>Secondary Event</div>
          {eventTypeOptions && (
            <SelectComponent
              data={eventTypeOptions}
              placeholder="Select event type"
              onSelectionChange={handleSecondaryEventTypeChange}
              selected={secondarySelectedEventType}
              searchable={true}
            />
          )}
          {secondarySelectedEventType && (
            <>
              <div className={styles['content']}>Select attribute</div>
              <SelectComponent
                data={secondaryAttrOptions}
                placeholder="Select attribute"
                onSelectionChange={handleSecondaryAttributeChange}
                selected={secondarySelectedEventAttrType}
                searchable={true}
              />
            </>
          )}
        </div>
      </div>
      <button
        className="text-xs bg-white hover:bg-violet-500 hover:color-white-500 py-1 px-1 border border-gray-400 rounded shadow"
        onClick={handleSubmitSave}
        style={{
          marginLeft: '12px',
          marginBottom: '12px'
        }}
      >
        Save
      </button>
      <button
        className="text-xs bg-white hover:bg-violet-500 hover:color-white-500 py-1 px-1 border border-gray-400 rounded shadow"
        onClick={handleSubmitSaveAndCreateTrigger}
        style={{
          marginLeft: '12px',
          marginBottom: '12px'
        }}
      >
        Save & Create Triggers
      </button>
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

export default CreateMonitor2;
