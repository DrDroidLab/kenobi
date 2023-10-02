import React from 'react';
import styles from './index.module.css';
import cx from 'classnames';
import { CircularProgress } from '@mui/material';
import MonitorTransactionTypeFilter from '../MonitorTransactionTypeFilter';

const MonitorTransactionFilter = ({
  columnOptions,
  attributeOptions,
  columnList,
  onColumnListChange,
  onAttributeListChange,
  attributeList,
  onSubmit,
  onExport,
  exportLoading,
  onClearFilter,
  isInactive,
  onInactiveChange
}) => {
  return (
    <div className={styles['wrapper']}>
      <div className={styles['mtSection']}>
        {/* <div className={styles['content']}>Monitor Transactions</div> */}
        <div onClick={onClearFilter}>
          <span className={cx(styles['content'], styles['clearFilter'])}>
            <span>Clear Filter</span>
            <span className={styles['clearClose']}>X</span>
          </span>
        </div>
      </div>
      <div className={styles['mtTypeFilterSection']}>
        <MonitorTransactionTypeFilter
          columnOptions={columnOptions}
          attributeOptions={attributeOptions}
          isInactive={isInactive}
          onInactiveChange={onInactiveChange}
          // columnList={columnList}
          onColumnListChange={onColumnListChange}
          onAttributeListChange={onAttributeListChange}
          attributeList={attributeList}
        />
      </div>
      <div className="flex items-center">
        <button
          className="text-xs bg-white hover:bg-gray-800 text-gray-500 py-1 px-1 border border-gray-400 rounded shadow"
          onClick={onSubmit}
          style={{
            marginLeft: '12px',
            marginBottom: '12px'
          }}
        >
          Submit
        </button>
        <button
          className="text-xs bg-white hover:bg-gray-800 text-gray-500 py-1 px-1 border border-gray-400 rounded shadow"
          onClick={onExport}
          style={{
            marginLeft: '12px',
            marginBottom: '12px'
          }}
        >
          Export
        </button>
        {exportLoading ? (
          <CircularProgress
            style={{
              marginLeft: '12px',
              marginBottom: '12px'
            }}
            size={20}
          />
        ) : (
          ''
        )}
      </div>
    </div>
  );
};

export default MonitorTransactionFilter;
