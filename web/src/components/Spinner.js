import React from 'react';
import spinner from '../data/spinner.gif';

const Spinner = () => (
  <div style={{ textAlign: 'center' }}>
    <img src={spinner} alt="Loading..." />
  </div>
);

export default Spinner;
