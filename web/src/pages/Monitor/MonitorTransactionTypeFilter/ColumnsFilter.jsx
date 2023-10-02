import React, { useMemo, useState, useCallback } from 'react';
import styles from './index.module.css';
import { MONITOR_OPTION_NAME } from '../constants';
import ValueComponent from '../../../components/ValueComponent';
import SelectComponent from '../../../components/SelectComponent';
import {
  getGlobalQueryOptionsDesc,
  getOparationMapping,
  getValueType
} from '../../../utils/GlobalQuery';

const attrOptions = getGlobalQueryOptionsDesc();
const opOptions = getOparationMapping();

const ColumnFilter = ({ option, onSelectionChange, onValueChange }) => {
  const list = attrOptions.filter(attrOption =>
    opOptions[option.literal_type].includes(attrOption?.id)
  );
  return (
    <div className={styles['columnFilterContainer']}>
      <div className={styles['content']}>{option.alias}</div>
      <SelectComponent
        data={list}
        placeholder={'Select operator'}
        selected={option.op}
        onSelectionChange={onSelectionChange}
        // disabled={option?.name === 'type'} //TODO: Need fix from backend
      />
      {option.op && (
        <ValueComponent
          valueType={option.val_type}
          onValueChange={onValueChange}
          value={option.id}
          valueOptions={option?.id_options}
        />
      )}
    </div>
  );
};

const ColumnsFilter = ({ options, onListChange }) => {
  const optionsToShow = options.filter(option => option.name !== MONITOR_OPTION_NAME);

  const handleSelectionChange = (val, name) => {
    const selectedItem = options.find(option => option.name === name);
    const val_type = getValueType(selectedItem.literal_type, val);
    const updatedItem = {
      ...selectedItem,
      val_type: val_type,
      op: val,
      id: ''
    };
    options.splice(
      options.findIndex(option => option.name === name),
      1,
      updatedItem
    );
    onListChange([...options]);
  };

  const handleValueChange = (val, name) => {
    let newValue;
    const selectedItem = options.find(option => option.name === name);

    if (selectedItem.val_type === 'ID') {
      newValue = {
        long: newValue,
        type: 'LONG'
      };
    }

    if (selectedItem.val_type === 'ID_ARRAY') {
      newValue = val;
    }
    if (selectedItem.val_type !== 'ID_ARRAY') {
      if (selectedItem.val_type.includes('ARRAY')) {
        // newValue = [];
        // if (val?.includes(',')) newValue = val.split(',').map(item => item.trim());
        // else newValue.push(val.trim());
        newValue = val;
      } else {
        newValue = val;
      }
    }

    const updatedItem = {
      ...selectedItem,
      id: newValue
    };
    options.splice(
      options.findIndex(option => option.name === name),
      1,
      updatedItem
    );
    onListChange([...options]);
  };

  const renderColumns = options => {
    return options?.map(option => {
      return (
        <ColumnFilter
          key={option.name}
          option={option}
          onSelectionChange={val => handleSelectionChange(val, option.name)}
          onValueChange={val => handleValueChange(val, option.name)}
        />
      );
    });
  };
  return <div className={styles['columnsFilterContainer']}>{renderColumns(optionsToShow)}</div>;
};

export default ColumnsFilter;
