import React from 'react';
import SelectComponent from '../SelectComponent';
import styles from './index.module.css';
import RuleBuilder from '../RuleBuilder/index.tsx';
import { getOperatorOptions, getValueType, groupOptions } from '../../utils/GlobalQuery';
import cx from 'classnames';

export const QUERY_BUILDER_ID = '1';

const QueryBuilder = ({
  filter,
  onAdd,
  onUpdate,
  onDelete,
  options,
  isGroupEnabled = true,
  queryBuilderClassName
}) => {
  if (!filter?.id) filter.id = QUERY_BUILDER_ID;
  const { id, lhs, op, rhs, filters } = filter;

  const handleGroupAdd = id => {
    onAdd({ id, isGroup: true });
  };
  const handleGroupChange = (id, value) => {
    onUpdate({ id, type: 'op', value });
  };

  const handleGroupDelete = (id, isGroup) => {
    onDelete({ id, isGroup });
  };

  const handleRuleAdd = id => {
    onAdd({ id });
  };
  const handleRuleChange = ({ id, key, value, item, filter }) => {
    if (key === 'lhs') {
      const operators = getOperatorOptions(item.subLabel);
      if (!!item?.id_option) {
        const optionMap = item?.id_option?.[`${item?.id_option?.type.toLowerCase()}_options`];
        const options = Object.entries(optionMap).map(([key, value]) => {
          return { id: key, label: value };
        });
        onUpdate({ id, type: 'rhsOptions', value: options });
      }
      onUpdate({ id, type: 'lhsType', value: item.subLabel });
      onUpdate({ id, type: 'operators', value: operators });
      onUpdate({ id, type: 'op', value: '' });
      onUpdate({ id, type: 'rhs', value: '' });
      onUpdate({ id, type: 'rhsType', value: '' });
      onUpdate({ id, type: 'path', value: item?.path });
      onUpdate({ id, type: 'optionType', value: item.optionType });
    }
    if (key === 'op') {
      const valueType = getValueType(filter.lhsType, value);
      onUpdate({ id, type: 'rhsType', value: valueType });
      onUpdate({ id, type: 'rhs', value: '' });
    }
    onUpdate({ id, type: key, value });
  };
  const handleRuleDelete = ({ id }) => {
    onDelete({ id });
  };

  const containerClassName = cx(styles['_container'], queryBuilderClassName);
  return (
    <div>
      {filters && (
        <div className={containerClassName}>
          <div className={styles['_group__container']}>
            {filters?.length >= 2 && (
              <SelectComponent
                data={groupOptions()}
                placeholder="Select an operator"
                selected={op}
                onSelectionChange={value => handleGroupChange(id, value)}
              />
            )}
            <div>
              <>
                <button
                  onClick={() => handleRuleAdd(id)}
                  className="text-xs  hover:bg-gray-800 text-gray-500 py-1 px-1 rounded shadow pl-4"
                >
                  + Add Rule
                </button>
                {isGroupEnabled && (
                  <button
                    onClick={() => handleGroupAdd(id)}
                    className="text-xs  hover:bg-gray-800 text-gray-500 py-1 px-1  rounded shadow pl-4"
                  >
                    + Add Group
                  </button>
                )}
              </>
              {id !== QUERY_BUILDER_ID && (
                <button
                  style={{ marginLeft: '16px' }}
                  onClick={() => handleGroupDelete(id, true)}
                  className="text-xs hover:bg-gray-800 text-gray-500 py-1 px-1 rounded shadow pl-4"
                >
                  Delete
                </button>
              )}
            </div>
          </div>
          <div>
            {filters?.map(item => {
              return (
                <div className={styles['_rules__container']} key={item.id}>
                  {Object.keys(item)?.includes('lhs') && (
                    <RuleBuilder
                      filter={item}
                      options={options}
                      onChange={({ key, value, option }) =>
                        handleRuleChange({
                          id: item.id,
                          key,
                          value,
                          item: option,
                          filter: item
                        })
                      }
                      onDelete={() => handleRuleDelete({ id: item.id })}
                    />
                  )}
                  <QueryBuilder
                    options={options}
                    filter={item}
                    onAdd={onAdd}
                    onUpdate={onUpdate}
                    onDelete={onDelete}
                  />
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryBuilder;
