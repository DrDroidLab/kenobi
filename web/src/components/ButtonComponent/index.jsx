import React from 'react';
import styles from './index.module.css';
import Check from '../../data/check.svg';
import Settings from '../../data/settings.svg';
import Loading from '../../data/loading.svg';

const Button = ({
  buttonType = 'primary',
  handleClick = () => {},
  label,
  isDisabled = false,
  isLoading = false
}) => {
  return (
    <button
      className={`
                    ${styles['button']}
                    ${styles[`button-${buttonType}`]}
                    ${isDisabled ? styles.disabled : ''}
                `}
      onClick={handleClick}
      disabled={isDisabled || isLoading}
    >
      {isLoading ? (
        <div className={styles['button-loading-container']}>
          <img src={Loading} />
          <span className={styles['button-label']}>Loading...</span>
        </div>
      ) : buttonType === 'success' || buttonType === 'requested' ? (
        <div className={styles['button-success-container']}>
          <img src={Check} className={styles['checkImage']} />
          <span className={styles['button-label']}>{label}</span>
        </div>
      ) : (
        label
      )}
    </button>
  );
};

export default Button;
