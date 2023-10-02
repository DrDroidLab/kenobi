import { useCallback, useEffect, useState } from 'react';
import API from '../API';
import Heading from '../components/Heading';
import PaginatedTable from '../components/PaginatedTable';
import EventsTable from '../components/Events/EventsTable';
import SuspenseLoader from '../components/Skeleton/SuspenseLoader';
import TableSkeleton from '../components/Skeleton/TableLoader';
import FilterComponent from '../components/FilterComponent';
import Toast from '../components/Toast';
import useToggle from '../hooks/useToggle';
import useNode from '../hooks/useNode.ts';
import { transformEventQueryOptionsToSelectOptions } from '../../src/components/Events/utils';
import { transformToAPIPayload, transformToQueryBuilderPayload } from '../utils/utils.js';
import { validatePayload } from '../utils/QueryBuilder';
import SaveQueryOverlay from '../components/Events/SaveQueryOverlay';
import useDidMountEffect from '../hooks/useDidMountEffect';

const Events = () => {
  const urlParams = new URLSearchParams(window.location.search);
  const id = urlParams.get('id');
  const startTime = urlParams.get('startTime');
  const endTime = urlParams.get('endTime');
  const [eventTableLoading, setEventTableLoading] = useState();
  const [eventSearchLoading, setEventSearchLoading] = useState(false);
  const [eventSaveQueryLoading, setEventSaveQueryLoading] = useState(false);
  const [saveQueryId, setSaveQueryId] = useState();
  const [eventQueryOptions, setEventQueryOptions] = useState();
  const [events, setEvents] = useState([]);
  const [total, setTotal] = useState(0);
  const [pageMeta, setPageMeta] = useState({ limit: 10, offset: 0 });
  const [searchPayload, setSearchPayload] = useState({
    meta: {
      page: {
        limit: 10,
        offset: 0
      }
    }
  });
  const [orderData, setOrderData] = useState({ orderByName: '', orderByType: '', order: '' });
  const [validationError, setValidationError] = useState();
  const { isOpen, toggle } = useToggle();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const { isOpen: isSaveQueryOpen, toggle: toggleSaveQuery } = useToggle();

  const [submitError, setSubmitError] = useState();

  const fetchEventQuerySave = API.useEventQuerySave();
  const fetchEventSearch = API.useEventSearchFilter();
  const fetchEventSearchOptions = API.useFetchEventSearchOptions();

  const { insertNode, deleteNode, updateNode } = useNode();

  const [queryBuilderPayload, setQueryBuilderPayload] = useState({
    op: 'AND',
    filters: []
  });

  useDidMountEffect(() => {
    if (eventSaveQueryLoading) {
      fetchEventQuerySave(
        searchPayload,
        res => {
          setEventSaveQueryLoading(false);
          setSaveQueryId(res.data?.query_context_id);
          toggleSaveQuery();
        },
        err => {
          setEventSaveQueryLoading(false);
          toggleError();
          setSubmitError(err?.err);
        }
      );
    }
  }, [eventSaveQueryLoading]);

  useEffect(() => {
    if (eventTableLoading) {
      fetchEventSearch(
        searchPayload,
        res => {
          setEventTableLoading(false);
          setEvents(res.data?.events);
          setTotal(Number(res.data?.meta?.total_count));
        },
        err => {
          setEventTableLoading(false);
          toggleError();
          setSubmitError(err?.err);
        }
      );
    }
  }, [eventTableLoading]);

  useEffect(() => {
    setEventSearchLoading(true);
    fetchEventSearchOptions(
      {
        saved_query_request_context_id: {
          type: 'STRING',
          string: id
        }
      },
      res => {
        setEventSearchLoading(false);
        const { default_query_request, event_query_options } = res.data;
        const { column_options, attribute_options } = event_query_options;
        const transformedOptions = transformEventQueryOptionsToSelectOptions({
          column_options: column_options,
          attribute_options: attribute_options
        });
        const transformedPayload = transformToQueryBuilderPayload(
          default_query_request,
          transformedOptions
        );
        setQueryBuilderPayload(transformedPayload);
        setEventQueryOptions(transformedOptions);
        setSearchPayload({
          ...searchPayload,
          meta: {
            page: pageMeta
          },
          query_request: {
            filter: {
              ...default_query_request.filter,
              filters: default_query_request.filter.filters || []
            }
          }
        });
        setEventTableLoading(true);
      },
      err => {
        setEventSearchLoading(false);
        console.error(err);
      }
    );
  }, []);

  const loadingCb = useCallback(() => {
    setEventTableLoading(true);
  }, [eventTableLoading]);

  const pageUpdateCb = useCallback(
    (page, successCb, errCb) => {
      setPageMeta({
        limit: page.limit,
        offset: page.offset
      });
      fetchEventSearch(
        {
          ...searchPayload,
          meta: {
            ...searchPayload.meta,
            page: page
          }
        },
        res => {
          setEvents(res.data?.events);
          setTotal(Number(res.data?.meta?.total_count));
          successCb(res.data?.events, Number(res.data?.meta?.total_count));
        },
        err => {
          errCb(err);
        }
      );
    },
    [fetchEventSearch]
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
    setSearchPayload({
      meta: {
        page: pageMeta
      }
    });
    setOrderData({
      order: '',
      orderByName: '',
      orderByType: ''
    });
    setEventTableLoading(true);
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
      meta: {
        page: pageMeta
      },
      query_request: {
        ...searchPayload.query_request,
        ...queryAPIPayload
      }
    });
    setEventTableLoading(true);
  };

  const handleSave = () => {
    const valError = validatePayload(queryBuilderPayload);
    if (valError) {
      setValidationError(valError);
      toggle();
      return;
    }
    const queryAPIPayload = transformToAPIPayload(queryBuilderPayload);
    setSearchPayload({
      ...searchPayload,
      meta: {
        page: pageMeta
      },
      query_request: {
        ...searchPayload.query_request,
        ...queryAPIPayload
      }
    });
    setEventSaveQueryLoading(true);
  };

  const handleSaveQueryOverlayClose = () => {
    setSaveQueryId('');
    toggleSaveQuery(false);
  };

  const handleSortChange = ({
    orderByName = orderData.orderByName,
    orderByType = orderData.orderByType
  }) => {
    setOrderData({
      order: orderData.order === 'asc' ? 'desc' : 'asc',
      orderByName,
      orderByType
    });
    setSearchPayload({
      ...searchPayload,
      meta: {
        page: pageMeta
      },
      query_request: {
        ...searchPayload.query_request,
        order_by: {
          expression: {
            column_identifier: {
              name: orderByName,
              type: orderByType
            }
          },
          order: orderData.order === 'ASC'.toLowerCase() ? 'DESC' : 'ASC'
        }
      }
    });
    setEventTableLoading(true);
  };

  return (
    <>
      <Heading
        heading={'Events'}
        onTimeRangeChangeCb={loadingCb}
        onRefreshCb={loadingCb}
        defaultCustomTimeRange={
          (startTime && endTime && { start: startTime, end: endTime }) || null
        }
      />
      <SuspenseLoader loading={!!eventSearchLoading} loader={<TableSkeleton />}>
        {eventQueryOptions && (
          <FilterComponent
            filter={queryBuilderPayload}
            options={eventQueryOptions}
            onAdd={handleAdd}
            onUpdate={handleUpdate}
            onDelete={handleDelete}
            onSubmit={handleSubmit}
            onSave={handleSave}
            onClearFilter={handleClearFilter}
          />
        )}
      </SuspenseLoader>
      <SuspenseLoader loading={!!eventTableLoading} loader={<TableSkeleton />}>
        <PaginatedTable
          renderTable={EventsTable}
          data={events}
          total={total}
          pageSize={pageMeta ? pageMeta?.limit : 10}
          pageUpdateCb={pageUpdateCb}
          onSortChange={handleSortChange}
          orderData={orderData}
        />
      </SuspenseLoader>
      <SaveQueryOverlay
        isOpen={isSaveQueryOpen}
        onClose={handleSaveQueryOverlayClose}
        saveQueryId={saveQueryId}
      />
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
    </>
  );
};

export default Events;
