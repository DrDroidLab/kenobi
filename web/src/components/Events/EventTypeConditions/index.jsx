import React from 'react';
import styles from './index.module.css';
import EventTypeCondition from '../EventTypeCondition';
import { randomString } from '../../../utils/utils';
import cx from 'classnames';
import {
  getGlobalQueryOptionsDesc,
  getOparationMapping,
  getValueType
} from '../../../utils/GlobalQuery';

const attrOptions = getGlobalQueryOptionsDesc();
const opOptions = getOparationMapping();
const EventTypeConditions = ({ options, conditionList, onConditionListChange }) => {
  const handleEventTypeSelectionChange = (id, conditionId) => {
    let updatedSelectedCondition;
    const selectedCondition = conditionList.find(conditionItem => conditionItem.id === conditionId);
    if (selectedCondition['selectedEventTypeAttr'] == id) {
      updatedSelectedCondition = {
        ...selectedCondition,
        selectedEventTypeAttr: ''
      };
    } else {
      const selectionOption = options.find(option => option.id === id);
      const list = attrOptions.filter(option =>
        opOptions[selectionOption.type].includes(option?.id)
      );
      updatedSelectedCondition = {
        ...selectedCondition,
        selectedEventTypeAttr: id,
        attrOpOptions: list,
        selectedEventAttrOp: '',
        valueType: '',
        attrValue: ''
      };
    }
    conditionList.splice(
      conditionList.findIndex(condItem => condItem.id === conditionId),
      1,
      updatedSelectedCondition
    );
    onConditionListChange([...conditionList]);
  };

  const handleEventAttrOpChange = (id, conditionId) => {
    let updatedSelectedCondition;
    const selectedCondition = conditionList.find(conditionItem => conditionItem.id === conditionId);
    if (selectedCondition['selectedEventAttrOp'] == id) {
      updatedSelectedCondition = {
        ...selectedCondition,
        selectedEventAttrOp: ''
      };
    } else {
      const selectedEventAttrType = options.find(
        option => option.id === selectedCondition['selectedEventTypeAttr']
      ).type;
      const type = getValueType(selectedEventAttrType, id);
      updatedSelectedCondition = {
        ...selectedCondition,
        selectedEventAttrOp: id,
        valueType: type,
        attrValue: ''
      };
    }
    conditionList.splice(
      conditionList.findIndex(condItem => condItem.id === conditionId),
      1,
      updatedSelectedCondition
    );
    onConditionListChange([...conditionList]);
  };

  const handleAttrValueChange = (value, conditionId) => {
    let newValue;
    const selectedCondition = conditionList.find(conditionItem => conditionItem.id === conditionId);
    if (selectedCondition.valueType.includes('ARRAY')) {
      // newValue = [];
      // if (value.includes(',')) newValue = value.split(',').map(item => item.trim());
      // else newValue.push(value.trim());
      newValue = value;
    } else {
      newValue = value;
    }
    const updatedSelectedCondition = {
      ...selectedCondition,
      attrValue: newValue
    };
    conditionList.splice(
      conditionList.findIndex(condItem => condItem.id === conditionId),
      1,
      updatedSelectedCondition
    );
    onConditionListChange([...conditionList]);
  };

  const renderEventAttrConditions = list => {
    return list.map((condition, index) => (
      <EventTypeCondition
        key={condition.id + index}
        options={options}
        eventTypeConditionId={condition.id}
        onRemove={handleRemoveEventTypeCondition}
        selectedEventTypeAttr={condition.selectedEventTypeAttr}
        attrOpOptions={condition.attrOpOptions}
        selectedEventAttrOp={condition.selectedEventAttrOp}
        attrValue={condition.attrValue}
        valueType={condition.valueType}
        onAttrValueChange={val => handleAttrValueChange(val, condition.id)}
        onEventAttrOpChange={id => handleEventAttrOpChange(id, condition.id)}
        onEventTypeSelectionChange={value => handleEventTypeSelectionChange(value, condition.id)}
      />
    ));
  };

  const handleAddConditionClick = () => {
    onConditionListChange([
      ...conditionList,
      {
        id: randomString(),
        selectedEventTypeAttr: '',
        attrOpOptions: [],
        selectedEventAttrOp: '',
        attrValue: '',
        valueType: ''
      }
    ]);
  };

  const handleRemoveEventTypeCondition = id => {
    const updatedConditionList = conditionList.filter(condition => condition.id !== id);
    onConditionListChange([...updatedConditionList]);
  };

  return (
    <div className={styles['container']}>
      {conditionList?.length >= 1 && <div className={styles['content']}>Filters</div>}
      <div className={styles['eventAttributesContainer']}>
        {conditionList?.length >= 1 && renderEventAttrConditions(conditionList)}
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

export default EventTypeConditions;
