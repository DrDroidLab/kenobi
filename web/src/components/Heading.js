import { Grid } from '@mui/material';
import React from 'react';
import TimeRangePicker from './TimeRangePicker';
import Refresh from '../Refresh';

const renderChildren = children => {
  return React.Children.map(children, child => {
    return <Grid item>{child}</Grid>;
  });
};

const Heading = ({
  subHeading,
  heading,
  onTimeRangeChangeCb,
  onRefreshCb,
  children,
  defaultTimeRange,
  defaultCustomTimeRange,
  defaultCustomTillNowTimeRange,
  isPanelLoad
}) => {
  const [isRefreshBtnDisabled, setIsRefreshBtnDisabled] = React.useState(false);

  const handleRefreshButtonDisable = isDisabled => {
    setIsRefreshBtnDisabled(isDisabled);
  };
  return (
    <>
      <div className="w-full py-3 flex justify-between bg-white border-b border-gray-300 px-4 items-center shadow-mds sticky">
        <div className="flex-col justify-items-center">
          {!!subHeading ? <div className="text-xs text-gray-400">{subHeading}</div> : null}
          <div className="text-xs sm:text-lg font-semibold text-gray-800">{heading}</div>
        </div>
        <div className="flex">
          {renderChildren(children)}
          {onTimeRangeChangeCb ? (
            <Grid item>
              <TimeRangePicker
                onTimeRangeChangeCb={onTimeRangeChangeCb}
                defaultTimeRange={defaultTimeRange}
                defaultCustomTimeRange={defaultCustomTimeRange}
                defaultCustomTillNowTimeRange={defaultCustomTillNowTimeRange}
                isPanelLoad={isPanelLoad}
                onRefreshButtonDisable={handleRefreshButtonDisable}
              />
            </Grid>
          ) : null}
          {onRefreshCb ? (
            <Grid item>
              <Refresh onRefreshCb={onRefreshCb} disabled={isRefreshBtnDisabled} />
            </Grid>
          ) : null}
        </div>
      </div>
    </>
  );
};

export default Heading;
