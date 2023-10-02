export const intervalOptions = [
  {
    label: '1 minute',
    id: 60
  },
  {
    label: '5 minutes',
    id: 300
  },
  {
    label: '10 minutes',
    id: 600
  },
  {
    label: '30 minutes',
    id: 1800
  },
  {
    label: '1 hour',
    id: 3600
  },
  {
    label: '3 hours',
    id: 10800
  }
];

export const metricTypes = [
  {
    column: 'event_type_id',
    label: 'Event',
    id: 'EVENT',
    type: 'ID'
  },
  {
    column: 'monitor_id',
    label: 'Monitor',
    id: 'MONITOR_TRANSACTION',
    type: 'ID'
  }
];

export const timeSeriesViewOptions = [
  {
    label: 'Line Chart',
    id: 'LINE'
  },
  {
    label: 'Bar Chart',
    id: 'BAR'
  },
  {
    label: 'Area Chart',
    id: 'AREA'
  }
];

export const nonTimeSeriesViewOptions = [
  {
    label: 'Bar Chart',
    id: 'BAR'
  },
  {
    label: 'Table Chart',
    id: 'SIMPLE_TABLE'
  }
];
