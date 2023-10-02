export const getEventTypeOptionsPayload = columns => {
  const eventTypeColumn = columns.find(column => column?.name === 'event_type_id');
  const optionsMap = eventTypeColumn?.id_option?.long_options;
  return Object.entries(optionsMap)?.map(option => ({
    id: option[0],
    label: option[1]
  }));
};

export const mapEventTypeIdToAttrs = attributeOptions => {
  return attributeOptions.reduce((acc, option) => {
    const id = option?.column_context?.[0]?.id?.long;
    if (acc[id]) {
      return { ...acc, [id]: [...acc[id], option] };
    }
    return {
      ...acc,
      [id]: Array(1).fill(option)
    };
  }, {});
};

///////////////////////////////////

export const transformEventQueryOptionsToSelectOptions = ({
  column_options = [],
  attribute_options = []
}) => {
  const columnOptions = column_options.map(option => ({
    id: option.name,
    label: option.alias || option.name,
    subLabel: option.type,
    optionType: 'column_identifier',
    ...option
  }));
  const attributeOptions = attribute_options.map(option => ({
    id: option.name,
    label: option.name,
    subLabel: option.type,
    optionType: Array.isArray(option?.path) ? 'attribute_identifier_v2' : 'attribute_identifier',
    ...option
  }));
  const options = [...columnOptions, ...attributeOptions].reduce((acc, option) => {
    const subLabel = option.subLabel;
    const id = option.id;
    const found = acc.some(item => item.subLabel === subLabel && item.id === id);
    if (!found) {
      acc = [...acc, option];
    }
    return acc;
  }, []);
  return options;
};
