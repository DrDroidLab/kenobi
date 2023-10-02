import { useState } from 'react';
import Heading from '../../components/Heading';
import PanelConfig from './PanelConfig';
import PanelPlot from './PanelPlot';
import styles from './index.module.css';

const CreatePanel = () => {
  const [panelData, setPanelData] = useState();
  const [refresh, setRefresh] = useState(false);

  const handleConfigVisualizeSubmit = config => {
    setPanelData({ data: config });
    setRefresh(!refresh);
  };

  const handleTimeRangeChange = () => {
    setRefresh(!refresh);
  };

  return (
    <>
      <Heading
        heading={'Metric Explorer'}
        onTimeRangeChangeCb={handleTimeRangeChange}
        onRefreshCb={handleTimeRangeChange}
      />
      <div className={styles['panel__container']}>
        <div className={styles['panelConfig']}>
          <PanelConfig onVisualize={handleConfigVisualizeSubmit} />
        </div>
        {panelData && (
          <div className={styles['panelPlot']}>
            <PanelPlot panelData={panelData} refresh={refresh} />
          </div>
        )}
      </div>
    </>
  );
};

export default CreatePanel;
