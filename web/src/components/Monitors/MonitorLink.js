import React from 'react';
import { Link } from 'react-router-dom';

const MonitorLink = ({ monitor, tab, style }) => {
  const handleClick = id => {
    window?.analytics?.track(`Monitor Id Clicked ${id}`, {
      monitorId: monitor?.id
    });
  };
  return (
    <Link
      to={`/monitors/${monitor?.id}/${tab ? tab : ''}`}
      style={{ textDecoration: 'none', ...style }}
      onClick={() => handleClick(monitor?.id)}
    >
      {monitor?.name}
    </Link>
  );
};

export default MonitorLink;
