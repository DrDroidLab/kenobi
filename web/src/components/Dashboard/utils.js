import dayjs from 'dayjs';

export const getLabelName = item => {
  if (item.labels) {
    if (item.labels[0].display_value) {
      return item.labels[0].display_value;
    }
    if (item.labels[0].value) {
      return extractValue(item.labels[0].value);
    }
  } else if (item.label_group) {
    return item.label_group;
  } else {
    return '';
  }
};

export const extractValue = v => {
  if (v.long) {
    return v.long;
  } else if (v.string) {
    return v.string;
  } else if (v.double) {
    return Math.trunc(v.double * 100) / 100;
  } else if (v.literal_type === 'BOOLEAN') {
    return v.boolean.toString();
  } else if (v.literal_type === 'TIMESTAMP') {
    return dayjs.unix(v.timestamp).format('DD MMM, hh:mm a');
  } else {
    return '';
  }
};

export const extractValue_v2 = v => {
  if (v.long) {
    return v.long;
  } else if (v.string) {
    return v.string;
  } else if (v.double) {
    return Math.trunc(v.double * 100) / 100;
  } else if (v.literal_type === 'BOOLEAN') {
    return v.boolean.toString();
  } else if (v.literal_type === 'TIMESTAMP') {
    return dayjs.unix(v.timestamp).format('DD MMM, hh:mm a');
  } else if (v.literal_type === 'ID') {
    return v.id.long;
  } else {
    return '';
  }
};

export const extractLabelName = ln => {
  if (ln.expression.column_identifier) {
    if (ln.alias) {
      return ln.alias;
    }
  }

  return ln.expression.attribute_identifier
    ? ln.expression.attribute_identifier.name
    : ln.expression.column_identifier
    ? ln.expression.column_identifier.name
    : '';
};

export const extractMetricType = mData => {
  return (
    mData.metadata.metric_alias_selector_map.metric_1.function +
    '_' +
    extractLabelName(mData.metadata.metric_alias_selector_map.metric_1)
  );
};
