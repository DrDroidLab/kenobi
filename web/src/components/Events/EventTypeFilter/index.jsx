import React from 'react';
import styles from './index.module.css';
import EventTypeConditions from '../EventTypeConditions';
import SelectComponent from '../../SelectComponent';

const EventTypeFilter = ({
  onEventTypeChange,
  selectedEventType,
  eventTypeOptions,
  attrOptions,
  conditionList,
  onConditionListChange
}) => {
  const handleEventTypeChange = id => {
    onConditionListChange([]);
    onEventTypeChange(id);
  };
  return (
    <div className={styles['container']}>
      <div className={styles['eventTypeSelectionSection']}>
        <div className={styles['content']}>Event Type</div>
        <SelectComponent
          data={eventTypeOptions}
          placeholder="Select event type"
          onSelectionChange={handleEventTypeChange}
          selected={selectedEventType}
          searchable={true}
        />
      </div>
      <div className={styles['eventTypeConditionsSection']}>
        {selectedEventType && (
          <EventTypeConditions
            options={attrOptions}
            conditionList={conditionList}
            onConditionListChange={onConditionListChange}
          />
        )}
      </div>
    </div>
  );
};

export default EventTypeFilter;
