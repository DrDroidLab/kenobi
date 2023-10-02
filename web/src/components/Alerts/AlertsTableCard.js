import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import AlertsTable from './AlertsTable';
import { Link } from 'react-router-dom';

const AlertsTableCard = ({
  extraHeader,
  alerts,
  total,
  pageSize,
  pageUpdateCb,
  tableContainerStyles
}) => {
  return (
    <div className="border border-gray-300 rounded-md bg-white">
      <div className="flex justify-between bg-white py-3 rounded-t-md px-4 border-b items-center">
        <Link to={`/alerts`} style={{ textDecoration: 'none' }}>
          <div className="text-base text-gray-800 hover:text-violet-700">
            Alerts{' '}
            <span className="text-sm text-gray-500 ml-2">
              {extraHeader ? ` (${extraHeader})` : null}
            </span>
          </div>
        </Link>
        <div></div>
      </div>

      <AlertsTable
        alerts={alerts}
        total={total}
        pageSize={pageSize}
        pageUpdateCb={pageUpdateCb}
        tableContainerStyles={tableContainerStyles}
      />
    </div>
  );
};

export default AlertsTableCard;
