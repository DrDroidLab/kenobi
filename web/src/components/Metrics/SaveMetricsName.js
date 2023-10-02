// import Button from 'react-bootstrap/Button';
// import Modal from 'react-bootstrap/Modal';
import React, { useState } from 'react';
import API from '../API';
import { useNavigate } from 'react-router-dom';

function SaveMetricsName(props) {
  let navigate = useNavigate();
  const createPanelAPI = API.useCreatePanel();

  const goToMetricsList = () => {
    navigate(`/${props.workflow_id}/metrics-list`);
  };
  let createPanel = () => {
    if (!panelName) {
      alert('Please enter panel name');
      return;
    }
    let data = {
      panel: {
        name: panelName,
        workflow_id: props.workflow_id,
        config: {
          type: 'CHART',
          chart_type: props.selectedChartType,
          metric_expressions: props.filterdata.metric_expressions
        }
      }
    };
    createPanelAPI(data, response => {
      goToMetricsList();
      props.onHide();
    });
  };
  const [panelName, setPanelName] = useState([]);

  let handlePanelNameChange = e => {
    setPanelName(e.target.value);
  };

  return (
    <Modal {...props} size="md" aria-labelledby="contained-modal-title-vcenter" centered>
      <Modal.Header closeButton>
        <Modal.Title id="contained-modal-title-vcenter">Save Metrics</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div className="inputWrap">
          <label>Enter name</label>
          <input placeholder="Enter name" onChange={handlePanelNameChange} />
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="light" onClick={props.onHide}>
          Close
        </Button>
        <Button onClick={createPanel}>Create</Button>
      </Modal.Footer>
    </Modal>
  );
}

export default SaveMetricsName;
