import React from 'react';
import { Link } from 'react-router-dom';

const AlertLink = ({ alert }) => {
  return (
    <Link to={`/alerts/${alert?.id}`} style={{ textDecoration: 'none' }}>
      {alert?.name}
    </Link>
  );
};

export default AlertLink;
