import React, { useCallback, useEffect, useState } from 'react';
import { Grid } from '@mui/material';
import API from '../API';
import Heading from '../components/Heading';
import SuspenseLoader from '../components/Skeleton/SuspenseLoader';
import TableSkeleton from '../components/Skeleton/TableLoader';
import MonitorsTableCard from '../components/Monitors/MonitorsTableCard';
import EntitiesTypeTableCard from '../components/Entities/EntitiesTypeTableCard';
import DashboardTableCard from '../components/Dashboard/DashboardTableCard';

function getFirstNElements(arr, n) {
  if (!arr || arr.length === 0) {
    return []; // Return an empty array if the input array is null or empty
  }
  return arr.slice(0, n); // Use the slice method to get the first N elements
}

const Home = () => {
  const [loading, setLoading] = useState(true);

  const page = { limit: 3, offset: 0 };

  const [entitySummaries, setEntitySummaries] = useState([]);
  const [dashboards, setDashboards] = useState([]);
  const [monitors, setMonitors] = useState([]);

  const [isMonitorsFetched, setIsMonitorsFetched] = useState(false);
  const [isEntitiesFetched, setIsEntitiesFetched] = useState(false);
  const [isDashboardsFetched, setIsDashboardsFetched] = useState(false);

  const [totalMonitors, setTotalMonitors] = useState(0);
  const [totalEntities, setTotalEntities] = useState(0);
  const [totalDashboards, setTotalDashboards] = useState(0);

  const fetchMonitors = API.useGetMonitors();
  const fetchEntitySummary = API.useGetEntitySummary();
  const getDashboards = API.useGetDashboardData();

  useEffect(() => {
    if (!loading) {
      return;
    }
    getDashboards({}, response => {
      setDashboards(getFirstNElements(response.data.dashboards, 3));
      setTotalDashboards(Number(response.data.dashboards?.length));
      setIsDashboardsFetched(true);
    });
    fetchEntitySummary([], page, {}, resp => {
      setEntitySummaries(resp.data?.entities);
      setTotalEntities(Number(resp.data?.meta?.total_count));
      setIsEntitiesFetched(true);
    });
    fetchMonitors([], page, null, response => {
      if (response.data?.monitors) {
        setMonitors(response.data?.monitors);
      }
      setTotalMonitors(Number(response.data?.meta?.total_count));
      setIsMonitorsFetched(true);
    });
    setLoading(false);
  }, [loading]);

  const loadingCb = useCallback(() => {
    setLoading(true);
    setIsMonitorsFetched(false);
    setIsEntitiesFetched(false);
  }, [loading]);

  useEffect(() => {
    window?.analytics?.page('Home');
  }, []);

  return (
    <>
      <Heading heading={'Home'} onTimeRangeChangeCb={loadingCb} onRefreshCb={loadingCb} />
      <div className="py-4 px-4">
        <Grid container direction="column" spacing={2}>
          <Grid item>
            <SuspenseLoader loading={!isDashboardsFetched} loader={<TableSkeleton noOfLines={2} />}>
              <DashboardTableCard
                dashboards={dashboards}
                extraHeader={totalDashboards}
                total={totalDashboards}
                tableContainerStyles={{}}
              ></DashboardTableCard>
            </SuspenseLoader>
          </Grid>
          <Grid item>
            <SuspenseLoader loading={!isEntitiesFetched} loader={<TableSkeleton noOfLines={2} />}>
              <EntitiesTypeTableCard
                entities={entitySummaries}
                extraHeader={totalEntities}
                total={totalEntities}
                tableContainerStyles={{}}
              ></EntitiesTypeTableCard>
            </SuspenseLoader>
          </Grid>
          <Grid item>
            <SuspenseLoader loading={!isMonitorsFetched} loader={<TableSkeleton noOfLines={2} />}>
              <MonitorsTableCard
                isCard={true}
                extraHeader={totalMonitors}
                monitors={monitors}
                total={monitors?.length}
                tableContainerStyles={{}}
              />
            </SuspenseLoader>
          </Grid>
        </Grid>
      </div>
    </>
  );
};

export default Home;
