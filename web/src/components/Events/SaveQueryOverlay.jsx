import React, { useState } from 'react';
import Overlay from '../Overlay';
import styles from './index.module.css';

const SaveQueryOverlay = ({ isOpen, onClose, saveQueryId }) => {
  const [queryId, setQueryId] = useState('');
  const [url, setUrl] = useState('');

  if (queryId !== saveQueryId) {
    setQueryId(saveQueryId);
    setUrl(`${window.location.origin}${window.location.pathname}?id=${saveQueryId}`);
  }
  const handleClose = () => {
    setUrl('');
    onClose();
  };

  const handleCopyClick = url => () => {
    navigator.clipboard.writeText(url);
  };
  return (
    <Overlay visible={isOpen}>
      <div className={styles['overlayContainer']}>
        <header className="text-gray-500">Saved Query</header>
        <div className={styles['contentContainer']}>
          <div className="text-xs text-gray-500">{url}</div>
          <button
            className={
              'text-xs bg-white hover:bg-gray-800 text-gray-500 py-1 px-1 border rounded shadow'
            }
            onClick={handleCopyClick(url)}
          >
            Copy to clipboard
          </button>
        </div>
        <div className={styles['actions']}>
          <button
            className={
              'text-xs bg-white hover:bg-gray-800 text-gray-500 py-1 px-1 border rounded shadow'
            }
            onClick={handleClose}
          >
            Cancel
          </button>
        </div>
      </div>
    </Overlay>
  );
};

export default SaveQueryOverlay;
