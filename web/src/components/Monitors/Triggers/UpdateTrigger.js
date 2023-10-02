import { useCallback, useEffect, useState } from 'react';
import API from '../../../API';
import Heading from '../../../components/Heading';
import SelectComponent from '../../SelectComponent';
import ValueComponent from '../../ValueComponent';

import { CircularProgress } from '@mui/material';

import { randomString } from '../../../utils/utils';

import { useNavigate, useParams } from 'react-router-dom';

import Toast from '../.././/Toast';
import useToggle from '../../../hooks/useToggle';

import styles from '../../../css/createTrigger.module.css';

import { mapEventTypeIdToAttrs } from '../../../components/Events/utils';

import AttributesFilter from '../../../pages/Monitor/MonitorTransactionTypeFilter/AttributesFilter';

const UpdateTrigger = () => {
  let { id, t_id } = useParams();

  const monitorId = id;
  const triggerId = t_id;

  const [loading, setLoading] = useState(true);

  const [origTriggerName, setOrigTriggerName] = useState();
  const [triggerName, setTriggerName] = useState();

  const [origTriggerStatus, setOrigTriggerStatus] = useState();
  const [triggerStatus, setTriggerStatus] = useState();

  const [attributeOptions, setAttributeOptions] = useState([]);

  const [attributeList, setAttributeList] = useState([]);
  const [dataFetched, setDataFetched] = useState(false);

  const triggerTypes = [
    { id: '1', label: 'Per Event' },
    { id: '2', label: 'Aggregated Events' }
  ];
  const perEventTriggerTypeHint =
    "Trigger an action whenever the secondary event doesn't happen within your configured delay";
  const aggrEventsTriggerTypeHint =
    "Trigger an action when a % of secondary event don't happen within your configured delay, evaluated periodically";

  const aggreEventsTriggerEventsInclusionOptions = [
    {
      label: 'Missing & Delayed',
      id: 'MISSING_AND_DELAYED_EVENTS'
    },
    {
      label: 'Only Delayed',
      id: 'DELAYED_EVENTS'
    },
    {
      label: 'Only Missing',
      id: 'MISSING_EVENTS'
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

  const equalsOperator = [
    { id: 'EQ', label: '=' },
    { id: 'NEQ', label: '!=' },
    { id: 'IN', label: 'IN' },
    { id: 'NOT_IN', label: 'NOT IN' }
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

  const aggrEventsSelectedEventsInclusionFlag1Hint =
    'Consider for all primary events irrespective of whether their secondary events occur after the delay or do not occur at all';
  const aggrEventsSelectedEventsInclusionFlag2Hint =
    'Consider only those primary events whose secondary events occur after the delay and skip those that do not occur at all';
  const aggrEventsSelectedEventsInclusionFlag3Hint =
    'Consider only those primary events whose secondary events do not occur at all';

  const [selectedTriggerType, setSelectedTriggerType] = useState();
  const [monitorName, setMonitorName] = useState();

  const [triggerTypeDisabled, setTriggerTypeDisabled] = useState(true);
  const [updateDefinition, setUpdateDefinition] = useState(false);
  const [updateNotification, setUpdateNotification] = useState(false);

  const [selectedAlertType, setSelectedAlertType] = useState();
  const [alertEmailDestination, setEmailAlertDestination] = useState();
  const [alertSlackDestination, setSlackAlertDestination] = useState();

  const [origSelectedAlertType, setOrigSelectedAlertType] = useState();
  const [origEmailAlertDestination, setOrigEmailAlertDestination] = useState();
  const [origSlackAlertDestination, setOrigSlackAlertDestination] = useState();

  const [perEventSelectedDelay, setPerEventSelectedDelay] = useState();
  const [aggrEventsSelectedDelay, setAggrEventsSelectedDelay] = useState();
  const [aggrEventsSelectedThreshold, setAggrEventsSelectedThreshold] = useState();
  const [aggrEventsSelectedResolution, setAggrEventsSelectedResolution] = useState();
  const [aggrEventsSelectedEventsInclusionFlag, setAggrEventsSelectedEventsInclusionFlag] =
    useState();

  const [origPerEventSelectedDelay, setOrigPerEventSelectedDelay] = useState();
  const [origAggrEventsSelectedDelay, setOrigAggrEventsSelectedDelay] = useState();
  const [origAggrEventsSelectedThreshold, setOrigAggrEventsSelectedThreshold] = useState();
  const [origAggrEventsSelectedResolution, setOrigAggrEventsSelectedResolution] = useState();
  const [origAggrEventsSelectedEventsInclusionFlag, setOrigAggrEventsSelectedEventsInclusionFlag] =
    useState();

  const [primaryEventId, setPrimaryEventId] = useState();
  const [primaryAttrOptions, setPrimaryAttrOptions] = useState([]);
  const [secondaryEventId, setSecondaryEventId] = useState();
  const [secondaryAttrOptions, setSecondaryAttrOptions] = useState([]);

  const [origPrimaryFilters, setOrigPrimaryFilters] = useState([]);
  const [origSecondaryFilters, setOrigSecondaryFilters] = useState([]);

  const [validationError, setValidationError] = useState();
  const { isOpen, toggle } = useToggle();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState();

  const getTriggerOptions = API.useGetTriggerOptions();
  const fetchMonitors = API.useGetMonitors();
  const createTrigger = API.useCreateTriggers();
  const fetchTriggerById = API.useGetTriggersByTriggerId();
  const updateTriggerData = API.useUpdateTriggers();

  const navigate = useNavigate();

  const getTypeOptions = (options, eventOrderType) => {
    const primaryLabel = options.find(
      option => option.path === 'primary_event_attribute'
    ).path_alias;
    const secondaryLabel = options.find(
      option => option.path === 'secondary_event_attribute'
    ).path_alias;
    return [
      {
        label: primaryLabel,
        id: 'primary_event_attribute'
      },
      {
        label: secondaryLabel,
        id: 'secondary_event_attribute'
      }
    ];
  };

  const getAttrOptions = (options, selectedList) => {
    return options.reduce((acc, option) => {
      if (option.path === selectedList.path) {
        return [
          ...acc,
          {
            label: option.name,
            id: option.name
          }
        ];
      }
      return acc;
    }, []);
  };

  const transformOptions = (options, eventOrderType) => {
    return options.map(option => ({
      name: option?.key,
      event_type_id: option?.event_type?.id,
      event_key_id: option?.id,
      path: eventOrderType === 'primary' ? 'primary_event_attribute' : 'secondary_event_attribute',
      op: option.op || '',
      literal_type: option?.key_type,
      value: option?.value || (option?.id_option?.type.includes('ARRAY') ? [] : ''),
      path_alias: option?.event_type?.name + ' (' + eventOrderType + ' event)',
      typeOptions:
        eventOrderType === 'primary'
          ? {
              label: option?.event_type?.name + ' (' + eventOrderType + ' event)',
              id: 'primary_event_attribute'
            }
          : {
              label: option?.event_type?.name + ' (' + eventOrderType + ' event)',
              id: 'secondary_event_attribute'
            },
      attrOptions: options.map(item => ({ id: item.id, label: item.key }))
    }));
  };

  const populateTriggerData = (p_a_options, s_a_options) => {
    setLoading(true);
    fetchTriggerById(
      t_id,
      {},
      resp => {
        let triggerData = resp.data?.monitor_trigger_notification_details[0];
        setOrigTriggerName(triggerData.trigger.name);
        setTriggerName(triggerData.trigger.name);

        setOrigTriggerStatus(triggerData.trigger.is_active ? 'active' : 'inactive');
        setTriggerStatus(triggerData.trigger.is_active ? 'active' : 'inactive');

        let origAttrList = [];
        let pef = triggerData.trigger.definition.primary_event_filters;
        for (var i = 0; i < pef?.length; i++) {
          let origAttr = {};
          origAttr['id'] = randomString();
          origAttr['event_key_id'] = pef[i].event_key_id;
          origAttr['literal_type'] = pef[i].literal.literal_type;
          origAttr['name'] = p_a_options.find(
            attr => attr.event_key_id === pef[i].event_key_id
          ).name;
          origAttr['op'] = pef[i].op;
          origAttr['path'] = 'primary_event_attribute';
          origAttr['value'] = getValFromLiteral(pef[i].literal);
          origAttr['typeOptions'] = [
            {
              label: p_a_options[0].path_alias,
              id: 'primary_event_attribute'
            },
            {
              label: s_a_options[0].path_alias,
              id: 'secondary_event_attribute'
            }
          ];
          origAttr['operators'] = equalsOperator;
          origAttr['attributeOptions'] = p_a_options[0].attrOptions.map(item => ({
            id: item.label,
            label: item.label
          }));
          origAttrList.push(origAttr);
        }

        let sef = triggerData.trigger.definition.secondary_event_filters;
        for (var i = 0; i < sef?.length; i++) {
          let origAttr = {};
          origAttr['id'] = randomString();
          origAttr['event_key_id'] = sef[i].event_key_id;
          origAttr['literal_type'] = sef[i].literal.literal_type;
          origAttr['name'] = s_a_options.find(
            attr => attr.event_key_id === sef[i].event_key_id
          ).name;
          origAttr['op'] = sef[i].op;
          origAttr['path'] = 'secondary_event_attribute';
          origAttr['value'] = getValFromLiteral(sef[i].literal);
          origAttr['typeOptions'] = [
            {
              label: p_a_options[0].path_alias,
              id: 'primary_event_attribute'
            },
            {
              label: s_a_options[0].path_alias,
              id: 'secondary_event_attribute'
            }
          ];
          origAttr['operators'] = equalsOperator;
          origAttr['attributeOptions'] = s_a_options[0].attrOptions.map(item => ({
            id: item.label,
            label: item.label
          }));
          origAttrList.push(origAttr);
        }
        setAttributeList([...origAttrList]);

        if (triggerData.trigger.definition.type === 'MISSING_EVENT') {
          setSelectedTriggerType('1');

          setOrigPerEventSelectedDelay(
            triggerData.trigger.definition.missing_event_trigger.transaction_time_threshold
          );
          setPerEventSelectedDelay(
            triggerData.trigger.definition.missing_event_trigger.transaction_time_threshold
          );
        } else {
          setSelectedTriggerType('2');

          setAggrEventsSelectedDelay(
            triggerData.trigger.definition.delayed_event_trigger.transaction_time_threshold
          );
          setOrigAggrEventsSelectedDelay(
            triggerData.trigger.definition.delayed_event_trigger.transaction_time_threshold
          );

          setAggrEventsSelectedResolution(
            triggerData.trigger.definition.delayed_event_trigger.resolution / 60
          );
          setOrigAggrEventsSelectedResolution(
            triggerData.trigger.definition.delayed_event_trigger.resolution / 60
          );

          setAggrEventsSelectedThreshold(
            triggerData.trigger.definition.delayed_event_trigger.trigger_threshold
          );
          setOrigAggrEventsSelectedThreshold(
            triggerData.trigger.definition.delayed_event_trigger.trigger_threshold
          );

          setAggrEventsSelectedEventsInclusionFlag(
            triggerData.trigger.definition.delayed_event_trigger.type
          );
          setOrigAggrEventsSelectedEventsInclusionFlag(
            triggerData.trigger.definition.delayed_event_trigger.type
          );
        }

        if (triggerData.notifications && triggerData.notifications.length > 0) {
          if (triggerData.notifications[0].channel === 'SLACK') {
            setSelectedAlertType('SLACK');
            setOrigSelectedAlertType('SLACK');

            setOrigSlackAlertDestination(
              triggerData.notifications[0].slack_configuration.webhook_url
            );
            setSlackAlertDestination(triggerData.notifications[0].slack_configuration.webhook_url);
          } else {
            setSelectedAlertType('EMAIL');
            setOrigSelectedAlertType('EMAIL');

            setOrigEmailAlertDestination(
              triggerData.notifications[0].email_configuration.recipient_email_id
            );
            setEmailAlertDestination(
              triggerData.notifications[0].email_configuration.recipient_email_id
            );
          }
        }

        setDataFetched(true);
      },
      err => {}
    );
  };

  useEffect(() => {
    setAggrEventsSelectedEventsInclusionFlag('MISSING_AND_DELAYED_EVENTS');
    setSelectedAlertType('NO_ALERT');
    setLoading(true);
    fetchMonitors(
      [],
      {},
      null,
      response => {
        let matchedMonitor = response.data?.monitors.filter(monitor => monitor.id === monitorId);
        setMonitorName(matchedMonitor[0].name);

        let p_e_id = matchedMonitor[0].primary_event_key?.event_type?.id;
        setPrimaryEventId(p_e_id);

        let s_e_id = matchedMonitor[0].secondary_event_key?.event_type?.id;
        setSecondaryEventId(s_e_id);

        getTriggerOptions(
          monitorId,
          response => {
            const monitorOptions = response.data?.monitor_trigger_options?.event_key_filter_options;
            let primaryEventAttrOptions = monitorOptions.filter(
              option => option.event_type.id === p_e_id
            );
            let secondaryEventAttrOptions = monitorOptions.filter(
              option => option.event_type.id === s_e_id
            );

            let p_a_options = transformOptions(primaryEventAttrOptions, 'primary');
            setPrimaryAttrOptions(p_a_options);

            let s_a_options = transformOptions(secondaryEventAttrOptions, 'secondary');
            setSecondaryAttrOptions(s_a_options);

            const attributeOptions = [...p_a_options, ...s_a_options];

            setAttributeOptions(attributeOptions);
            populateTriggerData(p_a_options, s_a_options);
            setLoading(false);
          },
          err => {
            console.log(err);
            setLoading(false);
          }
        );
      },
      err => {
        console.log(err);
        setLoading(false);
      }
    );
  }, []);

  const validateTriggerForm = () => {
    if (!triggerName) {
      return 'Enter a trigger name';
    }
    if (selectedTriggerType === '1' && !perEventSelectedDelay) {
      return 'Enter the delay for per event trigger';
    }
    if (
      selectedTriggerType === '2' &&
      (!aggrEventsSelectedDelay || !aggrEventsSelectedThreshold || !aggrEventsSelectedResolution)
    ) {
      return 'Enter the details for the aggregated events trigger';
    }
    return '';
  };

  const getValFromLiteral = option => {
    if (option.literal_type === 'STRING') {
      return option.string;
    }
    if (option.literal_type === 'LONG') {
      return option.long;
    }
    if (option.literal_type === 'DOUBLE') {
      return option.double;
    }
    if (option.literal_type === 'BOOLEAN') {
      return option.boolean;
    }
    if (option.literal_type === 'STRING_ARRAY') {
      return option.string_array.join(',');
    }
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
    if (option.literal_type === 'STRING_ARRAY') {
      return { literal_type: option.literal_type, string_array: option.value };
    }
  };

  const transformFilters = filterList => {
    let resultFilters = [];

    for (let i = 0; i < filterList.length; i++) {
      let filter = {};
      filter['op'] = filterList[i]?.op;
      filter['literal'] = getLiteralVal(filterList[i]);
      filter['event_key_id'] =
        filterList[i].path === 'primary_event_attribute'
          ? primaryAttrOptions.filter(option => option.name === filterList[i]?.name)[0].event_key_id
          : secondaryAttrOptions.filter(option => option.name === filterList[i]?.name)[0]
              .event_key_id;
      resultFilters.push(filter);
    }
    return resultFilters;
  };

  const handleSubmitUpdate = () => {
    let primary_event_filters = transformFilters(
      attributeList?.filter(item => item.path === 'primary_event_attribute')
    );

    let secondary_event_filters = transformFilters(
      attributeList?.filter(item => item.path === 'secondary_event_attribute')
    );

    let formValidationError = validateTriggerForm();

    if (formValidationError) {
      toggleError();
      setSubmitError(formValidationError);
      return;
    }

    let update_trigger_ops = [];

    if (triggerName !== origTriggerName) {
      update_trigger_ops.push({
        op: 'UPDATE_TRIGGER_NAME',
        update_trigger_name: {
          name: triggerName
        }
      });
    }

    if (triggerStatus !== origTriggerStatus) {
      update_trigger_ops.push({
        op: 'UPDATE_TRIGGER_STATUS',
        update_trigger_status: {
          is_active: triggerStatus == 'active' ? true : false
        }
      });
    }

    if (updateDefinition) {
      let definition = {};

      if (selectedTriggerType === '1') {
        definition = {
          type: 'MISSING_EVENT',
          missing_event_trigger: {
            transaction_time_threshold: perEventSelectedDelay
          },
          secondary_event_filters: secondary_event_filters,
          primary_event_filters: primary_event_filters
        };
      } else if (selectedTriggerType === '2') {
        definition = {
          type: 'DELAYED_EVENT',
          delayed_event_trigger: {
            transaction_time_threshold: aggrEventsSelectedDelay,
            resolution: aggrEventsSelectedResolution * 60,
            trigger_threshold: aggrEventsSelectedThreshold,
            type: aggrEventsSelectedEventsInclusionFlag
          },
          secondary_event_filters: secondary_event_filters,
          primary_event_filters: primary_event_filters
        };
      }

      if (definition) {
        update_trigger_ops.push({
          op: 'UPDATE_TRIGGER_DEFINITION',
          update_trigger_definition: {
            definition: definition
          }
        });
      }
    }

    if (updateNotification) {
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

      if (notifications) {
        update_trigger_ops.push({
          op: 'UPDATE_TRIGGER_NOTIFICATIONS',
          update_trigger_notifications: {
            notifications: notifications
          }
        });
      }
    }

    const payload = {
      trigger_id: t_id,
      update_trigger_ops: update_trigger_ops
    };

    setLoading(true);
    updateTriggerData(
      payload,
      response => {
        if (response.data.success) {
          navigate('/monitors/' + monitorId);
          window?.analytics?.track('Trigger Updated');
        }
        setLoading(false);
      },
      err => {
        console.log(err.err);
        toggleError();
        setSubmitError(err.err);
        setLoading(false);
        return;
      }
    );
  };

  const handleAttributeListChange = list => {
    setAttributeList([...list]);
    setUpdateDefinition(true);
  };

  const handleTriggerNameChange = val => {
    setTriggerName(val);
  };

  const handlePerEventSelectedDelayChange = val => {
    setPerEventSelectedDelay(val);
    if (val !== origPerEventSelectedDelay) {
      setUpdateDefinition(true);
    }
  };

  const handleAggrEventsSelectedDelayChange = val => {
    setAggrEventsSelectedDelay(val);
    if (val !== origAggrEventsSelectedDelay) {
      setUpdateDefinition(true);
    }
  };

  const handleAggrEventsSelectedThresholdChange = val => {
    setAggrEventsSelectedThreshold(val);
    if (val !== origAggrEventsSelectedThreshold) {
      setUpdateDefinition(true);
    }
  };

  const handleAggrEventsSelectedResolutionChange = val => {
    setAggrEventsSelectedResolution(val);
    if (val !== origAggrEventsSelectedResolution) {
      setUpdateDefinition(true);
    }
  };

  const handleTriggerTypeChange = id => {
    setSelectedTriggerType(id);
  };

  const handleAggrEventsSelectedEventsInclusionFlagChange = val => {
    setAggrEventsSelectedEventsInclusionFlag(val);
    if (val !== origAggrEventsSelectedEventsInclusionFlag) {
      setUpdateDefinition(true);
    }
  };

  const handleAlertTypeChange = id => {
    setSelectedAlertType(id);
    if (id !== origSelectedAlertType) {
      setUpdateNotification(true);
    }
  };

  const handleEmailAlertDestinationChange = val => {
    setEmailAlertDestination(val);
    if (val !== origEmailAlertDestination) {
      setUpdateNotification(true);
    }
  };

  const handleSlackAlertDestinationChange = val => {
    setSlackAlertDestination(val);
    if (val !== origSlackAlertDestination) {
      setUpdateNotification(true);
    }
  };

  const handleTriggerStatusChange = id => {
    setTriggerStatus(id);
  };

  return (
    <>
      <Heading
        heading={'Update Trigger / ' + origTriggerName}
        onTimeRangeChangeCb={false}
        onRefreshCb={false}
      />
      <div className={styles['container']}>
        <div className={styles['heading']}>
          <div className={styles['content']}>Monitor</div>
          <div className={styles['content']}>
            <b>
              <a href={`/monitors/${monitorId}`}>{monitorName}</a>
            </b>
          </div>
        </div>
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
          <div className={styles['content']}>Trigger Status</div>

          <SelectComponent
            data={statusOptions}
            onSelectionChange={handleTriggerStatusChange}
            selected={triggerStatus}
          />
        </div>
      </div>

      <div className={styles['container']}>
        <div className={styles['heading']}>
          Rules
          <div className={styles['subHeading']}>Set conditions for the trigger</div>
        </div>

        <div>
          <div className={styles['eventTypeSelectionSection']}>
            <div className={styles['content']}>Trigger Type</div>
            <SelectComponent
              data={triggerTypes}
              placeholder="Select Trigger Type"
              onSelectionChange={handleTriggerTypeChange}
              selected={selectedTriggerType}
              disabled={triggerTypeDisabled}
            />
            <div className={styles['subHeading']}>
              {selectedTriggerType === '1' ? perEventTriggerTypeHint : ''}
            </div>
            <div className={styles['subHeading']}>
              {selectedTriggerType === '2' ? aggrEventsTriggerTypeHint : ''}
            </div>
          </div>

          {selectedTriggerType === '1' && (
            <>
              <div className={styles['eventTypeSelectionSection']}>
                <div className={styles['content']}>Delay (seconds)</div>
                <ValueComponent
                  valueType={'DOUBLE'}
                  onValueChange={handlePerEventSelectedDelayChange}
                  value={perEventSelectedDelay}
                  placeHolder={' '}
                />
              </div>
            </>
          )}

          {selectedTriggerType === '2' && (
            <>
              <div className={styles['eventTypeSelectionSection']}>
                <div className={styles['content']}>Events Included</div>
                <SelectComponent
                  data={aggreEventsTriggerEventsInclusionOptions}
                  placeholder="Select Events Included"
                  onSelectionChange={handleAggrEventsSelectedEventsInclusionFlagChange}
                  selected={aggrEventsSelectedEventsInclusionFlag}
                />
                <div className={styles['subHeading']}>
                  {aggrEventsSelectedEventsInclusionFlag === 'MISSING_AND_DELAYED_EVENTS'
                    ? aggrEventsSelectedEventsInclusionFlag1Hint
                    : ''}
                </div>
                <div className={styles['subHeading']}>
                  {aggrEventsSelectedEventsInclusionFlag === 'DELAYED_EVENTS'
                    ? aggrEventsSelectedEventsInclusionFlag2Hint
                    : ''}
                </div>
                <div className={styles['subHeading']}>
                  {aggrEventsSelectedEventsInclusionFlag === 'MISSING_EVENTS'
                    ? aggrEventsSelectedEventsInclusionFlag3Hint
                    : ''}
                </div>
              </div>

              <div className={styles['eventTypeSelectionSection']}>
                <div className={styles['content']}>Threshold (%)</div>
                <ValueComponent
                  valueType={'DOUBLE'}
                  onValueChange={handleAggrEventsSelectedThresholdChange}
                  value={aggrEventsSelectedThreshold}
                  placeHolder={' '}
                />
                <div className={styles[('content', 'right')]}>Delay (seconds)</div>
                <ValueComponent
                  valueType={'DOUBLE'}
                  onValueChange={handleAggrEventsSelectedDelayChange}
                  value={aggrEventsSelectedDelay}
                  placeHolder={' '}
                />

                <div className={styles[('content', 'right')]}>Evaluation Period (minutes)</div>
                <ValueComponent
                  valueType={'DOUBLE'}
                  onValueChange={handleAggrEventsSelectedResolutionChange}
                  value={aggrEventsSelectedResolution}
                  placeHolder={' '}
                />
              </div>
            </>
          )}
        </div>
      </div>

      <div className={styles['container']}>
        <div className={styles['heading']}>
          Filters
          <div className={styles['subHeading']}>
            Add filters from either of the events in the monitor
          </div>
        </div>

        {dataFetched && (
          <AttributesFilter
            options={attributeOptions}
            list={attributeList}
            onListChange={handleAttributeListChange}
            fixedOperators={equalsOperator}
          />
        )}
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
              placeHolder={'Enter slack webhook URL'}
            />
          )}
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

export default UpdateTrigger;
