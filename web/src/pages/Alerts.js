import AlertsTable from '../components/Alerts/AlertsTable';
import { useCallback, useEffect, useState } from 'react';
import API from '../API';
import Heading from '../components/Heading';
import TableSkeleton from '../components/Skeleton/TableLoader';
import SuspenseLoader from '../components/Skeleton/SuspenseLoader';

const Alerts = () => {
  const [loading, setLoading] = useState(true);

  const [alerts, setAlerts] = useState({});

  const [total, setTotal] = useState(0);
  const [pageMeta, setPageMeta] = useState({ limit: 10, offset: 0 });

  const fetchAlerts = API.useGetAlerts();

  useEffect(() => {
    if (loading) {
      fetchAlerts(
        pageMeta,
        response => {
          setAlerts(response.data?.alerts_summary);
          setTotal(Number(response.data?.meta?.total_count));
          setLoading(false);
        },
        err => {
          setLoading(false);
        }
      );
    }
  }, [loading]);

  const loadingCb = useCallback(() => {
    setLoading(true);
  }, [loading]);

  const pageUpdateCb = useCallback(
    (page, successCb, errCb) => {
      setPageMeta(page);
      fetchAlerts(
        page,
        resp => {
          setAlerts(resp.data?.alerts_summary);
          setTotal(Number(resp.data?.meta?.total_count));
          successCb(resp.data?.alerts_summary, Number(resp.data?.meta?.total_count));
        },
        err => {
          errCb(err);
        }
      );
    },
    [fetchAlerts]
  );

  useEffect(() => {
    window?.analytics?.page('Alerts Page load');
  }, []);

  return (
    <>
      <Heading heading={'Alerts'} onTimeRangeChangeCb={loadingCb} onRefreshCb={loadingCb} />
      <SuspenseLoader loading={!!loading} loader={<TableSkeleton />}>
        <AlertsTable
          alerts={alerts}
          total={total}
          pageSize={pageMeta ? pageMeta?.limit : 10}
          pageUpdateCb={pageUpdateCb}
          tableContainerStyles={alerts?.length ? {} : { maxHeight: '25vh', minHeight: '25vh' }}
        ></AlertsTable>
      </SuspenseLoader>
    </>
  );
};

export default Alerts;
