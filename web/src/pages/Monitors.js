import { useCallback, useEffect, useState } from 'react';
import API from '../API';
import Heading from '../components/Heading';
import TableSkeleton from '../components/Skeleton/TableLoader';
import SuspenseLoader from '../components/Skeleton/SuspenseLoader';
import MonitorsTable from '../components/Monitors/MonitorsTable';
import CreateMonitorLink from '../components/Monitors/CreateMonitorLink';
import { SearchComponent } from '../components/SearchComponent';

const monitorSearchOptions = [
  {
    id: 'MONITOR',
    label: 'Monitor Name'
  }
];
const Monitors = () => {
  const [loading, setLoading] = useState(true);

  const [monitors, setMonitors] = useState([]);

  const [total, setTotal] = useState(0);
  const [pageMeta, setPageMeta] = useState({ limit: 10, offset: 0 });
  const [searchPayload, setSearchPayload] = useState();

  const fetchMonitors = API.useGetMonitors();

  useEffect(() => {
    if (loading) {
      fetchMonitors(
        [],
        pageMeta,
        searchPayload,
        response => {
          setMonitors(response.data?.monitors);
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
      fetchMonitors(
        [],
        page,
        searchPayload,
        resp => {
          setMonitors(resp.data?.monitors);
          setTotal(Number(resp.data?.meta?.total_count));
          successCb(resp.data?.monitors, Number(resp.data?.meta?.total_count));
        },
        err => {
          errCb(err);
        }
      );
    },
    [fetchMonitors]
  );

  useEffect(() => {
    window?.analytics?.page('Monitors Page load');
  }, []);

  const handleSearchChange = useCallback((searchValue, searchType) => {
    setSearchPayload({
      context: searchType,
      pattern: searchValue
    });
    setLoading(true);
  }, []);

  return (
    <>
      <Heading heading={'Monitors'} onTimeRangeChangeCb={loadingCb} onRefreshCb={loadingCb}>
        <CreateMonitorLink />
      </Heading>
      <SearchComponent
        selectDisabled
        options={monitorSearchOptions}
        selectedOption={monitorSearchOptions[0].id}
        onSearchChange={handleSearchChange}
      />
      <SuspenseLoader loading={!!loading} loader={<TableSkeleton />}>
        <MonitorsTable
          monitors={monitors}
          total={total}
          pageSize={pageMeta ? pageMeta?.limit : 10}
          pageUpdateCb={pageUpdateCb}
          tableContainerStyles={monitors?.length ? {} : { maxHeight: '35vh', minHeight: '35vh' }}
        ></MonitorsTable>
      </SuspenseLoader>
    </>
  );
};

export default Monitors;
