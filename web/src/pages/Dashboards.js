import { Link, useNavigate, useParams } from 'react-router-dom';
import Heading from '../components/Heading';
import API from '../API';
import { useCallback, useEffect, useState } from 'react';

import SuspenseLoader from '../components/Skeleton/SuspenseLoader';
import TableSkeleton from '../components/Skeleton/TableLoader';

import { CircularProgress } from '@mui/material';

import PanelGrid from '../components/Dashboard/PanelGrid';
import DashboardTable from '../components/Dashboard/DashboardTable';

const Dashboards = () => {
  const [loading, setLoading] = useState(true);

  const [dashList, setDashList] = useState([]);

  const [total, setTotal] = useState(0);
  const [pageMeta, setPageMeta] = useState({ limit: 10, offset: 0 });

  const getDashboards = API.useGetDashboardData();

  useEffect(() => {
    if (loading) {
      setDashList([]);
      getDashboards(
        {},
        response => {
          if (response.data?.dashboards?.length > 0) {
            setDashList(response.data.dashboards);
          }
          setLoading(false);
        },
        err => {
          setLoading(false);
        }
      );
    }
  }, [loading]);

  return (
    <div>
      <Heading heading={'Dashboards'} onTimeRangeChangeCb={false} onRefreshCb={false} />
      <SuspenseLoader loading={!!loading} loader={<TableSkeleton />}>
        <DashboardTable
          dashList={dashList}
          total={total}
          pageSize={pageMeta ? pageMeta?.limit : 10}
          pageUpdateCb={() => setLoading(true)}
          tableContainerStyles={dashList?.length ? {} : { maxHeight: '35vh', minHeight: '35vh' }}
        ></DashboardTable>
      </SuspenseLoader>
    </div>
  );
};

export default Dashboards;
