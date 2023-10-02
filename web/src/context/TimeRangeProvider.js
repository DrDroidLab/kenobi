import { createContext, useCallback, useState } from 'react';

const getCurrentTimeStamp = () => {
  return Math.floor(Date.now() / 1000);
};

const defaultTimeRangeOptions = {
  '5m': {
    displayLabel: '10 Minutes',
    getTimeRange: () => {
      let currentTimestamp = getCurrentTimeStamp();
      return { time_geq: currentTimestamp - 600, time_lt: currentTimestamp };
    }
  },
  '30m': {
    displayLabel: '30 Minutes',
    getTimeRange: () => {
      let currentTimestamp = getCurrentTimeStamp();
      return { time_geq: currentTimestamp - 1800, time_lt: currentTimestamp };
    }
  },
  '1h': {
    displayLabel: '1 Hour',
    getTimeRange: () => {
      let currentTimestamp = getCurrentTimeStamp();
      return { time_geq: currentTimestamp - 3600, time_lt: currentTimestamp };
    }
  },
  '3h': {
    displayLabel: '3 Hours',
    getTimeRange: () => {
      let currentTimestamp = getCurrentTimeStamp();
      return { time_geq: currentTimestamp - 10800, time_lt: currentTimestamp };
    }
  },
  '12h': {
    displayLabel: '12 Hours',
    getTimeRange: () => {
      let currentTimestamp = getCurrentTimeStamp();
      return { time_geq: currentTimestamp - 43200, time_lt: currentTimestamp };
    }
  },
  '1d': {
    displayLabel: '1 Day',
    getTimeRange: () => {
      let currentTimestamp = getCurrentTimeStamp();
      return { time_geq: currentTimestamp - 86400, time_lt: currentTimestamp };
    }
  },
  Custom: {
    displayLabel: 'Custom'
  },
  CustomTillNow: {
    displayLabel: 'Custom till now'
  }
};

const TimeRangeContext = createContext({});

export const TimeRangeProvider = ({ children }) => {
  const [timeRange, setTimeRange] = useState('30m');

  const [startTime, setStartTime] = useState();
  const [endTime, setEndTime] = useState();

  const updateTimeRange = value => {
    setTimeRange(value);
  };

  const updateCustomTimeRange = (start, end) => {
    setStartTime(start);
    setEndTime(end);
    setTimeRange('Custom');
  };

  const updateCustomTillNowTimeRange = start => {
    setStartTime(start);
    setTimeRange('CustomTillNow');
  };
  const getTimeRange = useCallback(() => {
    if (timeRange === 'Custom') {
      return { time_geq: startTime, time_lt: endTime };
    } else if (timeRange === 'CustomTillNow') {
      return { time_geq: startTime, time_lt: getCurrentTimeStamp() };
    } else {
      return defaultTimeRangeOptions[timeRange].getTimeRange();
    }
  }, [timeRange, startTime, endTime]);

  const getTimeRangeOptions = () => {
    return defaultTimeRangeOptions;
  };

  return (
    <TimeRangeContext.Provider
      value={{
        timeRange,
        updateTimeRange,
        updateCustomTimeRange,
        updateCustomTillNowTimeRange,
        getTimeRangeOptions,
        getTimeRange
      }}
    >
      {children}
    </TimeRangeContext.Provider>
  );
};

export default TimeRangeContext;
