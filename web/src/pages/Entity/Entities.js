import { useCallback, useEffect, useState } from 'react';
import Heading from '../../components/Heading';
import EntityTypesTable from '../../components/Entities/EntitiesTypesTable';
import TableSkeleton from '../../components/Skeleton/TableLoader';
import SuspenseLoader from '../../components/Skeleton/SuspenseLoader';
import API from '../../API';
import CreateEntityLink from '../../components/Entities/CreateEntityLink';
import { SearchComponent } from '../../components/SearchComponent';

const entitiesSearchOptions = [
  {
    label: 'Entity Name',
    id: 'ENTITY'
  }
];

export default function Entities() {
  const [loading, setLoading] = useState(true);

  const [entitySummaries, setEntitySummaries] = useState([]);

  const [total, setTotal] = useState(0);
  const [pageMeta, setPageMeta] = useState({ limit: 10, offset: 0 });
  const [searchPayload, setSearchPayload] = useState();

  const fetchEntitySummary = API.useGetEntitySummary();

  useEffect(() => {
    if (loading) {
      fetchEntitySummary(
        [],
        pageMeta,
        searchPayload,
        response => {
          setEntitySummaries(response.data?.entities);
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
      fetchEntitySummary(
        [],
        page,
        searchPayload,
        resp => {
          setEntitySummaries(resp.data?.entities);
          setTotal(Number(resp.data?.meta?.total_count));
          successCb(resp.data?.entities, Number(resp.data?.meta?.total_count));
        },
        err => {
          errCb(err);
        }
      );
    },
    [fetchEntitySummary]
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
      <Heading heading={'Entities'} onTimeRangeChangeCb={loadingCb} onRefreshCb={loadingCb}>
        <CreateEntityLink />
      </Heading>
      <SearchComponent
        selectDisabled
        options={entitiesSearchOptions}
        selectedOption={entitiesSearchOptions[0].id}
        onSearchChange={handleSearchChange}
      />
      <SuspenseLoader loading={!!loading} loader={<TableSkeleton />}>
        <EntityTypesTable
          entitySummaries={entitySummaries}
          total={total}
          pageSize={pageMeta ? pageMeta?.limit : 10}
          pageUpdateCb={pageUpdateCb}
          tableContainerStyles={
            entitySummaries?.length ? {} : { maxHeight: '35vh', minHeight: '35vh' }
          }
        ></EntityTypesTable>
      </SuspenseLoader>
    </>
  );
}
