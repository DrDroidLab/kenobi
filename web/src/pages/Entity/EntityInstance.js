import { useParams } from 'react-router-dom';
import Heading from '../../components/Heading';
import API from '../../API';
import { useCallback, useEffect, useState } from 'react';
import PaginatedTable from '../../components/PaginatedTable';
import SuspenseLoader from '../../components/Skeleton/SuspenseLoader';
import TableSkeleton from '../../components/Skeleton/TableLoader';
import EntityInstanceDetail from '../../components/Entities/EntityInstanceDetail';
import EntityStatsCard from '../../components/Entities/EntityStatsCard';

const EntityInstance = () => {
  let { e_id, id } = useParams();

  const [loading, setLoading] = useState(true);

  const [entityInstanceDetail, setEntityInstanceDetail] = useState({});
  const fetchEntityInstanceDetails = API.useGetInstanceDetails();

  const [entityInstanceTimeline, setEntityInstanceTimeline] = useState([]);
  const fetchEntityInstanceTimeline = API.useGetInstanceTimeline();

  const [total, setTotal] = useState(0);

  const [pageMeta, setPageMeta] = useState({ limit: 10, offset: 0 });

  useEffect(() => {
    if (loading) {
      fetchEntityInstanceDetails(
        id,
        pageMeta,
        response => {
          setLoading(false);
          setEntityInstanceDetail(response.data?.entity_instance);
        },
        err => {
          setLoading(false);
        }
      );
    }
  }, [pageMeta, loading, fetchEntityInstanceDetails]);

  useEffect(() => {
    if (loading) {
      fetchEntityInstanceTimeline(
        id,
        pageMeta,
        response => {
          setLoading(false);
          setTotal(response.data?.meta?.total_count);
          setEntityInstanceTimeline(response.data?.entity_instance_timeline_records);
        },
        err => {
          setLoading(false);
        }
      );
    }
  }, [pageMeta, loading, fetchEntityInstanceTimeline]);

  const loadingCb = useCallback(() => {
    setLoading(true);
  }, [loading]);

  const pageUpdateCb = useCallback(
    (page, successCb, errCb) => {
      setPageMeta(page);
      fetchEntityInstanceTimeline(
        id,
        pageMeta,
        resp => {
          successCb(
            resp.data?.entity_instance_timeline_records,
            Number(resp.data?.meta?.total_count)
          );
        },
        err => {
          errCb(err);
        }
      );
    },
    [fetchEntityInstanceTimeline]
  );

  return (
    <div>
      <Heading
        subHeading="Entity Instance"
        heading={
          loading
            ? ''
            : `${entityInstanceDetail.entity_instance.entity.name} -> ${entityInstanceDetail.entity_instance.instance}`
        }
        onTimeRangeChangeCb={loadingCb}
        onRefreshCb={loadingCb}
      />
      <EntityStatsCard entityStats={entityInstanceDetail.stats} />
      <SuspenseLoader loading={!!loading} loader={<TableSkeleton />}>
        {entityInstanceTimeline?.length > 0 ? (
          <PaginatedTable
            renderTable={EntityInstanceDetail}
            data={entityInstanceTimeline}
            total={total}
            pageSize={pageMeta ? pageMeta?.limit : 10}
            pageUpdateCb={pageUpdateCb}
          />
        ) : null}
      </SuspenseLoader>
    </div>
  );
};

export default EntityInstance;
