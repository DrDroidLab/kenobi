import { useCallback, useState } from 'react';
import { Handle, Position } from 'reactflow';

import redCross from '../../../data/icons8-error-64.png';
import greenTick from '../../../data/green-tick.png';
import greenUpArrow from '../../../data/icons8-green-arrow-48.png';
import redDownArrow from '../../../data/icons8-red-arrow-48.png';

import greenDownArrow from '../../../data/icons8-green-arrow-down-48.png';
import redUpArrow from '../../../data/icons8-red-arrow-up-48.png';

import styles from './index.module.css';

function EventNode({ data }) {
  const clickCb = () => {
    data.clickCb();
  };

  const render = data => {
    let res = [];
    data.metrics?.map((x, idx) => {
      res.push(
        <div
          style={{
            border: '1px solid grey',
            borderTop: '0px',
            borderRadius: idx < data.metrics.length - 1 ? '0px 0px 0px 0px' : '0px 0px 5px 5px',
            backgroundColor: 'white',
            flexDirection: 'inherit',
            display: 'flow-root',
            padding: '2px'
          }}
        >
          <div
            style={{
              height: '100%',
              textAlign: 'left',
              marginLeft: '4px',
              marginRight: '10px',
              fontSize: '7px',
              float: 'left'
            }}
          >
            {x.name}
          </div>
          <div
            style={{
              height: '100%',
              textAlign: 'right',
              marginLeft: '10px',
              marginRight: '4px',
              fontSize: '7px',
              float: 'right',
              color: x.metric_status.toLowerCase()
            }}
          >
            <b>{x.value}</b>
            {x.delta_type && (
              <>
                <div
                  style={{
                    height: '100%',
                    textAlign: 'right',
                    fontSize: '7px',
                    float: 'right',
                    color: x.metric_status.toLowerCase()
                  }}
                >
                  <b>{x.delta}%</b>
                </div>
                <div
                  style={{
                    float: 'right',
                    marginLeft: '5px'
                  }}
                >
                  {x.delta_type == 'UP' && x.metric_status == 'GREEN' && (
                    <img
                      src={greenUpArrow}
                      style={{ width: '8px', height: '8px', marginTop: '1px' }}
                    />
                  )}
                  {x.delta_type == 'DOWN' && x.metric_status == 'GREEN' && (
                    <img
                      src={greenDownArrow}
                      style={{ width: '8px', height: '8px', marginTop: '1px' }}
                    />
                  )}
                  {x.delta_type == 'UP' && x.metric_status == 'RED' && (
                    <img
                      src={redUpArrow}
                      style={{ width: '8px', height: '8px', marginTop: '1px' }}
                    />
                  )}
                  {x.delta_type == 'DOWN' && x.metric_status == 'RED' && (
                    <img
                      src={redDownArrow}
                      style={{ width: '8px', height: '8px', marginTop: '1px' }}
                    />
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      );
    });
    return res;
  };

  return (
    <>
      {data.nodeConnections?.indexOf('IN') > -1 && (
        <Handle type="target" position={Position.Left} />
      )}
      {data.nodeConnections?.indexOf('OUT') > -1 && (
        <Handle type="source" position={Position.Right} />
      )}
      <div className={styles['eventNode']}>
        <div style={{ borderRadius: '10px' }}>
          <div
            style={{
              border: '1px solid grey',
              borderBottom: '0.5px solid black',
              borderRadius: data.metrics?.length ? '5px 5px 0px 0px' : '5px 5px 5px 5px',
              backgroundColor: 'rgb(246 242 254)',
              flexDirection: 'inherit',
              display: 'flow-root',
              padding: '2px'
            }}
          >
            <div
              style={{
                height: '100%',
                textAlign: 'left',
                marginLeft: '5px',
                marginRight: '10px',
                fontSize: '8px',
                float: 'left'
              }}
            >
              {data.workflow_config ? (
                <span
                  style={{
                    cursor: 'pointer',
                    fontWeight: 'bold',
                    textDecoration: 'underline'
                  }}
                  onClick={event => clickCb()}
                >
                  {data.label}
                </span>
              ) : (
                data.label
              )}
            </div>

            <div
              style={{
                height: '100%',
                textAlign: 'right',
                marginRight: '5px',
                marginLeft: '10px',
                fontSize: '8px',
                float: 'right'
              }}
            >
              {data.labelStatus && data.labelStatus.toLowerCase() == 'good' && (
                <img src={greenTick} style={{ width: '8px', height: '8px', marginTop: '2px' }} />
              )}
              {data.labelStatus && data.labelStatus.toLowerCase() == 'bad' && (
                <img src={redCross} style={{ width: '7px', height: '7px', marginTop: '2px' }} />
              )}
            </div>
          </div>
          {render(data)}
        </div>
      </div>
    </>
  );
}

export default EventNode;
