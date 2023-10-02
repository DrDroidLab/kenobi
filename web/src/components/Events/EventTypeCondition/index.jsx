import React from 'react';
import styles from './index.module.css';
import cross from '../../../data/cross.svg';
import SelectComponent from '../../SelectComponent';
import ValueComponent from '../../ValueComponent';

const EventTypeCondition = ({
  options,
  eventTypeConditionId,
  onRemove,
  selectedEventTypeAttr,
  attrOpOptions,
  selectedEventAttrOp,
  attrValue,
  valueType,
  onAttrValueChange,
  onEventAttrOpChange,
  onEventTypeSelectionChange
}) => {
  const handleRemoveClick = event => {
    onRemove(event.target.id);
  };
  return (
    <div className={styles['container']}>
      <SelectComponent
        data={options}
        placeholder="Select attribute"
        onSelectionChange={onEventTypeSelectionChange}
        selected={selectedEventTypeAttr}
      />
      {selectedEventTypeAttr && (
        <SelectComponent
          data={attrOpOptions}
          placeholder="Select operator"
          onSelectionChange={onEventAttrOpChange}
          selected={selectedEventAttrOp}
          searchable
        />
      )}
      {selectedEventTypeAttr && selectedEventAttrOp && (
        <>
          <ValueComponent
            valueType={valueType}
            onValueChange={onAttrValueChange}
            value={attrValue}
          />{' '}
        </>
      )}
      <img
        className={styles['crossIcon']}
        src={cross}
        alt="cancel"
        width="18px"
        height="18px"
        id={eventTypeConditionId}
        onClick={handleRemoveClick}
      />
    </div>
  );
};

export default EventTypeCondition;
