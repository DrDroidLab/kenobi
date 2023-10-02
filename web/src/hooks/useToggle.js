import { useState } from 'react';

export default (initialState = false) => {
  const [isOpen, setIsOpen] = useState(initialState);
  const toggle = newVal => {
    typeof newVal === 'boolean' ? setIsOpen(newVal) : setIsOpen(!isOpen);
  };
  return { isOpen, toggle };
};
