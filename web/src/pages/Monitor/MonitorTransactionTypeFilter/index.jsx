import React from 'react';
import styles from './index.module.css';
import ColumnsFilter from './ColumnsFilter';
import AttributesFilter from './AttributesFilter';
import CheckboxComponent from '../../../components/CheckboxComponent';
import cx from 'classnames';
const MonitorTransactionTypeFilter = ({
  columnOptions,
  attributeOptions,
  onColumnListChange,
  onAttributeListChange,
  attributeList,
  isInactive,
  onInactiveChange
}) => {
  const handleCheckboxChange = e => {
    onInactiveChange(e.target.checked);
  };
  return (
    <div className={styles['container']}>
      <div className={styles['monitorTransactionTypeFilterSection']}>
        <ColumnsFilter options={columnOptions} onListChange={onColumnListChange} />
        {/* <CheckboxComponent label="Inactive" checked={isInactive} onChange={handleCheckboxChange} /> */}
      </div>
      <div
        className={cx(styles['monitorTransactionTypeFilterSection'], styles['additionalFilter'])}
      >
        <AttributesFilter
          options={attributeOptions}
          list={attributeList}
          onListChange={onAttributeListChange}
        />
      </div>
    </div>
  );
};

export default MonitorTransactionTypeFilter;
