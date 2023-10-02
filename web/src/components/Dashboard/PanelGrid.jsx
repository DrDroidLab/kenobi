import PanelPlot from './PanelPlot';
import FunnelView from '../Entities/workflows/FunnelView';
import BuilderView from '../Entities/workflows/BuilderView';
import styles from './index.module.css';
import Funnel from '../Entities/workflows/Funnel';

const PanelGrid = ({ panelDataList, refresh, startTime, name }) => {
  return (
    <div>
      <div className={styles['container']}>
        {panelDataList.map(panelData =>
          panelData.data.type == 'FUNNEL' ? (
            <Funnel funnelConfig={panelData.data.funnel} refresh={refresh} name={name} />
          ) : panelData.data.type == 'WORKFLOW' ? (
            <BuilderView builderConfig={panelData.data.workflow} refresh={refresh} />
          ) : (
            <PanelPlot
              panelData={panelData}
              refresh={refresh}
              showTitle={false}
              startTime={startTime}
            />
          )
        )}
      </div>
    </div>
  );
};

export default PanelGrid;
