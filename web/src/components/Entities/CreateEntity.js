import { useCallback, useEffect, useState } from 'react';
import API from '../../API';
import Heading from '../../components/Heading';
import SelectComponent from '../SelectComponent';
import ValueComponent from '../ValueComponent';
import cx from 'classnames';
import cross from '../../data/cross.svg';

import { CircularProgress } from '@mui/material';

import { randomString } from '../../utils/utils';

import { useNavigate } from 'react-router-dom';
import Toast from '../../components/Toast';
import useToggle from '../../hooks/useToggle';

import { groupedData3 } from '../../utils/CreateMonitor';

import styles from '../../css/createMonitor.module.css';

const CreateEntity = () => {
  const [eventTypeOptions, setEventTypeOptions] = useState();
  const [eventTypeAttrOptions, setEventTypeAttrOptions] = useState([]);

  const [entityName, setEntityName] = useState();

  const [eventsList, setEventsList] = useState([]);

  const [validationError, setValidationError] = useState();
  const { isOpen, toggle } = useToggle();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState();

  const [similarEventsLoading, setSimilarEventsLoading] = useState(false);
  const [searchResponseMessage, setSearchResponseMessage] = useState('');

  const getEntityOptions = API.useEntityCreateOptions();
  const createEntity = API.useCreateEntity();
  const searchEventKeys = API.useSearchEventKeys();

  const navigate = useNavigate();

  useEffect(() => {
    getEntityOptions(
      res => {
        let entityOptions = groupedData3(res);

        let c = entityOptions[0];
        setEventTypeOptions(c);
        let d = entityOptions[1];
        setEventTypeAttrOptions(d);
      },
      err => {
        console.error(err);
      }
    );
  }, []);

  const handleEventTypeChange = (id, item_id) => {
    const selectedListItem = eventsList.find(item => item.id === item_id);

    const options =
      eventTypeAttrOptions[id]?.map(option => ({
        id: option?.id,
        label: option?.name,
        type: option?.type
      })) || [];

    eventsList.splice(
      eventsList.findIndex(item => item.id === item_id),
      1,
      {
        ...selectedListItem,
        event_type_id: id,
        event_attribution_options: options
      }
    );

    setEventsList([...eventsList]);
  };

  const handleAttributeTypeChange = (id, item_id) => {
    const selectedListItem = eventsList.find(item => item.id === item_id);

    eventsList.splice(
      eventsList.findIndex(item => item.id === item_id),
      1,
      {
        ...selectedListItem,
        event_key_id: id
      }
    );

    setEventsList([...eventsList]);
  };

  const handleAddEventClick = () => {
    setEventsList([...eventsList, { event_type_id: null, event_key_id: null, id: randomString() }]);
  };

  const handleFindSimilarEventsClick = () => {
    const event_keys_ids = eventsList.map(item => item.event_key_id);
    setSimilarEventsLoading(true);
    setSearchResponseMessage('');
    searchEventKeys(
      { event_key_ids: event_keys_ids },
      res => {
        console.log(res.data);
        const event_keys = res.data.event_keys;

        for (let i = 0; i < event_keys.length; i++) {
          let transformedEvent = {};

          transformedEvent['event_key_id'] = event_keys[i].id;

          let event_type_id = event_keys[i].event_type.id;
          transformedEvent['event_type_id'] = event_type_id;

          const options =
            eventTypeAttrOptions[event_type_id]?.map(option => ({
              id: option?.id,
              label: option?.name,
              type: option?.type
            })) || [];

          transformedEvent['event_attribution_options'] = options;
          transformedEvent['id'] = randomString();
          eventsList.push(transformedEvent);
        }

        setSimilarEventsLoading(false);
        setSearchResponseMessage('Found ' + res.data?.event_keys?.length + ' similar events');
      },
      err => {
        console.error(err);
        setSimilarEventsLoading(false);
      }
    );
  };

  const validateEntityForm = () => {
    let eventTypeIdList = eventsList.map(item => item.event_type_id);
    let isRepeated = eventTypeIdList.some((item, index) => eventTypeIdList.indexOf(item) !== index);

    if (isRepeated) {
      return 'Select all different events for creating the entity';
    }

    if (!entityName) {
      return 'Enter an entity name';
    }

    if (eventsList.length < 2) {
      return 'Select atleast two events for creating an entity';
    }

    for (let i = 0; i < eventsList.length; i++) {
      if (eventsList[i].event_type_id && !eventsList[i].event_key_id) {
        return 'Select attribute for all events';
      }
    }

    return '';
  };

  const handleSubmitSave = () => {
    let formValidationError = validateEntityForm();
    if (formValidationError) {
      toggleError();
      setSubmitError(formValidationError);
      return;
    }

    let eventKeyIds = eventsList.filter(item => item.event_key_id).map(item => item.event_key_id);

    let payload = {
      name: entityName,
      is_active: true,
      event_key_ids: eventKeyIds
    };

    createEntity(payload, response => {
      if (response.data.success) {
        window?.analytics?.track('Entity Created');
        navigate('/entity/' + response.data?.entity?.id + '/');
      }
    });
  };

  const handleRemove = id => {
    const updatedList = eventsList.filter(item => item.id !== id);
    setEventsList([...updatedList]);
  };

  const handleEntityNameChange = val => {
    setEntityName(val);
  };

  const renderAttributeList = list => {
    return list.map(item => (
      <div className={styles['eventTypeSelectionSection']}>
        <div className={styles['content']}>Event</div>
        <SelectComponent
          data={eventTypeOptions}
          placeholder="Select event type"
          onSelectionChange={id => handleEventTypeChange(id, item.id)}
          selected={item.event_type_id}
          className={styles['selectList']}
          searchable={true}
        />
        {item.event_type_id && (
          <>
            <div className={styles['content-centre']}>Attribute</div>
            <SelectComponent
              data={item.event_attribution_options}
              placeholder="Select attribute"
              onSelectionChange={id => handleAttributeTypeChange(id, item.id)}
              selected={item.event_key_id}
              className={styles['selectList']}
              searchable={true}
            />
          </>
        )}
        <img
          className={styles['crossIcon']}
          src={cross}
          alt="cancel"
          width="18px"
          height="18px"
          onClick={() => handleRemove(item.id)}
        />
      </div>
    ));
  };

  return (
    <>
      <Heading heading={'Create Entity'} onTimeRangeChangeCb={false} onRefreshCb={false} />
      <div className={styles['container']}>
        <div className={styles['heading']}>
          <div className={styles['content']}>Entity Name</div>
          <ValueComponent
            valueType={'STRING'}
            onValueChange={handleEntityNameChange}
            value={entityName}
            placeHolder={'Enter entity name'}
          />
        </div>
      </div>

      <div className={styles['container']}>
        <div className={styles['heading']}>
          Events{' '}
          <div className={styles['subHeading']}>
            {' '}
            Select events which represent an quantifiable object in your business that you want to
            monitor. Choose attributes that connect them.{' '}
          </div>{' '}
        </div>
        {eventsList?.length >= 1 && renderAttributeList(eventsList)}
        <div className={styles['eventsEnrich']}>
          <div
            className={cx(styles['content'], styles['addConditionStyle'])}
            onClick={handleAddEventClick}
          >
            <b>+</b> Add event
          </div>
          {eventsList?.length >= 1 && eventsList[0].event_key_id && (
            <>
              <div
                className={cx(styles['content'], styles['addConditionStyle'])}
                onClick={handleFindSimilarEventsClick}
              >
                <b>+</b> Find similar events
              </div>
              {similarEventsLoading ? (
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
              <span className={styles['dataCount']}>{searchResponseMessage}</span>
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

export default CreateEntity;
