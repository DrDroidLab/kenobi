import { useParams } from 'react-router-dom';
import Heading from '../../components/Heading';
import API from '../../API';
import { useCallback, useEffect, useState } from 'react';
import MonitorCard from '../../components/Monitors/MonitorCard';
import TriggersSection from '../../components/Monitors/Triggers/TriggersSection';
import MonitorStatsCard from '../../components/Monitors/MonitorStatsCard';
import SuspenseLoader from '../../components/Skeleton/SuspenseLoader';
import MonitorTransactionsTable from '../../components/MonitorTransactions/MonitorTransactionsTable';
import TableSkeleton from '../../components/Skeleton/TableLoader';
import { transformToAPIPayload } from '../../utils/utils';
import { transformEventQueryOptionsToSelectOptions } from '../../components/Events/utils';
import useDidMountEffect from '../../hooks/useDidMountEffect';
import Toast from '../../components/Toast';
import useToggle from '../../hooks/useToggle';
import styles from './index.module.css';
import useNode from '../../hooks/useNode.ts';
import FilterComponent from '../../components/FilterComponent';
import { validatePayload } from '../../utils/QueryBuilder';
import SaveQueryOverlay from '../../components/Events/SaveQueryOverlay';
import { transformToMTQueryBuilderPayload } from './utils';

const getCurrentDateTimeStr = () => {
  const currentDate = new Date();
  const year = currentDate.getFullYear();
  const month = String(currentDate.getMonth() + 1).padStart(2, '0');
  const day = String(currentDate.getDate()).padStart(2, '0');
  const hours = String(currentDate.getHours()).padStart(2, '0');
  const minutes = String(currentDate.getMinutes()).padStart(2, '0');

  const formattedDate = `${year}-${month}-${day}_${hours}:${minutes}`;
  return formattedDate;
};

const Monitor = () => {
  let { id } = useParams();
  const urlParams = new URLSearchParams(window.location.search);
  const queryParamsId = urlParams.get('id');
  const startTime = urlParams.get('startTime');
  const endTime = urlParams.get('endTime');
  const [validationError, setValidationError] = useState();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState();
  const [monitorName, setMonitorName] = useState('');
  const [monitor, setMonitor] = useState({});
  const [monitorStats, setMonitorStats] = useState({});
  const [total, setTotal] = useState(0);
  const [pageMeta, setPageMeta] = useState({ limit: 10, offset: 0 });
  const [searchPayload, setSearchPayload] = useState({
    meta: {
      page: pageMeta
    }
  });
  const [defaultQueryRequest, setDefaultQueryRequest] = useState();
  const [monitorTransactionData, setMonitorTransactionData] = useState([]);
  const [monitorOptionsLoading, setMonitorOptionsLoading] = useState(true);
  const [monitorTransactionsLoading, setMonitorTransactionsLoading] = useState(false);
  const [monitorLoading, setMonitorLoading] = useState(true);
  const [monitorSaveQueryLoading, setMonitorSaveQueryLoading] = useState(false);

  const [monitorQueryOptions, setMonitorQueryOptions] = useState();
  const { isOpen, toggle } = useToggle();
  const { isOpen: isSaveQueryOpen, toggle: toggleSaveQuery } = useToggle();
  const [orderData, setOrderData] = useState({ orderByName: '', order: '' });
  const [saveQueryId, setSaveQueryId] = useState();
  const [exportLoading, setExportLoading] = useState(false);
  const [queryBuilderPayload, setQueryBuilderPayload] = useState({
    op: 'AND',
    filters: []
  });
  const { insertNode, deleteNode, updateNode } = useNode();
  const fetchMonitors = API.useFetchMonitorDefinition();
  const fetchMonitorTransactionsSearch = API.useGetMonitorTransactionSearch();
  const fetchMonitorTransactionsExport = API.useGetMonitorTransactionExport();
  const fetchMonitorTransactionsSearchOptions = API.useMTSearchOptions();
  const fetchMonitorQuerySave = API.useSaveMonitorQuery();

  useDidMountEffect(() => {
    if (monitorSaveQueryLoading) {
      fetchMonitorQuerySave(
        searchPayload,
        res => {
          setMonitorSaveQueryLoading(false);
          setSaveQueryId(res.data?.query_context_id);
          toggleSaveQuery();
        },
        err => {
          setMonitorSaveQueryLoading(false);
          toggleError();
          setSubmitError(err?.err);
        }
      );
    }
  }, [monitorSaveQueryLoading]);

  useEffect(() => {
    if (monitorLoading) {
      fetchMonitors(
        [id],
        {},
        response => {
          if (response.data?.monitor_definitions?.length > 0) {
            setMonitor(response.data?.monitor_definitions[0]?.monitor);
            setMonitorName(response.data?.monitor_definitions[0]?.monitor?.name);
          }
          setMonitorLoading(false);
        },
        err => {
          setMonitorLoading(false);
        }
      );
    }
  }, [monitorLoading]);

  const loadingCb = useCallback(() => {
    setMonitorTransactionsLoading(true);
  }, [monitorLoading]);

  const pageUpdateCb = useCallback(
    (page, successCb, errCb) => {
      setPageMeta(page);
      fetchMonitorTransactionsSearch(
        {
          ...searchPayload,
          meta: {
            page: page
          }
        },
        resp => {
          setMonitorStats(resp.data?.search_result_monitor_stats);
          setMonitorTransactionData(resp.data?.monitor_transaction_details);
          setTotal(Number(resp.data?.meta?.total_count));
          successCb(resp.data?.monitor_transaction_details, Number(resp.data?.meta?.total_count));
        },
        err => {
          errCb(err);
        }
      );
    },
    [fetchMonitorTransactionsSearch]
  );

  useEffect(() => {
    if (monitorTransactionsLoading) {
      fetchMonitorTransactionsSearch(
        {
          ...searchPayload,
          meta: {
            page: pageMeta
          }
        },
        resp => {
          setMonitorStats(resp.data?.search_result_monitor_stats);
          setMonitorTransactionData(resp.data?.monitor_transaction_details);
          setTotal(Number(resp.data?.meta?.total_count));
          setMonitorTransactionsLoading(false);
        },
        err => {
          setMonitorTransactionsLoading(false);
          toggleError();
          setSubmitError(err?.err);
        }
      );
    }
  }, [monitorTransactionsLoading]);

  useDidMountEffect(() => {
    if (exportLoading) {
      fetchMonitorTransactionsExport(
        {
          ...searchPayload,
          meta: {
            page: pageMeta
          }
        },
        resp => {
          const downloadUrl = window.URL.createObjectURL(new Blob([resp.data]));
          const filename = 'monitor_transactions_' + getCurrentDateTimeStr() + '.csv';
          const link = document.createElement('a');
          link.href = downloadUrl;
          link.setAttribute('download', filename);
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          setExportLoading(false);
        },
        err => {
          toggleError();
          setSubmitError(err?.err);
          setExportLoading(false);
        }
      );
    }
  }, [exportLoading]);

  useEffect(() => {
    setMonitorOptionsLoading(true);
    fetchMonitorTransactionsSearchOptions(
      {
        id_literal: {
          type: 'LONG',
          long: id
        },
        saved_query_request_context_id: {
          type: 'STRING',
          string: queryParamsId
        }
      },
      res => {
        setMonitorOptionsLoading(false);
        const { default_query_request, monitor_transaction_query_options } = res.data;
        const { column_options, attribute_options_v2 } = monitor_transaction_query_options;
        const transformedOptions = transformEventQueryOptionsToSelectOptions({
          column_options: column_options,
          attribute_options: attribute_options_v2
        });
        const transformedPayload = transformToMTQueryBuilderPayload(
          default_query_request,
          transformedOptions,
          'attribute_identifier_v2',
          'monitor_id'
        );
        setDefaultQueryRequest(default_query_request);
        setQueryBuilderPayload(transformedPayload);
        setMonitorQueryOptions(transformedOptions);
        /////////// By default adding monitor_id with AND operator filter to query request
        const queryRequest = {
          filter: {
            ...default_query_request.filter,
            filters: [default_query_request.filter.filters[0] || []],
            op: 'AND'
          }
        };
        if (default_query_request.filter.filters.slice(1).length > 0) {
          queryRequest.filter.filters.push({
            filters: default_query_request.filter.filters.slice(1),
            op: default_query_request.filter.op
          });
        }
        ////////////
        setSearchPayload({
          ...searchPayload,
          query_request: queryRequest
        });
        setMonitorTransactionsLoading(true);
      },
      err => {
        setMonitorOptionsLoading(false);
        console.error(err);
      }
    );
  }, []);

  const handleClearFilter = () => {
    const transformedPayload = transformToMTQueryBuilderPayload(
      defaultQueryRequest,
      monitorQueryOptions,
      'attribute_identifier_v2',
      'monitor_id'
    );
    setQueryBuilderPayload(transformedPayload);
    setSearchPayload({
      meta: {
        page: pageMeta
      },
      query_request: {
        filter: {
          filters: defaultQueryRequest.filter.filters?.filter(
            query => query.lhs?.column_identifier?.name === 'monitor_id'
          ),
          op: defaultQueryRequest.filter.op
        }
      }
    });
    setOrderData({
      order: '',
      orderByName: '',
      orderByType: ''
    });
    setMonitorTransactionsLoading(true);
  };

  const handleSortChange = ({ orderByName, order }) => {
    setOrderData({
      order,
      orderByName
    });
    setSearchPayload({
      ...searchPayload,
      query_request: {
        ...searchPayload.query_request,
        order_by: {
          expression: {
            column_identifier: {
              name: orderByName
            }
          },
          order: order === 'asc' ? 'ASC' : 'DESC',
          allow_nulls: true,
          nulls_last: order === 'asc' ? false : true
        }
      }
    });
    setMonitorTransactionsLoading(true);
  };

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

  const handleSubmit = () => {
    const valError = validatePayload(queryBuilderPayload);
    if (valError) {
      setValidationError(valError);
      toggle();
      return;
    }
    const queryAPIPayload = transformToAPIPayload(queryBuilderPayload);

    /////////////////// By default adding monitor_id with AND operator filter to query request
    const transformedQueryPayload = {
      filter: {
        filters: [queryAPIPayload.filter.filters[0]],
        op: 'AND'
      }
    };

    if (queryAPIPayload.filter.filters.slice(1).length > 0) {
      transformedQueryPayload.filter.filters.push({
        filters: queryAPIPayload.filter.filters.slice(1),
        op: queryAPIPayload.filter.op
      });
    }
    ///////////////////
    setSearchPayload({
      ...searchPayload,
      query_request: {
        ...searchPayload.query_request,
        ...transformedQueryPayload
      }
    });
    setMonitorTransactionsLoading(true);
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
      query_request: {
        ...searchPayload.query_request,
        ...queryAPIPayload
      }
    });
    setMonitorSaveQueryLoading(true);
  };

  const handleExport = () => {
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
    setExportLoading(true);
  };

  const handleSaveQueryOverlayClose = () => {
    setSaveQueryId('');
    toggleSaveQuery(false);
  };

  return (
    <>
      <SuspenseLoader loading={!!monitorLoading} loader={<TableSkeleton noOfLines={1} />}>
        <Heading
          heading={monitorName}
          subHeading="Monitor"
          onTimeRangeChangeCb={loadingCb}
          onRefreshCb={loadingCb}
          defaultCustomTimeRange={
            (startTime && endTime && { start: startTime, end: endTime }) || null
          }
        />
      </SuspenseLoader>
      <div className={styles['monitorData']}>
        <SuspenseLoader loading={!!monitorLoading} loader={<TableSkeleton noOfLines={1} />}>
          <div className={styles['monitorStats']}>
            <MonitorCard monitor={monitor} />
          </div>
        </SuspenseLoader>
        <div>
          <TriggersSection monitor_id={id} />

          <div className={styles['mt-search']}>
            <div
              className={
                'flex justify-between bg-white py-2 rounded-t-md px-4 border-b items-center ' +
                styles['mt-search-bar']
              }
            >
              <div className={styles['title']}>Monitor Transactions</div>
            </div>

            <SuspenseLoader
              loading={!!monitorOptionsLoading}
              loader={<TableSkeleton noOfLines={2} />}
            >
              {monitorQueryOptions && (
                <FilterComponent
                  filter={queryBuilderPayload}
                  options={monitorQueryOptions}
                  onAdd={handleAdd}
                  onUpdate={handleUpdate}
                  onDelete={handleDelete}
                  onSubmit={handleSubmit}
                  onSave={handleSave}
                  onExport={handleExport}
                  exportLoading={exportLoading}
                  onClearFilter={handleClearFilter}
                />
              )}
            </SuspenseLoader>
            <SuspenseLoader
              loading={!!monitorTransactionsLoading}
              loader={<TableSkeleton noOfLines={1} />}
            >
              <div className={styles['monitorStats']}>
                <MonitorStatsCard monitorStats={monitorStats} />
              </div>
            </SuspenseLoader>
            <SuspenseLoader
              loader={<TableSkeleton noOfLines={4} />}
              loading={!!monitorTransactionsLoading}
              className={styles['mt-table']}
            >
              <MonitorTransactionsTable
                monitor_transactions={monitorTransactionData}
                total={total}
                pageSize={pageMeta ? pageMeta?.limit : 10}
                pageUpdateCb={pageUpdateCb}
                tableContainerStyles={
                  monitorTransactionData?.length ? {} : { maxHeight: '35vh', minHeight: '35vh' }
                }
                onSortChange={handleSortChange}
                orderData={orderData}
              />
            </SuspenseLoader>
          </div>
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
        </div>
      </div>
    </>
  );
};

export default Monitor;
