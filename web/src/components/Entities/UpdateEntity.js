import { useCallback, useEffect, useState } from 'react';
import API from '../../API';
import Heading from '../../components/Heading';

import SelectComponent from '../SelectComponent';
import ValueComponent from '../ValueComponent';
import cx from 'classnames';
import cross from '../../data/cross.svg';

import { randomString } from '../../utils/utils';

import { useNavigate, useParams } from 'react-router-dom';

import Toast from '../../components/Toast';
import useToggle from '../../hooks/useToggle';

import { groupedData3 } from '../../utils/CreateMonitor';

import styles from '../../css/createMonitor.module.css';

const UpdateEntity = () => {
  const { id } = useParams();

  const [dataFetched, setDataFetched] = useState(false);

  const [eventTypeOptions, setEventTypeOptions] = useState();
  const [eventTypeAttrOptions, setEventTypeAttrOptions] = useState([]);

  const [origEntityName, setOrigEntityName] = useState();
  const [entityName, setEntityName] = useState();

  const [origEntityStatus, setOrigEntityStatus] = useState();
  const [entityStatus, setEntityStatus] = useState();

  const [origEventsList, setOrigEventsList] = useState([]);
  const [eventsList, setEventsList] = useState([]);

  const [updateDefinition, setUpdateDefinition] = useState(false);

  const [validationError, setValidationError] = useState();
  const { isOpen, toggle } = useToggle();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState();

  const getEntityOptions = API.useEntityCreateOptions();
  const getEntityDetails = API.useGetEntityDetails();
  const updateEntityData = API.useUpdateEntity();

  const statusOptions = [
    {
      label: 'Active',
      id: 'active'
    },
    {
      label: 'Inactive',
      id: 'inactive'
    }
  ];

  const navigate = useNavigate();

  const populateOrigEntity = (entity, eventTypeOptions, eventAttrOptions, eventKeyOptions) => {
    setOrigEntityName(entity.entity.name);
    setEntityName(entity.entity.name);

    setOrigEntityStatus(entity.entity.is_active ? 'active' : 'inactive');
    setEntityStatus(entity.entity.is_active ? 'active' : 'inactive');

    let entity_event_key_mappings = entity.entity_event_key_mappings;

    let transformedEventsList = [];
    let transformedOrigEventsList = [];

    for (let i = 0; i < entity_event_key_mappings.length; i++) {
      let transformedEvent = {};
      transformedEvent['mapping_id'] = entity_event_key_mappings[i].id;
      transformedEvent['event_key_id'] = entity_event_key_mappings[i].event_key.id;

      let event_type_id = eventKeyOptions.find(
        item => item.id == entity_event_key_mappings[i].event_key.id
      ).event_type.id;

      transformedEvent['event_type_id'] = event_type_id;

      const options =
        eventAttrOptions[event_type_id]?.map(option => ({
          id: option?.id,
          label: option?.name,
          type: option?.type
        })) || [];

      transformedEvent['event_attribution_options'] = options;
      transformedEvent['id'] = randomString();
      transformedEventsList.push(transformedEvent);
      transformedOrigEventsList.push(transformedEvent);
    }

    setOrigEventsList(transformedOrigEventsList);
    setEventsList(transformedEventsList);
  };

  useEffect(() => {
    getEntityOptions(
      res => {
        let entityOptions = groupedData3(res);
        let eventKeyOptions = res.data.entity_options.event_key_options;

        let c = entityOptions[0];
        setEventTypeOptions(c);
        let d = entityOptions[1];
        setEventTypeAttrOptions(d);

        getEntityDetails(
          id,
          {},
          res => {
            let entity = res.data.entity;
            populateOrigEntity(entity, c, d, eventKeyOptions);
            setDataFetched(true);
          },
          err => {
            console.error(err);
          }
        );
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
    setUpdateDefinition(true);
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
    setUpdateDefinition(true);
  };

  const handleAddEventClick = () => {
    setEventsList([...eventsList, { event_type_id: null, event_key_id: null, id: randomString() }]);
    setUpdateDefinition(true);
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

  const handleSubmitUpdate = () => {
    let formValidationError = validateEntityForm();
    if (formValidationError) {
      toggleError();
      setSubmitError(formValidationError);
      return;
    }

    let update_entity_ops = [];

    if (origEntityName != entityName) {
      update_entity_ops.push({
        op: 'UPDATE_ENTITY_NAME',
        update_entity_name: {
          name: entityName
        }
      });
    }

    if (origEntityStatus != entityStatus) {
      update_entity_ops.push({
        op: 'UPDATE_ENTITY_STATUS',
        update_entity_status: {
          is_active: entityStatus == 'active' ? true : false
        }
      });
    }

    if (updateDefinition) {
      let originalKeyList = origEventsList.map(item => item.event_key_id);
      let updatedKeyList = eventsList.map(item => item.event_key_id);

      let addedKeys = [];
      let removedKeys = [];

      for (let i = 0; i < updatedKeyList.length; i++) {
        if (originalKeyList.indexOf(updatedKeyList[i]) == -1) {
          addedKeys.push(updatedKeyList[i]);
        }
      }

      for (let i = 0; i < originalKeyList.length; i++) {
        if (updatedKeyList.indexOf(originalKeyList[i]) == -1) {
          removedKeys.push(originalKeyList[i]);
        }
      }

      if (addedKeys.length) {
        update_entity_ops.push({
          op: 'ADD_ENTITY_EVENT_KEY_MAPPINGS',
          add_entity_event_key_mappings: {
            event_key_ids: addedKeys
          }
        });
      }

      if (removedKeys.length) {
        update_entity_ops.push({
          op: 'REMOVE_ENTITY_EVENT_KEY_MAPPINGS',
          remove_entity_event_key_mappings: {
            entity_event_key_mapping_ids: origEventsList
              .filter(item => removedKeys.indexOf(item.event_key_id) >= 0)
              .map(item => item.mapping_id)
          }
        });
      }
    }

    const payload = {
      entity_id: id,
      update_entity_ops: update_entity_ops
    };

    updateEntityData(
      payload,
      response => {
        if (response.data.success) {
          navigate('/entities');
          window?.analytics?.track('Entity Updated');
        }
      },
      err => {
        console.log(err.err);
        toggleError();
        setSubmitError(err.err);
        return;
      }
    );
  };

  const handleRemove = id => {
    const updatedList = eventsList.filter(item => item.id !== id);
    setEventsList([...updatedList]);
    setUpdateDefinition(true);
  };

  const handleEntityNameChange = val => {
    setEntityName(val);
  };

  const handleEntityStatusChange = id => {
    setEntityStatus(id);
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
      <Heading
        heading={'Update Entity / ' + origEntityName}
        onTimeRangeChangeCb={false}
        onRefreshCb={false}
      />
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
        <div className={styles['heading']}>
          <div className={styles['content']}>Entity Status</div>

          <SelectComponent
            data={statusOptions}
            onSelectionChange={handleEntityStatusChange}
            selected={entityStatus}
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
        {dataFetched && eventsList?.length >= 1 && renderAttributeList(eventsList)}
        <div
          className={cx(styles['content'], styles['addConditionStyle'])}
          onClick={handleAddEventClick}
        >
          <b>+</b> Add event
        </div>
      </div>
      <button
        className="text-xs bg-white hover:bg-violet-500 hover:color-white-500 py-1 px-1 border border-gray-400 rounded shadow"
        onClick={handleSubmitUpdate}
        style={{
          marginLeft: '12px',
          marginBottom: '12px'
        }}
      >
        Update
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

export default UpdateEntity;
