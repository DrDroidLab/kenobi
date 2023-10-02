import EntitiesTypesTable from './EntitiesTypesTable';
import { Link } from 'react-router-dom';
import React from 'react';

const EntitiesTypeTableCard = ({
  isCard,
  extraHeader,
  entities,
  total,
  pageSize,
  pageUpdateCb,
  tableContainerStyles
}) => {
  const handleCreateEntityClick = () => {
    window?.analytics?.track('Create Entity Button Clicked');
  };
  return (
    <div className="border border-gray-300 rounded-md bg-white">
      <div className="flex justify-between bg-white py-2 rounded-t-md px-4 border-b items-center">
        <Link to={`/entities`} style={{ textDecoration: 'none' }}>
          <div
            className="text-base text-gray-800 hover:text-violet-700"
            style={{ color: 'rgb(149 83 254)' }}
          >
            Entities{' '}
            <span className="text-sm text-gray-500 ml-2" style={{ color: 'rgb(149 83 254)' }}>
              {extraHeader ? ` (${extraHeader})` : null}
            </span>
          </div>
        </Link>

        <div>
          <Link to="/entity/create" onClick={handleCreateEntityClick}>
            <div className="text-sm rounded-lg py-2 px-2 cursor-pointer border-violet-600 text-violet-600 dura hover:text-violet-700 hover:bg-violet-50 flex">
              <span className="w-5 mr-1">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth="2"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
              </span>
              <span>Create Entity</span>
            </div>
          </Link>
        </div>
      </div>
      <EntitiesTypesTable
        entitySummaries={entities}
        total={total}
        pageSize={pageSize}
        pageUpdateCb={pageUpdateCb}
        tableContainerStyles={tableContainerStyles}
      />
    </div>
  );
};

export default EntitiesTypeTableCard;
