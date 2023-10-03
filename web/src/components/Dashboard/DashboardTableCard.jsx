import DashboardTable from './DashboardTable';
import { Link } from 'react-router-dom';
import React from 'react';

const DashboardTableCard = ({
  extraHeader,
  dashboards,
  total,
  pageSize,
  pageUpdateCb,
  tableContainerStyles,
  isCard
}) => {
  return (
    <div className="border border-gray-300 rounded-md bg-white">
      <div className="flex justify-between bg-white py-2 rounded-t-md px-4 border-b items-center">
        <Link to={`/dashboards`} style={{ textDecoration: 'none' }}>
          <div
            className="text-base text-gray-800 hover:text-violet-700"
            style={{ color: 'rgb(149 83 254)' }}
          >
            Dashboards{' '}
            <span className="text-sm text-gray-500 ml-2" style={{ color: 'rgb(149 83 254)' }}>
              {extraHeader ? ` (${extraHeader})` : null}
            </span>
          </div>
        </Link>
      </div>
      <DashboardTable
        dashList={dashboards}
        total={total}
        pageSize={pageSize}
        pageUpdateCb={pageUpdateCb}
        tableContainerStyles={tableContainerStyles}
        isCard={isCard}
      />
    </div>
  );
};

export default DashboardTableCard;
