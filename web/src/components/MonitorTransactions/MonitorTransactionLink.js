import React from 'react';
import { Link } from 'react-router-dom';

const MonitorTransactionLink = ({ monitor_transaction, tab, style }) => {
  return (
    <Link
      to={`/monitor-transactions/${monitor_transaction?.id}/${tab ? tab : ''}`}
      style={{ textDecoration: 'none', ...style }}
    >
      {monitor_transaction?.transaction}
    </Link>
  );
};

export default MonitorTransactionLink;
