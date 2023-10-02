import { useNavigate, useParams } from 'react-router-dom';
import API from '../../../API';
import { useCallback, useEffect, useState } from 'react';
import TriggersTable from './TriggersTable';
import { LinearProgress } from '@mui/material';
import ArrowDown from '../../../data/arrow-down.svg';
import styles from './index.module.css';
import cx from 'classnames';
import useToggle from '../../../hooks/useToggle';

import TriggerActionOverlay from './TriggerActionOverlay';

const TriggersSection = ({ entity_id, loading, change, onTabLoadCb, onTabChangeCb }) => {
  let navigate = useNavigate();

  const fetchTriggers = API.useGetEntityTriggers();

  const [triggersData, setTriggersData] = useState([]);
  const [triggersCount, setTriggersCount] = useState(0);
  const [dataFetched, setDataFetched] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [isActionOpen, setIsActionOpen] = useState(false);

  const { isOpen, toggle } = useToggle();

  const [total, setTotal] = useState(0);
  const [pageMeta, setPageMeta] = useState({ limit: 10, offset: 0 });

  useEffect(() => {
    if (!dataFetched) {
      fetchTriggers(
        entity_id,
        pageMeta,
        resp => {
          setTriggersData(resp.data?.entity_trigger_notification_details);
          setTriggersCount(resp.data?.entity_trigger_notification_details?.length);
          setTotal(Number(resp.data?.meta?.total_count));
          setDataFetched(true);
        },
        err => {
          setDataFetched(true);
        }
      );
    }
  }, []);

  const pageUpdateCb = useCallback(
    (page, successCb, errCb) => {
      setPageMeta(page);
      fetchTriggers(
        entity_id,
        page,
        resp => {
          setTriggersData(resp.data?.entity_trigger_notification_details);
          setTotal(Number(resp.data?.meta?.total_count));
          setTriggersCount(resp.data?.entity_trigger_notification_details?.length);
          setDataFetched(true);
          successCb(
            resp.data?.entity_trigger_notification_details,
            Number(resp.data?.meta?.total_count)
          );
        },
        err => {
          errCb(err);
        }
      );
    },
    [fetchTriggers]
  );

  const togglePanel = () => {
    setExpanded(!expanded);
  };

  const params = { entity_id: entity_id };

  return (
    <div className={styles['triggerCard']}>
      <div
        className={
          'flex justify-between bg-white py-2 rounded-t-md px-4 border-b items-center ' +
          styles['triggerBar']
        }
      >
        <div className={styles[('title', 'triggerTitle')]}>
          Triggers {triggersCount ? <span className={styles['alias']}>{triggersCount}</span> : ''}
        </div>

        <div className={styles['triggerBarEnd']}>
          <button
            className={styles['greyButton']}
            onClick={() => navigate(`/entity/${entity_id}/triggers/create`)}
          >
            + Create Trigger
          </button>
          <div className={styles['vl']}></div>
          <button onClick={() => togglePanel()}>
            <img
              width="20px"
              height="20px"
              src={ArrowDown}
              className={cx(styles['arrow-down-icon'], {
                [styles['open']]: expanded
              })}
            />
          </button>
        </div>
      </div>
      {expanded ? (
        dataFetched ? (
          <TriggersTable
            triggers={triggersData}
            total={total}
            params={params}
            pageSize={pageMeta ? pageMeta?.limit : 10}
            pageUpdateCb={pageUpdateCb}
            tableContainerStyles={
              triggersData?.length ? {} : { maxHeight: '35vh', minHeight: '35vh' }
            }
          />
        ) : (
          <>
            <LinearProgress /> <TriggersTable />{' '}
          </>
        )
      ) : null}
    </div>
  );
};

export default TriggersSection;
