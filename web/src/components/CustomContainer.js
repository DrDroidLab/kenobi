import * as React from 'react';

const CustomContainer = ({ children }) => {
  return (
    <div
      style={{
        // backgroundColor: '#f9fafc',
        width: '100%',
        // padding: '0px 36px 10px 36px',
        height: 'maxContent',
        minHeight: '100vh',
        position: 'relative'
      }}
    >
      {children}
    </div>
  );
};

export default CustomContainer;
