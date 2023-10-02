import { useCallback, useEffect, useState } from 'react';
import API from '../../../API';
import Heading from '../../../components/Heading';
import SelectComponent from '../../SelectComponent';
import ValueComponent from '../../ValueComponent';

import FilterComponent from '../../FilterComponent';

import { CircularProgress } from '@mui/material';

import useNode from '../../../hooks/useNode.ts';
import { transformEventQueryOptionsToSelectOptions } from '../../Events/utils';
import {
  transformToAPIPayload,
  transformToQueryBuilderPayload,
  getQueryBuilderPayloadFilters
} from '../../../utils/utils.js';

import { useNavigate, useParams } from 'react-router-dom';

import Toast from '../.././/Toast';
import useToggle from '../../../hooks/useToggle';

import styles from '../../../css/createTrigger.module.css';

const transformOptions = options => {
  return options.map(option => ({
    name: option?.key,
    event_type_id: option?.event_type?.id,
    event_key_id: option?.id,
    path: 'event_attribute',
    op: option.op || '',
    literal_type: option?.key_type,
    type: option?.key_type,
    value: option?.value || (option?.id_option?.type.includes('ARRAY') ? [] : ''),
    path_alias: option?.event_type?.name
  }));
};

function getUniqueList(list, property) {
  const uniqueList = [];
  const seen = {};

  for (const item of list) {
    const key = item[property];
    if (!seen[key]) {
      seen[key] = true;
      uniqueList.push(item);
    }
  }
  return uniqueList;
}

const CreateTrigger = () => {
  let { id, t_id } = useParams();

  const entityId = id;
  const entityTriggerId = t_id;

  const [triggerName, setTriggerName] = useState();
  const [origTriggerData, setOrigTriggerData] = useState();

  const [triggerStatus, setTriggerStatus] = useState();

  const [dataFetched, setDataFetched] = useState(false);

  const [loading, setLoading] = useState();

  const [triggerEventOptions, setTriggerEventOptions] = useState([]);
  const [triggerEvent, setTriggerEvent] = useState();

  const { insertNode, deleteNode, updateNode } = useNode();

  const [queryBuilderPayload, setQueryBuilderPayload] = useState({
    op: 'AND',
    filters: []
  });

  const [eventQueryOptions, setEventQueryOptions] = useState();

  const triggerTypes = [
    { id: '1', label: 'Per Entity' }
    // { id: '2', label: 'Aggregated' }
  ];
  const perEntityTriggerTypeHint =
    'Trigger an action for every entity instance that satisfies the rule';
  const aggrEntityTriggerTypeHint =
    'Trigger an action when a % of entity instances satisfy a rule, evaluated periodically';

  const triggerRuleOptions = [
    {
      label: 'Last Event',
      id: 'LAST_EVENT'
    },
    {
      label: 'Event Count',
      id: 'EVENT_COUNT'
    },
    {
      label: 'Event Occurence',
      id: 'EVENT_OCCURS'
    }
  ];

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

  const alertOptions = [
    {
      label: 'SLACK',
      id: 'SLACK'
    },
    {
      label: 'EMAIL',
      id: 'EMAIL'
    },
    {
      label: 'No Alert',
      id: 'NO_ALERT'
    }
  ];

  const triggerRule1Hint =
    'Trigger action if entity is stuck at the configured event for longer than the configured time interval';
  const triggerRule2Hint =
    'Trigger action if the configured event occurs more than the configured count in the configured time interval';
  const triggerRule3Hint = 'Trigger action whenever the configured event occurs';

  const [selectedTriggerType, setSelectedTriggerType] = useState('1');
  const [entityName, setEntityName] = useState();

  const [selectedAlertType, setSelectedAlertType] = useState();
  const [alertEmailDestination, setEmailAlertDestination] = useState();
  const [alertSlackDestination, setSlackAlertDestination] = useState();

  const [timeInterval, setTimeInterval] = useState();
  const [thresholdCount, setThresholdCount] = useState();

  const [triggerRule, setTriggerRule] = useState();

  const [validationError, setValidationError] = useState();
  const { isOpen, toggle } = useToggle();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState();

  const updateTrigger = API.useUpdateEntityTriggers();
  const getTriggerOptions = API.useGetEntityTriggerOptions();
  const fetchTriggers = API.useGetEntityTriggersByTriggerId();

  const navigate = useNavigate();

  const fetchTriggerData = transformedOptions => {
    if (!dataFetched) {
      setLoading(true);
      fetchTriggers(
        entityId,
        entityTriggerId,
        {},
        resp => {
          setOrigTriggerData(resp.data?.entity_trigger_notification_details);
          let trigger_notif_obj = resp.data?.entity_trigger_notification_details[0];
          setTriggerName(trigger_notif_obj.trigger.name);
          setEntityName(trigger_notif_obj.trigger.entity_name);
          setTriggerRule(trigger_notif_obj.trigger.definition.rule_type);
          setTriggerEvent(trigger_notif_obj.trigger.definition.trigger_rule_config.event_id);
          setTimeInterval(trigger_notif_obj.trigger.definition.trigger_rule_config.time_interval);
          setThresholdCount(
            trigger_notif_obj.trigger.definition.trigger_rule_config.threshold_count
          );
          setTriggerStatus(trigger_notif_obj.trigger.is_active ? 'active' : 'inactive');

          if (trigger_notif_obj.notifications && trigger_notif_obj.notifications.length > 0) {
            if (trigger_notif_obj.notifications[0].channel === 'SLACK') {
              setSelectedAlertType('SLACK');
              setSlackAlertDestination(
                trigger_notif_obj.notifications[0].slack_configuration.webhook_url
              );
            } else {
              setSelectedAlertType('EMAIL');
              setEmailAlertDestination(
                trigger_notif_obj.notifications[0].email_configuration.recipient_email_id
              );
            }
          }

          setQueryBuilderPayload(
            transformToQueryBuilderPayload(
              { filter: trigger_notif_obj.trigger.filter },
              transformedOptions
            )
          );

          setDataFetched(true);
          setLoading(false);
        },
        err => {
          setDataFetched(true);
          setLoading(false);
        }
      );
    }
  };

  useEffect(() => {
    setSelectedAlertType('NO_ALERT');
    setLoading(true);
    getTriggerOptions(
      id,
      response => {
        const eventTypeList = response.data?.event_key_options.map(item => ({
          label: item.event_type.name,
          id: item.event_type.id
        }));
        setTriggerEventOptions(getUniqueList(eventTypeList, 'id'));

        const triggerOptions = response.data?.event_key_options;
        const transformedOptions = transformEventQueryOptionsToSelectOptions({
          column_options: [],
          attribute_options: transformOptions(triggerOptions)
        });
        const transformedPayload = transformToQueryBuilderPayload(
          { filter: { filters: [], op: 'AND' } },
          transformedOptions
        );
        setQueryBuilderPayload(transformedPayload);
        setEventQueryOptions(transformedOptions);
        fetchTriggerData(transformedOptions);
      },
      err => {
        console.error(err);
        setLoading(false);
      }
    );
  }, []);

  const validateTriggerForm = () => {
    if (!triggerName) {
      return 'Enter a trigger name';
    }

    if (!triggerEvent) {
      return 'Select a trigger event';
    }

    if (triggerRule != 'EVENT_OCCURS' && !timeInterval) {
      return 'Enter the time interval delay for the trigger rule';
    }

    if (triggerRule == 'EVENT_COUNT' && !thresholdCount) {
      return 'Enter the threshold count for the trigger rule';
    }

    return '';
  };

  const getLiteralVal = option => {
    if (option.literal_type === 'STRING') {
      return { literal_type: option.literal_type, string: option.value };
    }
    if (option.literal_type === 'LONG') {
      return { literal_type: option.literal_type, long: option.value };
    }
    if (option.literal_type === 'DOUBLE') {
      return { literal_type: option.literal_type, double: option.value };
    }
    if (option.literal_type === 'BOOLEAN') {
      return { literal_type: option.literal_type, boolean: option.value };
    }
  };

  const handleSubmitUpdate = () => {
    let formValidationError = validateTriggerForm();
    if (formValidationError) {
      toggleError();
      setSubmitError(formValidationError);
      return;
    }

    const queryAPIPayload = transformToAPIPayload(queryBuilderPayload);

    let trigger = {};
    if (selectedTriggerType === '1') {
      trigger = {
        id: entityTriggerId,
        name: triggerName,
        is_active: triggerStatus == 'active' ? true : false,
        entity_id: entityId,
        definition: {
          type: selectedTriggerType,
          rule_type: triggerRule,
          trigger_rule_config: {
            event_id: triggerEvent,
            event_name: triggerEventOptions.find(item => item.id === triggerEvent)?.label,
            time_interval: timeInterval,
            threshold_count: thresholdCount
          }
        },
        filter: queryAPIPayload.filter
      };
    } else {
      toggleError();
      setSubmitError('Something went wrong');
      return;
    }

    let notifications = [];
    if (selectedAlertType === 'EMAIL') {
      let notification = {
        channel: 'EMAIL',
        email_configuration: {
          recipient_email_id: alertEmailDestination
        }
      };
      notifications.push(notification);
    } else if (selectedAlertType === 'SLACK') {
      let notification = {
        channel: 'SLACK',
        slack_configuration: {
          webhook_url: alertSlackDestination
        }
      };
      notifications.push(notification);
    }

    const payload = {
      trigger: trigger,
      notifications: notifications
    };

    setLoading(true);
    updateTrigger(
      payload,
      response => {
        setLoading(false);
        if (response.data.message.title == 'Trigger Updated') {
          navigate('/entity/' + entityId);
          window?.analytics?.track('Entity Trigger Updated');
        }
      },
      err => {
        setLoading(false);
        toggleError();
        setSubmitError(err.err);
        return;
      }
    );
  };

  const handleAdd = ({ id, isGroup }) => {
    const tree = insertNode({
      tree: queryBuilderPayload,
      id: id,
      isGroup: isGroup
    });
    setQueryBuilderPayload({ ...tree });
  };

  const handleUpdate = ({ id, type, value, isGroup }) => {
    const tree = updateNode({ tree: queryBuilderPayload, id, value, type, isGroup });
    setQueryBuilderPayload({ ...tree });
  };

  const handleDelete = ({ id, isGroup }) => {
    const tree = deleteNode({
      tree: queryBuilderPayload,
      id,
      isGroup
    });
    setQueryBuilderPayload({ ...tree });
  };

  const handleThresholdCountChange = val => {
    setThresholdCount(val);
  };

  const handleTimeIntervalChange = val => {
    setTimeInterval(val);
  };

  const handleTriggerNameChange = val => {
    setTriggerName(val);
  };

  const handleTriggerTypeChange = id => {
    setSelectedTriggerType(id);
  };

  const handleTriggerRuleChange = val => {
    setTriggerRule(val);
  };

  const handleTriggerEventChange = val => {
    setTriggerEvent(val);
  };

  const handleAlertTypeChange = id => {
    setSelectedAlertType(id);
  };

  const handleEmailAlertDestinationChange = val => {
    setEmailAlertDestination(val);
  };

  const handleSlackAlertDestinationChange = val => {
    setSlackAlertDestination(val);
  };

  const handleTriggerStatusChange = id => {
    setTriggerStatus(id);
  };

  return (
    <>
      <Heading
        heading={'Update Trigger / ' + triggerName}
        onTimeRangeChangeCb={false}
        onRefreshCb={false}
      />
      <div className={styles['container']}>
        <div className={styles['heading']}>
          <div className={styles['content']}>Trigger Name</div>
          <ValueComponent
            valueType={'STRING'}
            onValueChange={handleTriggerNameChange}
            value={triggerName}
            placeHolder={'Enter trigger name'}
          />
        </div>
        <div className={styles['heading']}>
          <div className={styles['content']}>Entity</div>
          <div className={styles['content']}>
            <b>{entityName}</b>
          </div>
        </div>

        <div className={styles['heading']}>
          <div className={styles['content']}>Trigger Status</div>

          <SelectComponent
            data={statusOptions}
            onSelectionChange={handleTriggerStatusChange}
            selected={triggerStatus}
            placeholder={'Select Status'}
          />
        </div>
      </div>

      <div className={styles['container']}>
        <div className={styles['heading']}>
          Rules
          <div className={styles['subHeading']}>Set conditions for the trigger</div>
        </div>

        <div>
          {/* <div className={styles['eventTypeSelectionSection']}>
            <div className={styles['content']}>Trigger Type</div>
            <SelectComponent
              data={triggerTypes}
              placeholder="Select Trigger Type"
              onSelectionChange={handleTriggerTypeChange}
              selected={selectedTriggerType}
            />
            <div className={styles['subHeading']}>
              {selectedTriggerType === '1' ? perEntityTriggerTypeHint : ''}
            </div>
            <div className={styles['subHeading']}>
              {selectedTriggerType === '2' ? aggrEntityTriggerTypeHint : ''}
            </div>
          </div> */}

          {selectedTriggerType && (
            <>
              <div className={styles['eventTypeSelectionSection']}>
                <div className={styles['content']}>Trigger Rule</div>
                <SelectComponent
                  data={triggerRuleOptions}
                  placeholder="Select Rule"
                  onSelectionChange={handleTriggerRuleChange}
                  selected={triggerRule}
                />
                <div className={styles['subHeading']}>
                  {triggerRule === 'LAST_EVENT' ? triggerRule1Hint : ''}
                </div>
                <div className={styles['subHeading']}>
                  {triggerRule === 'EVENT_COUNT' ? triggerRule2Hint : ''}
                </div>
                <div className={styles['subHeading']}>
                  {triggerRule === 'EVENT_OCCURS' ? triggerRule3Hint : ''}
                </div>
              </div>

              <div className={styles['eventTypeSelectionSection']}>
                <div className={styles['content']}>Trigger Event</div>
                <SelectComponent
                  data={triggerEventOptions}
                  placeholder="Select Event"
                  onSelectionChange={handleTriggerEventChange}
                  selected={triggerEvent}
                  searchable={true}
                />

                {triggerRule && ['EVENT_COUNT', 'LAST_EVENT'].indexOf(triggerRule) > -1 && (
                  <>
                    <div className={styles[('content', 'right')]}>Time interval (seconds)</div>
                    <ValueComponent
                      valueType={'LONG'}
                      onValueChange={handleTimeIntervalChange}
                      value={timeInterval}
                      placeHolder={' '}
                    />
                  </>
                )}

                {triggerRule && triggerRule == 'EVENT_COUNT' && (
                  <>
                    <div className={styles['content']}>Threshold Count</div>
                    <ValueComponent
                      valueType={'LONG'}
                      onValueChange={handleThresholdCountChange}
                      value={thresholdCount}
                      placeHolder={' '}
                    />
                  </>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      <div className={styles['container']}>
        <div className={styles['heading']}>
          Filters
          <div className={styles['subHeading']}>
            Add filters from any of the events in the entity
          </div>
        </div>

        <FilterComponent
          filter={queryBuilderPayload}
          options={eventQueryOptions}
          onAdd={handleAdd}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
          isGroupEnabled={false}
        />
      </div>

      <div className={styles['container']}>
        <div className={styles['heading']}>
          Actions
          <div className={styles['subHeading']}>Setup alerts for the trigger</div>
        </div>

        <div className={styles['heading']}>
          <div className={styles['content']}>Alert</div>
          <SelectComponent
            data={alertOptions}
            placeholder="Select Alert Type"
            onSelectionChange={handleAlertTypeChange}
            selected={selectedAlertType}
          />
          {selectedAlertType === 'EMAIL' && (
            <ValueComponent
              valueType={'STRING'}
              onValueChange={handleEmailAlertDestinationChange}
              value={alertEmailDestination}
              placeHolder={'Enter email'}
            />
          )}
          {selectedAlertType === 'SLACK' && (
            <ValueComponent
              valueType={'STRING'}
              onValueChange={handleSlackAlertDestinationChange}
              value={alertSlackDestination}
              length={600}
              placeHolder={'Enter slack webhook url'}
            />
          )}
        </div>
      </div>

      <div className={styles['eventTypeSelectionSection']}>
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

        {loading ? (
          <CircularProgress
            style={{
              marginLeft: '5px'
            }}
            size={20}
          />
        ) : (
          ''
        )}
      </div>

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

export default CreateTrigger;
