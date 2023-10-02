import { useParams } from 'react-router-dom';
import Heading from '../../components/Heading';
import API from '../../API';
import { useCallback, useEffect, useState } from 'react';
import PaginatedTable from '../../components/PaginatedTable';
import SuspenseLoader from '../../components/Skeleton/SuspenseLoader';
import TableSkeleton from '../../components/Skeleton/TableLoader';
import EntityTable from '../../components/Entities/EntityTable';
import { transformEventQueryOptionsToSelectOptions } from '../../components/Events/utils';
import useNode from '../../hooks/useNode.ts';
import FilterComponent from '../../components/FilterComponent';
import { validatePayload } from '../../utils/QueryBuilder';
import useToggle from '../../hooks/useToggle';
import { transformToAPIPayload } from '../../utils/utils';
import Toast from '../../components/Toast';
import { transformToMTQueryBuilderPayload } from '../Monitor/utils';

import TriggersSection from '../../components/Entities/Triggers/TriggersSection';

const Entity = () => {
  let { id } = useParams();
  const urlParams = new URLSearchParams(window.location.search);
  const queryParamsId = urlParams.get('id');
  const { isOpen, toggle } = useToggle();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState();
  const [validationError, setValidationError] = useState();
  const [loading, setLoading] = useState(false);
  const [entitySummaries, setEntitySummaries] = useState({});
  const [entitySearchOptions, setEntitySearchOptions] = useState([]);
  const [entitySearchLoading, setEntitySearchLoading] = useState(true);
  const [defaultQueryRequest, setDefaultQueryRequest] = useState();
  const [entityInstanceSummary, setEntityInstanceSummary] = useState([]);
  const [searchPayload, setSearchPayload] = useState();
  const [pageMeta, setPageMeta] = useState({ limit: 10, offset: 0 });
  const [total, setTotal] = useState(0);
  const [entitySummaryLoading, setEntitySummaryLoading] = useState(true);
  const [queryBuilderPayload, setQueryBuilderPayload] = useState({
    op: 'AND',
    filters: []
  });

  const fetchEntitySummary = API.useGetEntitySummary();
  const fetchEntityInstanceSummary = API.useGetEntityInstanceSummary();
  const fetchEntitySearchOptions = API.useGetEntitySearchOptions();

  const { insertNode, deleteNode, updateNode } = useNode();

  useEffect(() => {
    if (loading) {
      fetchEntityInstanceSummary(
        {
          ...searchPayload,
          meta: {
            page: pageMeta
          }
        },
        response => {
          setLoading(false);
          setTotal(response.data?.meta?.total_count);
          setEntityInstanceSummary(response.data?.entity_instances);
        },
        err => {
          setLoading(false);
          toggleError();
          setSubmitError(err?.err);
        }
      );
    }
  }, [loading]);

  useEffect(() => {
    if (entitySummaryLoading) {
      setEntityInstanceSummary([]);
      fetchEntitySummary(
        [id],
        pageMeta,
        null,
        response => {
          if (response.data?.entities?.length > 0) {
            setEntitySummaries(response.data?.entities[0]);
            setEntitySummaryLoading(false);
          }
        },
        err => {
          console.error(err);
          setEntitySummaryLoading(false);
        }
      );
    }
  }, [entitySummaryLoading]);

  useEffect(() => {
    if (entitySearchLoading) {
      fetchEntitySearchOptions(
        {
          id_literal: {
            type: 'LONG',
            long: id
          }
        },
        res => {
          setEntitySearchLoading(false);
          const { default_query_request, event_query_options } = res.data;
          const { column_options, attribute_options_v2 } = event_query_options;
          const transformedOptions = transformEventQueryOptionsToSelectOptions({
            column_options: column_options,
            attribute_options: attribute_options_v2
          });
          const transformedPayload = transformToMTQueryBuilderPayload(
            default_query_request,
            transformedOptions,
            'attribute_identifier_v2',
            'entity_id'
          );
          setDefaultQueryRequest(default_query_request);
          setQueryBuilderPayload(transformedPayload);
          setEntitySearchOptions(transformedOptions);
          setSearchPayload({
            ...searchPayload,
            query_request: {
              filter: {
                ...default_query_request.filter,
                filters: default_query_request.filter.filters || []
              }
            }
          });
          setLoading(true);
        },
        err => {
          setEntitySearchLoading(false);
          console.error(err);
        }
      );
    }
  }, []);

  const loadingCb = useCallback(() => {
    setLoading(true);
  }, [loading]);

  const pageUpdateCb = useCallback(
    (page, successCb, errCb) => {
      setPageMeta(page);
      fetchEntityInstanceSummary(
        {
          ...searchPayload,
          meta: {
            page: page
          }
        },
        resp => {
          setTotal(Number(resp.data?.meta?.total_count));
          setEntityInstanceSummary(resp.data?.entity_instances);
          successCb(resp.data?.entity_instances, Number(resp.data?.meta?.total_count));
        },
        err => {
          errCb(err);
        }
      );
    },
    [fetchEntityInstanceSummary]
  );

  const handleAdd = ({ id, isGroup }) => {
    const tree = insertNode({
      tree: queryBuilderPayload,
      id: id,
      isGroup: isGroup
    });
    setQueryBuilderPayload({ ...tree });
  };
  const handleUpdate = ({ id, type, value, isGroup }) => {
    const tree = updateNode({ tree: queryBuilderPayload, id, value, type, isGroup });
    setQueryBuilderPayload({ ...tree });
  };
  const handleDelete = ({ id, isGroup }) => {
    const tree = deleteNode({
      tree: queryBuilderPayload,
      id,
      isGroup
    });
    setQueryBuilderPayload({ ...tree });
  };

  const handleClearFilter = () => {
    const transformedPayload = transformToMTQueryBuilderPayload(
      defaultQueryRequest,
      entitySearchOptions,
      'attribute_identifier_v2',
      'entity_id'
    );
    setQueryBuilderPayload(transformedPayload);
    setSearchPayload({
      filter: {
        op: 'AND',
        filters: defaultQueryRequest.filter.filters
      }
    });
    setSearchPayload({
      meta: {
        page: pageMeta
      },
      query_request: {
        filter: {
          filters: defaultQueryRequest.filter.filters?.filter(
            query => query.lhs?.column_identifier?.name === 'entity_id'
          ),
          op: defaultQueryRequest.filter.op
        }
      }
    });
    setLoading(true);
  };

  const handleSubmit = () => {
    const valError = validatePayload(queryBuilderPayload);
    if (valError) {
      setValidationError(valError);
      toggle();
      return;
    }
    const queryAPIPayload = transformToAPIPayload(queryBuilderPayload);
    setSearchPayload({
      ...searchPayload,
      query_request: {
        ...searchPayload.query_request,
        ...queryAPIPayload
      }
    });
    setLoading(true);
  };

  return (
    <div>
      <Heading
        subHeading="Entity"
        heading={entitySummaries?.entity?.name}
        onTimeRangeChangeCb={loadingCb}
        onRefreshCb={loadingCb}
      />
      <div>
        <TriggersSection entity_id={id} />
        <SuspenseLoader loading={!!entitySearchLoading} loader={<TableSkeleton />}>
          {entitySearchOptions && (
            <FilterComponent
              filter={queryBuilderPayload}
              options={entitySearchOptions}
              onAdd={handleAdd}
              onUpdate={handleUpdate}
              onDelete={handleDelete}
              onSubmit={handleSubmit}
              onClearFilter={handleClearFilter}
            />
          )}
        </SuspenseLoader>
        <SuspenseLoader loading={!!loading} loader={<TableSkeleton />}>
          <PaginatedTable
            renderTable={EntityTable}
            data={entityInstanceSummary}
            total={total}
            pageSize={pageMeta ? pageMeta?.limit : 10}
            pageUpdateCb={pageUpdateCb}
          />
        </SuspenseLoader>
      </div>

      <Toast
        open={!!isOpen}
        severity="info"
        message={validationError}
        handleClose={() => toggle()}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      />
      <Toast
        open={!!IsError}
        severity="error"
        message={submitError}
        handleClose={() => toggleError()}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      />
    </div>
  );
};

export default Entity;
