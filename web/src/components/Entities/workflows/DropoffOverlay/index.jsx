import { useEffect, useState } from 'react';
import { getPercentage } from '../../../../utils/utils';
import Overlay from '../../../Overlay';
import styles from './index.module.css';
import apis from '../../../../API';
import { Backdrop, CircularProgress } from '@mui/material';

export const getCurrentDateTimeStr = () => {
  const currentDate = new Date();
  const year = currentDate.getFullYear();
  const month = String(currentDate.getMonth() + 1).padStart(2, '0');
  const day = String(currentDate.getDate()).padStart(2, '0');
  const hours = String(currentDate.getHours()).padStart(2, '0');
  const minutes = String(currentDate.getMinutes()).padStart(2, '0');

  const formattedDate = `${year}-${month}-${day}_${hours}:${minutes}`;
  return formattedDate;
};

const DropoffOverlay = ({
  isOpen,
  previousNodeCount,
  distributions = [],
  clickedEdgeData,
  onClose
}) => {
  const [isDownloading, setIsDownloading] = useState(false);
  const getEdgeMetaData = apis.useGetFunnelDropOff();

  useEffect(() => {
    if (isDownloading) {
      setIsDownloading(true);
      getEdgeMetaData(
        {
          start_event_type_id: clickedEdgeData.start_node_id,
          end_event_type_id: clickedEdgeData.end_node_id,
          funnel_key_name: clickedEdgeData.funnel_key_name,
          filter_key_name: clickedEdgeData.selectedFilterKeyName,
          filter_value: clickedEdgeData.filterValue,
          funnel_event_type_ids: clickedEdgeData.selectedEventTypes
        },
        res => {
          setIsDownloading(false);
          onClose();
          const downloadUrl = window.URL.createObjectURL(new Blob([res.data]));
          const filename =
            'funnel_drop_' +
            clickedEdgeData.funnel_key_name +
            '_' +
            getCurrentDateTimeStr() +
            '.csv';
          const link = document.createElement('a');
          link.href = downloadUrl;
          link.setAttribute('download', filename);
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        },
        err => {
          console.error(err);
          setIsDownloading(false);
          onClose();
        }
      );
    }
  }, [isDownloading]);

  const handleClose = () => {
    onClose();
  };

  const handleDownload = () => {
    setIsDownloading(true);
  };
  return (
    <>
      <Overlay visible={isOpen}>
        <div className={styles['container']}>
          <div className={styles['heading']}>Drop off Distribution</div>
          <div className="content">
            {distributions.length === 0 && (
              <div className="text-xs text-gray-500 font-semibold">No data</div>
            )}
            {distributions.map(distribution => {
              const { count, event_type_name } = distribution;
              return (
                <div
                  key={distribution.id}
                  style={{
                    display: 'flex',
                    flexDirection: 'row',
                    justifyContent: 'space-between',
                    marginTop: '1.5rem',
                    gap: '3rem'
                  }}
                >
                  <div className="text-xs text-gray-500 font-semibold">{event_type_name}</div>
                  <div className="text-xs text-gray-500 font-semibold">
                    {getPercentage({ value: count, total: previousNodeCount })}%
                  </div>
                </div>
              );
            })}
          </div>
          <div className={styles['actions']}>
            {distributions.length > 0 && (
              <button
                className={
                  'text-xs mr-2 bg-white hover:bg-gray-800 text-gray-500 py-1 px-1 border rounded shadow'
                }
                onClick={handleDownload}
              >
                Download csv
              </button>
            )}
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
      <Backdrop
        sx={{ zIndex: theme => theme.zIndex.drawer, position: 'fixed', top: '0px', left: '0px' }}
        open={isDownloading}
      >
        <CircularProgress />
      </Backdrop>
    </>
  );
};

export default DropoffOverlay;
