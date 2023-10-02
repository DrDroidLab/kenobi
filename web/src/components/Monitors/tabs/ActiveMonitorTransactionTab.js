import API from '../../../API';
import { useCallback, useEffect, useState } from 'react';
import MonitorTransactionsTable from '../../MonitorTransactions/MonitorTransactionsTable';
import { LinearProgress } from '@mui/material';

const MonitorTransactionsByStatusTab = ({
  loading,
  change,
  monitor_id,
  transaction_status,
  onTabLoadCb,
  onTabChangeCb
}) => {
  const fetchMonitorTransactions = API.useGetMonitorTransactions();

  const [monitorTransactionData, setMonitorTransactionData] = useState([]);
  const [dataFetched, setDataFetched] = useState(false);

  const [total, setTotal] = useState(0);
  const [pageMeta, setPageMeta] = useState({ limit: 10, offset: 0 });

  useEffect(() => {
    if (change && !dataFetched) {
      fetchMonitorTransactions(
        monitor_id,
        {
          transaction_status: transaction_status
        },
        pageMeta,
        resp => {
          setMonitorTransactionData(resp.data?.monitor_transactions);
          setTotal(Number(resp.data?.meta?.total_count));
          setDataFetched(true);
          onTabChangeCb();
        },
        err => {
          setDataFetched(true);
        }
      );
    } else if (loading) {
      setDataFetched(false);
      fetchMonitorTransactions(
        monitor_id,
        {
          transaction_status: transaction_status
        },
        pageMeta,
        resp => {
          setMonitorTransactionData(resp.data?.monitor_transactions);
          setTotal(Number(resp.data?.meta?.total_count));
          setDataFetched(true);
          onTabLoadCb();
        },
        err => {
          setDataFetched(true);
        }
      );
    }
  }, [change, loading]);

  const pageUpdateCb = useCallback(
    (page, successCb, errCb) => {
      setPageMeta(page);
      fetchMonitorTransactions(
        monitor_id,
        {
          transaction_status: transaction_status
        },
        page,
        resp => {
          setMonitorTransactionData(resp.data?.monitor_transactions);
          setTotal(Number(resp.data?.meta?.total_count));
          successCb(resp.data?.monitor_transactions, Number(resp.data?.meta?.total_count));
        },
        err => {
          errCb(err);
        }
      );
    },
    [fetchMonitorTransactions]
  );

  return (
    <>
      {dataFetched ? (
        <MonitorTransactionsTable
          monitor_transactions={monitorTransactionData}
          total={total}
          pageSize={pageMeta ? pageMeta?.limit : 10}
          pageUpdateCb={pageUpdateCb}
          tableContainerStyles={
            monitorTransactionData?.length ? {} : { maxHeight: '35vh', minHeight: '35vh' }
          }
        />
      ) : (
        <>
          <LinearProgress /> <MonitorTransactionsTable triggers={[]} />{' '}
        </>
      )}
    </>
  );
};

export default MonitorTransactionsByStatusTab;
