import React, { useState, useEffect } from 'react';
import styles from './index.module.css';
import cx from 'classnames';
import { randomString } from '../../../utils/utils';
import SelectComponent from '../../../components/SelectComponent';
import {
  getGlobalQueryOptionsDesc,
  getOparationMapping,
  getValueType
} from '../../../utils/GlobalQuery';
import ValueComponent from '../../../components/ValueComponent';
import cross from '../../../data/cross.svg';

const gloabalattrOptions = getGlobalQueryOptionsDesc();
const opOptions = getOparationMapping();

const AttributeFilter = ({
  onAttributeChange,
  selectedAttribute,
  selectedOperator,
  selectedValue,
  onOperatorChange,
  onValueChange,
  operators,
  valueType,
  typeOptions,
  onSelectedTypeChange,
  selectedType,
  attrOptions,
  onRemove
}) => {
  return (
    <div className={styles['attributeTypeContainer']}>
      <SelectComponent
        data={typeOptions}
        placeholder="Select type"
        onSelectionChange={onSelectedTypeChange}
        selected={selectedType}
        searchable={true}
      />
      {selectedType && (
        <SelectComponent
          data={attrOptions}
          placeholder="Select attribute"
          onSelectionChange={onAttributeChange}
          selected={selectedAttribute}
          searchable={true}
        />
      )}
      {selectedAttribute && (
        <SelectComponent
          data={operators}
          placeholder="Select Operator"
          onSelectionChange={onOperatorChange}
          selected={selectedOperator}
        />
      )}

      {selectedOperator && (
        <ValueComponent valueType={valueType} onValueChange={onValueChange} value={selectedValue} />
      )}
      <img
        className={styles['crossIcon']}
        src={cross}
        alt="cancel"
        width="18px"
        height="18px"
        onClick={onRemove}
      />
    </div>
  );
};

const AttributesFilter = ({ options, list, onListChange, fixedOperators = [] }) => {
  const handleAddConditionClick = () => {
    const primaryLabel = options.find(
      option => option.path === 'primary_event_attribute'
    ).path_alias;
    const secondaryLabel = options.find(
      option => option.path === 'secondary_event_attribute'
    ).path_alias;

    onListChange([
      ...list,
      {
        id: randomString(),
        name: '',
        path: '',
        op: '',
        literal_type: '',
        value: '',
        path_alias: '',
        attributeOptions: [],
        operators: [],
        typeOptions: [
          {
            label: primaryLabel,
            id: 'primary_event_attribute'
          },
          {
            label: secondaryLabel,
            id: 'secondary_event_attribute'
          }
        ]
      }
    ]);
  };

  const handleSelectedTypeChange = (val, id) => {
    const selectedList = list.find(item => item.id === id);
    const selectedAttrOptions = options.reduce((acc, option) => {
      if (option.path === val) {
        return [
          ...acc,
          {
            label: option.name,
            id: option.name
          }
        ];
      }
      return acc;
    }, []);
    // setAttrOptions(selectedAttrOptions);
    list.splice(
      list.findIndex(condItem => condItem.id === id),
      1,
      {
        ...selectedList,
        path: val,
        name: '',
        op: '',
        literal_type: '',
        value: '',
        path_alias: '',
        attributeOptions: selectedAttrOptions
      }
    );
    onListChange([...list]);
  };

  const handleAttributeChange = (val, id) => {
    const selectedList = list.find(item => item.id === id);
    const selectedOption = options.find(item => item.name === val);
    const operators = gloabalattrOptions.filter(option =>
      opOptions[selectedOption.literal_type].includes(option?.id)
    );
    list.splice(
      list.findIndex(item => item.id === id),
      1,
      {
        ...selectedList,
        name: val,
        op: '',
        literal_type: '',
        value: '',
        path_alias: '',
        operators: fixedOperators && fixedOperators.length > 0 ? fixedOperators : operators
      }
    );

    onListChange([...list]);
  };

  const handleOperatorChange = (val, id) => {
    const selectedList = list.find(item => item.id === id);
    const selectedOption = options.find(item => item.name === selectedList.name);
    const valueType = getValueType(selectedOption.literal_type, val);

    let defaultValue = '';
    if (valueType == 'BOOLEAN') {
      defaultValue = false;
    }

    list.splice(
      list.findIndex(item => item.id === id),
      1,
      {
        ...selectedList,
        op: val,
        literal_type: valueType,
        value: defaultValue,
        path_alias: ''
      }
    );
    // setValueType(valueType);
    onListChange([...list]);
  };
  const handleValueChange = (val, id) => {
    let newValue;
    const selectedList = list.find(item => item.id === id);
    // check for array cases
    if (selectedList.literal_type.includes('ARRAY')) {
      // newValue = [];
      // if (val.includes(',')) newValue = val.split(',').map(item => item.trim());
      // else newValue.push(val.trim());
      newValue = val;
    } else {
      newValue = val;
    }
    list.splice(
      list.findIndex(condItem => condItem.id === id),
      1,
      {
        ...selectedList,
        value: newValue,
        path_alias: ''
      }
    );
    onListChange([...list]);
  };
  const handleRemove = id => {
    const updatedList = list.filter(item => item.id !== id);
    onListChange([...updatedList]);
  };

  const renderAttributeList = list => {
    return list.map(item => (
      <AttributeFilter
        key={item.id}
        selectedAttribute={item.name}
        selectedOperator={item.op}
        selectedValue={item.value}
        onAttributeChange={val => handleAttributeChange(val, item.id)}
        onOperatorChange={val => handleOperatorChange(val, item.id)}
        onValueChange={val => handleValueChange(val, item.id)}
        operators={item?.operators}
        valueType={item.literal_type}
        typeOptions={item?.typeOptions}
        onSelectedTypeChange={val => handleSelectedTypeChange(val, item.id)}
        onRemove={() => handleRemove(item.id)}
        selectedType={item.path}
        attrOptions={item?.attributeOptions}
      />
    ));
  };

  return (
    <div className={styles['container']}>
      {list?.length >= 1 && <div className={styles['content']}>Filters</div>}
      <div className={styles['attributesTypeContainer']}>
        {list?.length >= 1 && renderAttributeList(list)}
        <div
          className={cx(styles['content'], styles['addConditionStyle'])}
          onClick={handleAddConditionClick}
        >
          <b>+</b> Add filters
        </div>
      </div>
    </div>
  );
};

export default AttributesFilter;
