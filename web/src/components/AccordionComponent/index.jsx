import Chevron from './Chevron';
import styles from './index.module.css';
import cx from 'classnames';

const AccordionComponent = ({
  title,
  children,
  onExpandedChange,
  expanded,
  titleClassName,
  headerComponent
}) => {
  const handleToggleBtnClick = () => {
    onExpandedChange(!expanded);
  };
  const customTitleClassName = cx(styles['accordion__title'], titleClassName);
  return (
    <div className={cx(styles['accordion__container'])}>
      <button
        className={cx(styles[`accordion`], {
          [styles[`active`]]: expanded
        })}
        onClick={handleToggleBtnClick}
      >
        <p className={customTitleClassName}>{title}</p>
        <div className={styles['accordion__headerComponent']}>
          {headerComponent}
          <Chevron
            width={10}
            fill={'#777'}
            className={cx(styles['accordion__icon'], {
              [styles['rotate']]: expanded
            })}
          />
        </div>
      </button>
      {expanded && <div className={styles['accordion__content']}>{children}</div>}
    </div>
  );
};

export default AccordionComponent;
