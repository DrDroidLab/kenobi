import EventTypesTable from '../components/EventType/EventTypesTable';
import { useCallback, useEffect, useState } from 'react';
import API from '../API';
import Heading from '../components/Heading';
import TableSkeleton from '../components/Skeleton/TableLoader';
import SuspenseLoader from '../components/Skeleton/SuspenseLoader';
import { SearchComponent } from '../components/SearchComponent';

const entitySearchSearchOptions = [
  {
    label: 'Event Type Name',
    id: 'EVENT_TYPE'
  }
];
const EventTypes = () => {
  const [loading, setLoading] = useState(true);

  const [eventTypeSummaries, setEventTypeSummaries] = useState([]);

  const [total, setTotal] = useState(0);
  const [pageMeta, setPageMeta] = useState({ limit: 10, offset: 0 });
  const [searchPayload, setSearchPayload] = useState();

  const fetchEventTypeSummary = API.useGetEventTypeSummary();

  useEffect(() => {
    if (loading) {
      fetchEventTypeSummary(
        [],
        pageMeta,
        searchPayload,
        response => {
          setEventTypeSummaries(response.data?.event_type_summary);
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
      fetchEventTypeSummary(
        [],
        page,
        searchPayload,
        resp => {
          setEventTypeSummaries(resp.data?.event_type_summary);
          setTotal(Number(resp.data?.meta?.total_count));
          successCb(resp.data?.event_type_summary, Number(resp.data?.meta?.total_count));
        },
        err => {
          errCb(err);
        }
      );
    },
    [fetchEventTypeSummary]
  );

  const handleSearchChange = useCallback((searchValue, searchType) => {
    setPageMeta({ limit: 10, offset: 0 });
    setSearchPayload({
      context: searchType,
      pattern: searchValue
    });
    setLoading(true);
  }, []);

  return (
    <>
      <Heading heading={'Event Types'} onTimeRangeChangeCb={loadingCb} onRefreshCb={loadingCb} />
      <SearchComponent
        selectDisabled
        options={entitySearchSearchOptions}
        selectedOption={entitySearchSearchOptions[0].id}
        onSearchChange={handleSearchChange}
      />
      <SuspenseLoader loading={!!loading} loader={<TableSkeleton />}>
        <EventTypesTable
          eventTypeSummaries={eventTypeSummaries}
          total={total}
          pageSize={pageMeta ? pageMeta?.limit : 10}
          pageUpdateCb={pageUpdateCb}
          tableContainerStyles={
            eventTypeSummaries?.length ? {} : { maxHeight: '35vh', minHeight: '35vh' }
          }
        ></EventTypesTable>
      </SuspenseLoader>
    </>
  );
};

export default EventTypes;
