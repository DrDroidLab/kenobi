import React from 'react';
import styles from './index.module.css';

const TabContent = props => {
  const { id, title, content } = props;

  return (
    <div className={styles['content']} key={id}>
      <div className={styles['segmentTitle']}>
        <h1>{id}</h1>
        <hr></hr>
      </div>
      {
        <div>
          <p className={styles['title']}>{title}</p>
          <p>{content}</p>
        </div>
      }
    </div>
  );
};

export default TabContent;
