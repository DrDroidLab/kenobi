import React from 'react';
import styles from './index.module.css';
import cx from 'classnames';
import QueryBuilder from '../../components/QueryBuilder/index.tsx';
import { CircularProgress } from '@mui/material';

const FilterComponent = ({
  filter,
  options,
  onAdd,
  onUpdate,
  onDelete,
  onSubmit,
  onSave,
  onClearFilter,
  isGroupEnabled,
  onExport,
  exportLoading,
  containerClassName,
  queryBuilderClassName,
  headerName
}) => {
  const { id, filters } = filter;
  const handleClearFilter = () => {
    onUpdate({ id, type: 'filters', value: [] });
    onUpdate({ id, type: 'op', value: 'AND' });
    onClearFilter();
  };

  const containerClass = cx(styles['_container'], containerClassName);
  return (
    <div className={containerClass}>
      {headerName && <div className={styles['header']}>{headerName}</div>}
      {typeof onClearFilter === 'function' && (
        <div className={styles['_events__section']}>
          <div className={styles['content']}></div>
          <div onClick={handleClearFilter}>
            <span className={cx(styles['content'], styles['clearFilter'])}>
              <span>Clear Filter </span>
              <span className={styles['clearClose']}>X</span>
            </span>
          </div>
        </div>
      )}
      <div className={styles['_filter__section']}>
        <QueryBuilder
          isGroupEnabled={isGroupEnabled}
          filter={filter}
          options={options}
          onAdd={onAdd}
          onUpdate={onUpdate}
          onDelete={onDelete}
          queryBuilderClassName={queryBuilderClassName}
        />
      </div>
      <div className={styles['_submit__section']}>
        <>
          {typeof onSubmit === 'function' && (
            <button
              className="text-xs bg-white hover:bg-gray-800 text-gray-500 py-1 px-1 border border-gray-400 rounded shadow mr-2"
              onClick={onSubmit}
            >
              Submit
            </button>
          )}
          {typeof onSave === 'function' && (
            <button
              className="text-xs bg-white hover:bg-gray-800 text-gray-500 py-1 px-1 border border-gray-400 rounded shadow mr-2"
              onClick={onSave}
            >
              Save
            </button>
          )}
          {typeof onExport === 'function' && (
            <button
              className="text-xs bg-white hover:bg-gray-800 text-gray-500 py-1 px-1 border border-gray-400 rounded shadow"
              onClick={onExport}
            >
              Export
            </button>
          )}
          {exportLoading && (
            <CircularProgress
              style={{
                marginLeft: '12px'
              }}
              size={20}
            />
          )}
        </>
      </div>
    </div>
  );
};

export default FilterComponent;
