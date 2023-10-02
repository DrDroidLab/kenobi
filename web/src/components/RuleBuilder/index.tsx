import React from 'react';
import SelectComponent from '../SelectComponent';
import styles from './index.module.css';
import cross from '../../data/cross.svg';
import ValueComponent from '../ValueComponent';

const RuleBuilder = ({ filter, options, onChange, onDelete }) => {
  const handleLhsChange = (value, option) => {
    onChange({
      key: 'lhs',
      value: value,
      option: option
    });
  };
  return (
    <>
      {!filter?.hide && (
        <div className={styles['_rule__container']}>
          <SelectComponent
            searchable
            data={options}
            placeholder="Select key"
            selected={filter.lhs}
            onSelectionChange={(value, option) => handleLhsChange(value, option)}
          />
          {filter.lhs && (
            <SelectComponent
              data={filter.operators}
              placeholder="Select Operator"
              selected={filter.op}
              onSelectionChange={(value, option) =>
                onChange({
                  key: 'op',
                  value: value,
                  option: option
                })
              }
            />
          )}
          {filter.op && (
            <ValueComponent
              valueType={filter.rhsType}
              valueOptions={filter?.rhsOptions}
              onValueChange={value =>
                onChange({
                  key: 'rhs',
                  value: value
                })
              }
              value={filter.rhs}
            />
          )}

          <div>
            <img
              className={styles['_cross__icon']}
              src={cross}
              alt="cancel"
              width="18px"
              height="18px"
              onClick={() => onDelete()}
            />
          </div>
        </div>
      )}
    </>
  );
};

export default RuleBuilder;
