import React, { useCallback } from 'react';
import styles from './index.module.css';
import SelectComponent from '../SelectComponent';
import { debounce } from '../../utils/utils';

export const SearchComponent = ({
  options,
  selectedOption,
  onSelectionChange,
  onSearchChange,
  searchedValue,
  selectDisabled,
  selectPlaceholder
}) => {
  const handleChange = useCallback(
    debounce(event => onSearchChange(event.target.value, selectedOption)),
    []
  );
  return (
    <div className={styles['container']}>
      <SelectComponent
        data={options}
        selected={selectedOption}
        disabled={selectDisabled}
        onSelectionChange={onSelectionChange}
        placeholder={selectPlaceholder}
        containerClassName={styles['container__select']}
      />
      <input
        type="text"
        placeholder="Search..."
        name="search"
        onChange={handleChange}
        value={searchedValue}
        className={styles['container__input']}
        autoComplete="off"
      />
    </div>
  );
};
