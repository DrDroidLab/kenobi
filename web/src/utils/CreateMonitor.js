export const groupedData = response => {
  const responseEventsData = response?.data?.monitor_options?.event_key_options;
  const responseNotificationsData = response?.data?.monitor_options?.notification_options;
  const responseTriggersData = response?.data.monitor_options?.trigger_options;
  const responseEventTriggerFilter =
    response?.data?.monitor_options?.event_trigger_filter_key_options;

  return {
    eventTypeMap: groupEventTypesById(responseEventsData),
    eventTriggerFilterMap: groupEventTypesById(responseEventTriggerFilter),
    notificationMap: getNotificationHashMap(responseNotificationsData),
    triggerMap: responseTriggersData
  };
};

export const groupedData2 = response => {
  const responseEventsData = response?.data?.monitor_options?.event_key_options;
  return groupEventTypesList(responseEventsData);
};

export const groupedData3 = response => {
  const responseEventsData = response?.data?.entity_options?.event_key_options;
  return groupEventTypesList(responseEventsData);
};

export const getKeyNames = response => {
  const responseEventsData = response?.data?.entity_options?.event_key_options;
  const keyList = responseEventsData.map(x => x.key);
  return new Set(keyList);
};

const groupEventTypesList = responseEventsData => {
  const eventTypeList = [];
  const eventTypeNames = [];
  const eventTypeMap = {};

  if (!responseEventsData) {
    return eventTypeList;
  }

  for (let i = 0; i < responseEventsData.length; i++) {
    const { id, key: name, key_type: type, event_type } = responseEventsData[i];
    const { id: e_id, name: eventTypeName } = event_type;

    if (!eventTypeMap[e_id]) {
      eventTypeMap[e_id] = [];
    }

    eventTypeMap[e_id].push({
      name: name,
      id: id,
      type: type
    });

    if (!eventTypeNames.includes(eventTypeName)) {
      eventTypeList.push({ id: e_id, label: eventTypeName });
      eventTypeNames.push(eventTypeName);
    }
  }

  return [eventTypeList, eventTypeMap];
};

const groupEventTypesById = responseEventsData => {
  const eventTypeMap = {};

  if (!responseEventsData) {
    return eventTypeMap;
  }

  responseEventsData.forEach(option => {
    const { id, key, key_type, event_type } = option;
    const { name: eventTypeName } = event_type;

    if (!eventTypeMap[eventTypeName]) {
      eventTypeMap[eventTypeName] = [];
    }

    eventTypeMap[eventTypeName].push({
      key,
      id,
      key_type
    });
  });

  return eventTypeMap;
};

const getNotificationHashMap = responseNotificationsData => {
  const notificationHashMap = {};

  if (!responseNotificationsData) {
    return notificationHashMap;
  }

  responseNotificationsData.forEach(option => {
    const { channel } = option;
    const values = {};

    if (option.slack_configuration) {
      values.webhook_url = option.slack_configuration.webhook_url;
    }

    if (option.email_configuration) {
      values.email_address = option.email_configuration.recipient_email_id;
    }

    notificationHashMap[channel] = values;
  });

  return notificationHashMap;
};

export const getInputKeyType = (data, inputFilter) => {
  return data?.eventTypeMap[inputFilter?.event_type].find(
    eventType => eventType?.id === inputFilter?.event_key_id
  )?.key_type;
};

export const getInputKeyFilterType = (data, inputFilter) => {
  return data?.eventTriggerFilterMap[inputFilter?.event_type].find(
    eventType => eventType?.id === inputFilter?.event_key_id
  )?.key_type;
};

export const InputTyepMap = {
  STRING: 'text',
  LONG: 'number',
  DOUBLE: 'number',
  BOOLEAN: 'boolean'
};

export const LiteralMap = {
  STRING: 'string',
  LONG: 'long',
  DOUBLE: 'double',
  BOOLEAN: 'boolean'
};
