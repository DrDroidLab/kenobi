import React, { useEffect, useRef, useState } from 'react';
import styles from './index.module.css';
import useToggle from '../../hooks/useToggle';
import ArrowDown from '../../data/arrow-down.svg';
import cx from 'classnames';
import useOutsideClick from '../../hooks/useOutsideClick';

const SelectComponent = ({
  data,
  placeholder = 'Select your id',
  onSelectionChange,
  selected,
  disabled = false,
  searchable = false,
  containerClassName = {}
}) => {
  const selectRef = useRef(null);
  const [searchVal, setSearchVal] = useState('');
  const [options, setOptions] = useState(data);
  const { isOpen, toggle } = useToggle();
  const toggleDropdown = () => toggle();
  const _containerClassName = cx(styles['_dropdown__container'], containerClassName);
  useEffect(() => {
    if (data !== options) setOptions(data);
  }, [data]);
  const handleItemClick = (id, item) => {
    onSelectionChange(id, item);
    toggle();
  };

  const returnSubLabel = (data, selected) => {
    let selectedItem = data?.find(item => item.id === selected);
    if (selectedItem && selectedItem.subLabel) {
      return `(${selectedItem.subLabel})`;
    }
    return '';
  };

  const handleSearchChange = event => {
    const searchedVal = event.target.value;
    const values = data.filter(item =>
      item.label.toLowerCase().includes(searchedVal.toLowerCase())
    );
    setSearchVal(searchedVal);
    setOptions(values);
  };

  useOutsideClick(selectRef, () => toggle(false));

  return (
    <div className={_containerClassName} ref={selectRef}>
      <div className={styles['dropdown__header']} onClick={toggleDropdown}>
        {selected ? (
          <>
            <span>{data?.find(item => item.id === selected)?.label}</span> &nbsp;
            {returnSubLabel(data, selected)}{' '}
          </>
        ) : (
          <span>{placeholder}</span>
        )}
        {!disabled && (
          <img
            width="20px"
            height="20px"
            src={ArrowDown}
            className={cx(styles['arrow-down-icon'], {
              [styles['open']]: isOpen
            })}
          />
        )}
      </div>

      {!disabled && (
        <div
          className={cx(styles[`dropdown__body`], {
            [styles['open']]: isOpen
          })}
        >
          {' '}
          {!!searchable && (
            <input
              className={styles['searchContainer']}
              onChange={handleSearchChange}
              value={searchVal}
              type={'text'}
            />
          )}
          {options?.map((item, index) => (
            <div
              className={styles['dropdown__item']}
              onClick={e => handleItemClick(e.target.id, item)}
              id={item.id}
              key={item.id + index}
            >
              <span
                className={cx(styles[`dropdown__item-dot`], {
                  [styles['selected']]: item.id === selected
                })}
              ></span>
              {item.label}&nbsp;
              {item.subLabel ? `(${item.subLabel})` : ''}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SelectComponent;
