import { useEffect } from 'react';

import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';
import useTimeRange from '../hooks/useTimeRange';

import Toast from '../components/Toast';
import useToggle from '../hooks/useToggle';

import styles from './timepicker.module.css';
import ArrowRightAltIcon from '@mui/icons-material/ArrowRightAlt';

import { useState } from 'react';

const renderTimeRangeMenuItems = timeRangeOptions => {
  if (timeRangeOptions === undefined) {
    return;
  }

  return Object.keys(timeRangeOptions).map(key => (
    <MenuItem key={key} value={key}>
      {timeRangeOptions[key].displayLabel}
    </MenuItem>
  ));
};

const convertEpochToDateTime = epochTime => {
  let date = new Date(epochTime * 1000);

  let year = date.getFullYear();
  let month = ('0' + (date.getMonth() + 1)).slice(-2);
  let day = ('0' + date.getDate()).slice(-2);
  let hours = ('0' + date.getHours()).slice(-2);
  let minutes = ('0' + date.getMinutes()).slice(-2);

  let formattedDateTime = year + '-' + month + '-' + day + 'T' + hours + ':' + minutes;
  return formattedDateTime;
};

const convertDateTimeToEpoch = dateTime => {
  return Date.parse(dateTime) / 1000;
};

const TimeRangePicker = ({
  onTimeRangeChangeCb,
  defaultTimeRange,
  defaultCustomTimeRange,
  defaultCustomTillNowTimeRange,
  isPanelLoad,
  onRefreshButtonDisable
}) => {
  const {
    timeRange,
    updateTimeRange,
    updateCustomTimeRange,
    updateCustomTillNowTimeRange,
    getTimeRangeOptions,
    getTimeRange
  } = useTimeRange();

  const previousTimeRange = getTimeRange();

  const [loadTimeRangeOptions, setLoadTimeRangeOptions] = useState(false);

  const [isCustomTimeRangeSelected, setIsCustomTimeRangeSelected] = useState(
    defaultTimeRange ? false : timeRange === 'Custom'
  );
  const [isCustomTillNowTimeRangeSelected, setIsCustomTillNowTimeRangeSelected] = useState(
    defaultTimeRange ? false : timeRange === 'CustomTillNow'
  );
  const [startTime, setStartTime] = useState(convertEpochToDateTime(previousTimeRange.time_geq));
  const [endTime, setEndTime] = useState(convertEpochToDateTime(previousTimeRange.time_lt));

  const { isOpen, toggle } = useToggle();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState();

  useEffect(() => {
    if (defaultTimeRange) {
      updateTimeRange(defaultTimeRange);
    }

    if (defaultCustomTimeRange) {
      setIsCustomTimeRangeSelected(true);
      setStartTime(convertEpochToDateTime(parseInt(defaultCustomTimeRange.start)));
      setEndTime(convertEpochToDateTime(parseInt(defaultCustomTimeRange.end)));
      updateCustomTimeRange(
        parseInt(defaultCustomTimeRange.start),
        parseInt(defaultCustomTimeRange.end)
      );
    }

    if (defaultCustomTillNowTimeRange) {
      setIsCustomTillNowTimeRangeSelected(true);
      setIsCustomTimeRangeSelected(false);
      setStartTime(convertEpochToDateTime(parseInt(defaultCustomTillNowTimeRange.start)));
      updateCustomTillNowTimeRange(parseInt(defaultCustomTillNowTimeRange.start));
    }

    setLoadTimeRangeOptions(true);
  }, [isPanelLoad]);

  const onTimeRangeChange = event => {
    if (event.target.value === 'Custom') {
      const previousTimeRange = getTimeRange();
      let startTimeValue = convertEpochToDateTime(previousTimeRange.time_geq);
      let endTimeValue = convertEpochToDateTime(previousTimeRange.time_lt);
      setStartTime(startTimeValue);
      setEndTime(endTimeValue);
      setIsCustomTillNowTimeRangeSelected(false);
      setIsCustomTimeRangeSelected(true);
      updateCustomTimeRange(previousTimeRange.time_geq, previousTimeRange.time_lt);
    } else if (event.target.value === 'CustomTillNow') {
      const previousTimeRange = getTimeRange();
      let startTimeValue = convertEpochToDateTime(previousTimeRange.time_geq);
      setStartTime(startTimeValue);
      setIsCustomTimeRangeSelected(false);
      setIsCustomTillNowTimeRangeSelected(true);
      updateCustomTillNowTimeRange(previousTimeRange.time_geq);
      setStartTime(startTimeValue);
    } else {
      setIsCustomTillNowTimeRangeSelected(false);
      setIsCustomTimeRangeSelected(false);
      updateTimeRange(event.target.value);
      if (onTimeRangeChangeCb) {
        onTimeRangeChangeCb();
      }
    }
  };

  const handleTimeSelectorChange = () => {
    if (isCustomTimeRangeSelected) {
      onRefreshButtonDisable(false);
      let startTimeValue = convertDateTimeToEpoch(
        document.getElementById('startTimeSelector').value
      );
      let endTimeValue = convertDateTimeToEpoch(document.getElementById('endTimeSelector').value);

      if (!startTimeValue || !endTimeValue) {
        toggleError();
        setSubmitError('Please select start and end time');
        return;
      }

      if (startTimeValue > endTimeValue) {
        toggleError();
        setSubmitError('Choose end time later than the start time');
        onRefreshButtonDisable(true);
        return;
      }
      if (endTimeValue - startTimeValue > 604800) {
        toggleError();
        setSubmitError('Start time cannot be older than 7 days from end time');
        onRefreshButtonDisable(true);
        return;
      }

      updateCustomTimeRange(startTimeValue, endTimeValue);
    }
  };

  const handleCustomTillNowChange = e => {
    onRefreshButtonDisable(false);
    const startTimeValue = convertDateTimeToEpoch(e?.target?.value);
    setStartTime(e?.target?.value);
    const currentTimeStamp = Math.floor(Date.now() / 1000);
    if (!startTimeValue) {
      toggleError();
      setSubmitError('Please select start time');
      onRefreshButtonDisable(true);
      return;
    }
    if (startTimeValue > currentTimeStamp) {
      toggleError();
      setSubmitError('Choose end time later than the start time');
      onRefreshButtonDisable(true);
      return;
    }
    if (currentTimeStamp - startTimeValue > 604800) {
      toggleError();
      setSubmitError('Start time cannot be older than 7 days');
      onRefreshButtonDisable(true);
      return;
    }
    updateCustomTillNowTimeRange(startTimeValue);
  };
  return (
    <>
      {loadTimeRangeOptions && (
        <div className={styles['timeRangePicker']}>
          {isCustomTimeRangeSelected && !isCustomTillNowTimeRangeSelected && (
            <div className={styles['timeSelectorGroup']}>
              <input
                type="datetime-local"
                className={styles['timeSelector']}
                id="startTimeSelector"
                defaultValue={startTime}
                onChange={e => handleTimeSelectorChange()}
              />
              <ArrowRightAltIcon />
              <input
                type="datetime-local"
                className={styles['timeSelector']}
                id="endTimeSelector"
                defaultValue={endTime}
                onChange={e => handleTimeSelectorChange()}
              />
            </div>
          )}
          {isCustomTillNowTimeRangeSelected && !isCustomTimeRangeSelected && (
            <div className={styles['timeSelectorGroup']}>
              <input
                type="datetime-local"
                className={styles['timeSelector']}
                id="startTimeSelector"
                defaultValue={startTime}
                onChange={handleCustomTillNowChange}
              />
              <span>
                <ArrowRightAltIcon />
              </span>

              <span>Now</span>
            </div>
          )}
          <div className={styles['timeRangeSelector']}>
            <FormControl>
              <InputLabel id="time-range-select-label">Time Range</InputLabel>
              <Select
                value={timeRange}
                label="TimeRange"
                id="time-range-select"
                onChange={onTimeRangeChange}
                labelId="time-range-select-label"
                size="small"
              >
                {renderTimeRangeMenuItems(getTimeRangeOptions())}
              </Select>
            </FormControl>
          </div>
        </div>
      )}

      <Toast
        open={!!IsError}
        severity="error"
        message={submitError}
        handleClose={() => toggleError()}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        autoHideDuration={60000}
      />
    </>
  );
};

export default TimeRangePicker;
