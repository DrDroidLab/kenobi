import { Link, useNavigate, useParams } from 'react-router-dom';
import Heading from '../../components/Heading';
import API from '../../API';
import { useCallback, useEffect, useState } from 'react';

import SuspenseLoader from '../../components/Skeleton/SuspenseLoader';
import TableSkeleton from '../../components/Skeleton/TableLoader';

import { CircularProgress } from '@mui/material';

import PanelGrid from './PanelGrid';

const DashboardView = () => {
  const { id } = useParams();

  const dashName = atob(id);
  const [loading, setLoading] = useState(false);
  const [refresh, setRefresh] = useState(false);
  const [loadPanels, setLoadPanels] = useState(false);
  const [panelDataList, setPanelDataList] = useState([]);
  const [customTimeRange, setCustomTimeRange] = useState();
  const [startTime, setStartTime] = useState();
  const getDashboards = API.useGetDashboardData();

  useEffect(() => {
    setLoading(true);
    getDashboards(
      { name: dashName },
      response => {
        if (response.data?.dashboards?.length > 0) {
          let dashAPIResponse = response.data?.dashboards[0];
          setPanelDataList(dashAPIResponse.panels);

          // This is always in IST
          let startISTHour = dashAPIResponse.start_hour;

          if (startISTHour) {
            let startUTCHour = parseInt(startISTHour) - 6;
            if (startUTCHour < 0) {
              startUTCHour = startUTCHour + 24;
            }

            const utcTime = new Date();
            utcTime.setUTCHours(startUTCHour, 30, 0);

            const epochTimestamp = Math.floor(utcTime.getTime() / 1000);
            const localTimestamp = new Date(epochTimestamp * 1000);

            const localTimeZoneStartHour = localTimestamp.getHours();
            const localTimeZoneMinutes = localTimestamp.getMinutes();

            let startTime = new Date();
            let currentHour = new Date().getHours();

            if (localTimeZoneStartHour > currentHour) {
              startTime.setDate(startTime.getDate() - 1);
            }
            startTime.setHours(localTimeZoneStartHour, localTimeZoneMinutes, 0, 0);

            setCustomTimeRange({
              start: startTime.getTime() / 1000
            });
            setStartTime(startTime.getTime() / 1000);
          }
        }
        setLoading(false);
        setLoadPanels(true);
      },
      err => {
        setLoading(false);
      }
    );
  }, []);

  const loadingCb = () => {
    setRefresh(!refresh);
  };

  return (
    <SuspenseLoader loading={!!loading} loader={<TableSkeleton noOfLines={6} />}>
      <Heading
        subHeading={'Dashboard'}
        heading={dashName}
        onTimeRangeChangeCb={loadingCb}
        onRefreshCb={loadingCb}
        defaultCustomTillNowTimeRange={customTimeRange || null}
        isPanelLoad={loadPanels}
      />
      {panelDataList?.length && loadPanels && (
        <PanelGrid
          panelDataList={panelDataList}
          refresh={refresh}
          startTime={startTime}
          name={dashName}
        />
      )}
    </SuspenseLoader>
  );
};

export default DashboardView;
