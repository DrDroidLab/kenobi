import { React, useEffect, useState } from 'react';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Button,
  Checkbox,
  Divider,
  FormControl,
  FormControlLabel,
  getInputLabelUtilityClasses,
  Grid,
  Input,
  InputLabel,
  MenuItem,
  Select,
  Tab,
  TextField,
  Typography,
  RadioGroup,
  Radio
} from '@mui/material';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import '../../css/Alerts.css';
import { useNavigate } from 'react-router-dom';
import API from '../../API';
import ArrowRightAltIcon from '@mui/icons-material/ArrowRightAlt';
import {
  getInputKeyType,
  getInputKeyFilterType,
  groupedData,
  InputTyepMap,
  LiteralMap
} from '../../utils/CreateMonitor';

import styles from '../../css/createMonitor.module.css';

import HelpDrawer from '../help/HelpDrawer';
import EventTypeFilter from '../Events/EventTypeFilter';

function CreateMonitor() {
  const [expanded, setExpanded] = useState(1);
  const [inputFilterList, setinputFilterList] = useState([]);
  const handleAddFilterClick = () => {
    setinputFilterList([
      ...inputFilterList,
      {
        event_key_id: '',
        event_type: '',
        val: '',
        op: 1
      }
    ]);
  };

  const handleFilterChange = (event, index, key) => {
    const { value } = event.target;
    const updateFilterList = [...inputFilterList].map((item, itemIndex) => {
      if (index === itemIndex) {
        item[key] = value;
      }
      return item;
    });
    setinputFilterList(updateFilterList);
  };

  const handleFilterCheckboxChange = (event, index, inputFilter) => {
    let radioButtonValue;
    const { value } = event.target;
    if (value === 'true') radioButtonValue = true;
    else radioButtonValue = false;
    const literalValue = LiteralMap[getInputKeyFilterType(responseData, inputFilter)];
    const updateFilterList = [...inputFilterList].map((item, itemIndex) => {
      if (index === itemIndex) {
        item['val'] = radioButtonValue;
        item['literal'] = {
          literal_type: getInputKeyFilterType(responseData, inputFilter),
          [literalValue]: radioButtonValue
        };
      }
      return item;
    });
    setinputFilterList(updateFilterList);
  };

  const handleFilterInputChange = (event, index, inputFilter) => {
    const { value } = event.target;
    const literalValue = LiteralMap[getInputKeyType(responseData, inputFilter)];
    const updateFilterList = [...inputFilterList].map((item, itemIndex) => {
      if (index === itemIndex) {
        item['val'] = value;
        item['literal'] = {
          literal_type: getInputKeyType(responseData, inputFilter),
          [literalValue]: value
        };
      }
      return item;
    });
    setinputFilterList(updateFilterList);
  };

  const handleFilterRemove = (event, index) => {
    const { value } = event.target;
    const updateFilterList = [...inputFilterList].filter((item, itemIndex) => itemIndex !== index);
    setinputFilterList(updateFilterList);
  };

  const handleAccordionChange = panel_id => () => {
    if (panel_id === expanded) {
      setExpanded(-1);
    } else {
      setExpanded(panel_id);
    }
  };

  const navigate = useNavigate();
  const [isEnabled1, setIsEnabled1] = useState(false);
  const [isEnabled2, setIsEnabled2] = useState(false);

  const handleCheckboxChange1 = event => {
    setIsEnabled1(event.target.checked);
  };
  const handleCheckboxChange2 = event => {
    setIsEnabled2(event.target.checked);
  };
  const [isSetupClicked, setIsSetupClicked] = useState(false);
  const [isSetupClicked2, setIsSetupClicked2] = useState(false);

  const createMonitor = API.useCreateMonitors();
  const getMonitorOptions = API.useGetMonitorOptions();

  const [monitorName, setMonitorName] = useState('');
  const [monitorPrimaryEvent, setMonitorPrimaryEvent] = useState('');
  const [monitorSecondaryEvent, setMonitorSecondaryEvent] = useState('');
  const [monitorMissingEvent, setMonitorMissingEvent] = useState('');
  const [monitorMissingThreshold, setMonitorMissingThreshold] = useState('');
  const [monitorDelayedEvent, setMonitorDelayedEvent] = useState('');
  const [monitorDelayedThreshold, setMonitorDelayedThreshold] = useState('');
  const [monitorDelayedTrigger, setMonitorDelayedTrigger] = useState('');
  const [monitorDelayedResolution, setMonitorDelayedResolution] = useState('');
  const [monitorDelayedMissingEventsFlag, setMonitorDelayedMissingEventsFlag] = useState('exclude');
  const [monitorNotificationChannel, setMonitorNotificationChannel] = useState('SLACK');

  const [responseData, setResponseData] = useState(false);

  const [selectedPrimaryEventType, setselectedPrimaryEventType] = useState('');
  const [selectedSecondaryEventType, setselectedSecondaryEventType] = useState('');

  const [formErrors, setFormErrors] = useState({});
  const [webhookUrl, setWebhookUrl] = useState('');
  const [recipientEmail, setRecipientEmail] = useState('');

  const handleMonitorNameChange = event => {
    const { name, value } = event.target;
    setMonitorName(value);
  };

  const handleEventDataChange = event => {
    event.preventDefault();
    setIsSetupClicked(true);
  };

  useEffect(() => {
    getMonitorOptions(response => {
      let monitorOptions = groupedData(response);
      setResponseData(monitorOptions);
      setWebhookUrl(monitorOptions.notificationMap.SLACK?.webhook_url);
      setRecipientEmail(monitorOptions.notificationMap.EMAIL?.email_address);
    });
  }, []);

  const handleMonitorEvent = event => {
    event.preventDefault();
    const { name, value } = event.target;
    if (name === 'primary_event_value') {
      setMonitorPrimaryEvent(value);
    }
    if (name === 'secondary_event_value') {
      setMonitorSecondaryEvent(value);
    }
  };

  const handleRuleDataChange = event => {
    event.preventDefault();
    setIsSetupClicked2(true);
    const { name, value } = event.target;
    if (event.target[0].checked === true) {
      setMonitorMissingEvent('MISSING_EVENT');
      setMonitorMissingThreshold(event.target[1].value);
      window?.analytics?.track('Missing Trigger');

      if (event.target[2].checked === true) {
        setMonitorDelayedEvent('DELAYED_EVENT');
        setMonitorDelayedTrigger(event.target[3].value);
        setMonitorDelayedThreshold(event.target[4].value);
        setMonitorDelayedResolution(event.target[5].value);
        setMonitorDelayedMissingEventsFlag(event.target[6].value);
        window?.analytics?.track('Missing and Delayed Trigger');
      }
    } else {
      if (event.target[1].checked === true) {
        setMonitorDelayedEvent('DELAYED_EVENT');
        setMonitorDelayedTrigger(event.target[2].value);
        setMonitorDelayedThreshold(event.target[3].value);
        setMonitorDelayedResolution(event.target[4].value);
        setMonitorDelayedMissingEventsFlag(event.target[5].value);
        window?.analytics?.track('Delayed Trigger');
      }
    }

    // Rule Name form value stored
  };

  const handleNotificationsDataChange = event => {
    event.preventDefault();
    const selectedChannel = event.target.value;
    setMonitorNotificationChannel(selectedChannel);

    if (selectedChannel === 'SLACK') {
      setRecipientEmail('');
      window?.analytics?.track('Slack Notification Created');
    } else if (selectedChannel === 'EMAIL') {
      setWebhookUrl('');
      window?.analytics?.track('Email Notification Created');
    }
  };

  const validateForm = () => {
    const errors = {};

    // Validate monitor name
    if (!monitorName) {
      errors.monitorName = 'Please enter a monitor name and unique';
    }

    // Validate primary event value
    if (!monitorPrimaryEvent) {
      errors.monitorPrimaryEvent = 'Please select a primary event value';
    }

    // Validate secondary event value
    if (!monitorSecondaryEvent) {
      errors.monitorSecondaryEvent = 'Please select a secondary event value';
    }

    // Validate rule data
    if (isEnabled1 && (!monitorMissingEvent || !monitorMissingThreshold)) {
      errors.ruleData = 'Please enter missing event trigger data';
    }
    if (
      isEnabled2 &&
      (!monitorDelayedEvent ||
        !monitorDelayedThreshold ||
        !monitorDelayedTrigger ||
        !monitorDelayedResolution)
    ) {
      errors.ruleData = 'Please enter delayed event trigger data';
    }

    // Validate notifications data
    if (monitorNotificationChannel === 'SLACK' && !webhookUrl) {
      errors.webhookUrl = 'Please enter a Slack webhook URL';
    } else if (monitorNotificationChannel === 'EMAIL' && !recipientEmail) {
      errors.recipientEmail = 'Please enter an email recipient';
    }

    setFormErrors(errors);

    return Object.keys(errors).length === 0;
  };
  const hasErrors = Object.keys(formErrors).length > 0;

  const onSubmitCallback = () => {
    const isValid = validateForm();

    if (isValid) {
      let notifications = [];

      if (monitorNotificationChannel === 'SLACK') {
        notifications.push({
          channel: 'SLACK',
          slack_configuration: {
            webhook_url: webhookUrl
          }
        });
      } else if (monitorNotificationChannel === 'EMAIL') {
        notifications.push({
          channel: 'EMAIL',
          email_configuration: {
            recipient_email_id: recipientEmail
          }
        });
      }
      const createPayload = {
        primary_event_key_id: monitorPrimaryEvent,
        secondary_event_key_id: monitorSecondaryEvent,
        name: monitorName,
        is_active: true,
        triggers: [],
        notifications
      };

      if (isEnabled1) {
        createPayload.triggers.push({
          name: monitorName + ' Missing Event Trigger',
          priority: 'TP_0',
          definition: {
            type: monitorMissingEvent,
            missing_event_trigger: {
              transaction_time_threshold: Number(monitorMissingThreshold)
            },
            primary_event_filters: inputFilterList?.filter(
              item => item.event_type === selectedPrimaryEventType
            ),
            secondary_event_filters: inputFilterList?.filter(
              item => item.event_type === selectedSecondaryEventType
            )
          }
        });
      }

      if (isEnabled2) {
        createPayload.triggers.push({
          name: monitorName + ' Delayed Event Trigger',
          priority: 'TP_0',
          definition: {
            type: monitorDelayedEvent,
            delayed_event_trigger: {
              trigger_threshold: Number(monitorDelayedTrigger),
              transaction_time_threshold: Number(monitorDelayedThreshold),
              resolution: Number(monitorDelayedResolution * 60),
              skip_unfinished_transactions: !!(monitorDelayedMissingEventsFlag === 'exclude')
            },
            primary_event_filters: inputFilterList?.filter(
              item => item.event_type === selectedPrimaryEventType
            ),
            secondary_event_filters: inputFilterList?.filter(
              item => item.event_type === selectedSecondaryEventType
            )
          }
        });
      }

      console.log('data', createPayload);
      createMonitor(createPayload, response => {
        console.log(response);
        if (response.data.success) {
          navigate('/monitors');
          window?.analytics?.track('Monitor Created');
        }
      });
    }
  };

  return (
    <div>
      {/* {!isError && ( */}
      <div style={{ padding: '1%', backgroundColor: '#f9fafb' }}>
        <Box
          component="div"
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '20px'
          }}
        >
          <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
            Create Monitor
          </Typography>
        </Box>

        <div style={{ backgroundColor: '#F9FAFB' }}>
          <Grid
            item
            xs={12}
            style={{
              padding: '20px',
              height: '100%'
            }}
          >
            <Grid container spacing={2} alignItems="center" style={{ padding: '8px' }}>
              <Grid item xs={2}>
                <InputLabel htmlFor="name" sx={{ marginRight: '2px', fontWeight: 'bold' }}>
                  Monitor Name
                </InputLabel>
              </Grid>
              <Grid item xs={10}>
                <Input
                  type="text"
                  placeholder="Monitor Name"
                  name="name"
                  onChange={handleMonitorNameChange}
                  fullWidth
                />
              </Grid>
            </Grid>
            <Grid xs={12}>
              <Accordion
                sx={{
                  margin: '15px 0px',
                  borderRadius: '10px'
                }}
                expanded={expanded === 1}
                onChange={handleAccordionChange(1)}
              >
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                  aria-controls="panel1a-content"
                  id="panel1a-header"
                >
                  <Typography>Select Events</Typography>
                </AccordionSummary>
                <AccordionDetails style={{ backgroundColor: 'white' }}>
                  <form onSubmit={handleEventDataChange}>
                    <Grid container>
                      <Grid item xs={12}>
                        <div style={{ marginTop: '2%' }}>
                          <h6 style={{ fontWeight: 'bold', marginTop: '10px' }}>Primary Event</h6>
                          <Grid container spacing={1} style={{ marginTop: '10px' }}>
                            <Grid item xs={5}>
                              <FormControl fullWidth style={{ backgroundColor: '#f9fafb' }}>
                                <InputLabel id="demo-simple-select-label">
                                  Select an event type
                                </InputLabel>
                                <Select
                                  value={selectedPrimaryEventType}
                                  onChange={event => {
                                    setselectedPrimaryEventType(event.target.value);
                                    setMonitorPrimaryEvent('');
                                  }}
                                  labelId="demo-simple-select-label"
                                  id="demo-simple-select"
                                  name="primary_event_type"
                                  label="Select an event type"
                                >
                                  {responseData &&
                                    Object.keys(responseData?.eventTypeMap)?.map(eventTypeName => (
                                      <MenuItem key={eventTypeName} value={eventTypeName}>
                                        {eventTypeName}
                                      </MenuItem>
                                    ))}
                                </Select>
                              </FormControl>
                            </Grid>
                            {selectedPrimaryEventType && (
                              <>
                                <Grid item xs={1} style={{ marginTop: '2%' }}>
                                  <ArrowRightAltIcon fontSize="large" color="action" />
                                </Grid>
                                <Grid item xs={5}>
                                  <FormControl fullWidth style={{ backgroundColor: '#f9fafb' }}>
                                    <InputLabel>Select a key</InputLabel>
                                    <Select
                                      onChange={handleMonitorEvent}
                                      type="number"
                                      label="Select a key"
                                      name="primary_event_value"
                                    >
                                      {responseData?.eventTypeMap[selectedPrimaryEventType]?.map(
                                        ({ key, id }) => (
                                          <MenuItem key={key} value={id}>
                                            {key}
                                          </MenuItem>
                                        )
                                      )}
                                    </Select>
                                  </FormControl>
                                </Grid>
                              </>
                            )}
                          </Grid>
                          <h6 style={{ fontWeight: 'bold', marginTop: '10px' }}>Secondary Event</h6>
                          <Grid container spacing={1} style={{ marginTop: '10px' }}>
                            <Grid item xs={5}>
                              <FormControl fullWidth style={{ backgroundColor: '#f9fafb' }}>
                                <InputLabel>Select an event type</InputLabel>
                                <Select
                                  value={selectedSecondaryEventType}
                                  onChange={event => {
                                    setselectedSecondaryEventType(event.target.value);
                                    setMonitorSecondaryEvent('');
                                  }}
                                  name="secondary_event_type"
                                  label="Select an event type"
                                >
                                  {responseData &&
                                    Object.keys(responseData?.eventTypeMap)?.map(eventTypeName => (
                                      <MenuItem key={eventTypeName} value={eventTypeName}>
                                        {eventTypeName}
                                      </MenuItem>
                                    ))}
                                </Select>
                              </FormControl>
                            </Grid>
                            {selectedSecondaryEventType && (
                              <>
                                <Grid item xs={1} style={{ marginTop: '2%' }}>
                                  <ArrowRightAltIcon fontSize="large" color="action" />
                                </Grid>
                                <Grid item xs={5}>
                                  <FormControl fullWidth style={{ backgroundColor: '#f9fafb' }}>
                                    <InputLabel>Select a key</InputLabel>
                                    <Select
                                      onChange={handleMonitorEvent}
                                      name="secondary_event_value"
                                      type="number"
                                      label="Select a key"
                                    >
                                      {responseData?.eventTypeMap[selectedSecondaryEventType]?.map(
                                        ({ key, id }) => (
                                          <MenuItem key={key} value={id}>
                                            {key}
                                          </MenuItem>
                                        )
                                      )}
                                    </Select>
                                  </FormControl>
                                </Grid>
                              </>
                            )}
                          </Grid>
                        </div>
                      </Grid>
                    </Grid>
                    <br></br>
                    <Button
                      type="submit"
                      variant="contained"
                      sx={{
                        '&.Mui-disabled': {
                          backgroundColor: '#c0c0c0',
                          color: '#fff'
                        }
                      }}
                      disabled={
                        !monitorPrimaryEvent ||
                        !monitorSecondaryEvent ||
                        selectedPrimaryEventType === selectedSecondaryEventType
                      }
                      onClick={handleAccordionChange(2)}
                    >
                      Next Step
                    </Button>
                    {(!monitorPrimaryEvent ||
                      !monitorSecondaryEvent ||
                      selectedPrimaryEventType === selectedSecondaryEventType) && (
                      <span
                        style={{
                          color: '#c0c0c0',
                          marginLeft: '10px',
                          fontStyle: 'italic'
                        }}
                      >
                        You need to select different event type and its value
                      </span>
                    )}
                  </form>
                </AccordionDetails>
              </Accordion>

              {/* Set up trigger Accordion */}
              <Accordion
                sx={{
                  margin: '15px 0px',
                  borderRadius: '10px'
                }}
                disabled={!isSetupClicked}
                expanded={expanded === 2}
                onChange={handleAccordionChange(2)}
                // expanded={expandedAccordion === "panel2a-header"}
                // onChange={(event, isExpanded) =>
                //   setExpandedAccordion(isExpanded ? "panel2a-header" : null)
                // }
              >
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                  // aria-controls="panel1a-content"
                  // id="panel1a-header"
                  disabled={!isSetupClicked}
                >
                  <Typography>Setup Triggers</Typography>
                </AccordionSummary>
                <AccordionDetails style={{ backgroundColor: 'white' }}>
                  <form onSubmit={handleRuleDataChange}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <div style={{ width: '135px' }}>
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={isEnabled1}
                              onChange={handleCheckboxChange1}
                              name="MISSING_EVENT_TT"
                            />
                          }
                          label="Per Event"
                        />
                      </div>
                      {isEnabled1 && (
                        <div className={styles['ruleBox']}>
                          <Typography
                            variant="h6"
                            gutterBottom
                            style={{ marginLeft: 8, fontSize: '14px' }}
                          >
                            Alert if secondary event does not happen within
                            <input
                              type="number"
                              step="any"
                              name="primary_transaction_time_threshold"
                              defaultValue={
                                responseData?.triggerMap?.[0]?.default_missing_event_trigger_config
                                  ?.transaction_time_threshold
                              }
                              style={{ marginLeft: 8, marginRight: 8, border: '1px solid grey' }}
                            />
                            seconds from the primary event
                          </Typography>
                        </div>
                      )}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <div style={{ width: '135px' }}>
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={isEnabled2}
                              onChange={handleCheckboxChange2}
                              name="DELAYED_EVENT_TT"
                            />
                          }
                          label="Aggregated Events"
                        />
                      </div>
                      {isEnabled2 && (
                        <div className={styles['ruleBox']}>
                          <Typography
                            variant="h6"
                            gutterBottom
                            style={{ marginLeft: 8, fontSize: '14px' }}
                          >
                            Alert if for
                            <input
                              type="number"
                              name="trigger_threshold"
                              defaultValue={
                                responseData?.triggerMap?.[1]?.default_delayed_event_trigger_config
                                  ?.trigger_threshold
                              }
                              style={{
                                marginLeft: 8,
                                marginRight: 8,
                                marginBottom: 8,
                                border: '1px solid grey'
                              }}
                            />
                            % of primary events, secondary events do not happen within
                            <input
                              type="number"
                              step="any"
                              name="secondary_transaction_time_threshold"
                              defaultValue={
                                responseData?.triggerMap?.[1]?.default_delayed_event_trigger_config
                                  ?.transaction_time_threshold
                              }
                              style={{ marginLeft: 8, marginRight: 8, border: '1px solid grey' }}
                            />
                            seconds, evaluated every
                            <input
                              type="number"
                              name="resolution"
                              defaultValue={
                                responseData?.triggerMap?.[1]?.default_delayed_event_trigger_config
                                  ?.resolution
                              }
                              style={{ marginLeft: 8, marginRight: 8, border: '1px solid grey' }}
                            />
                            minutes; &nbsp;
                            <Select
                              defaultValue={'exclude'}
                              style={{
                                marginLeft: 8,
                                marginRight: 8,
                                border: '1px solid grey',
                                backgroundColor: 'white'
                              }}
                            >
                              <MenuItem key="exclude" value="exclude">
                                exclude
                              </MenuItem>
                              <MenuItem key="include" value="include">
                                include
                              </MenuItem>
                            </Select>
                            missing secondary events
                          </Typography>
                        </div>
                      )}
                    </div>

                    {(isEnabled1 || isEnabled2) &&
                      inputFilterList.length >= 1 &&
                      inputFilterList.map((inputFilter, inputFilterIndex) => (
                        <Grid container spacing={1} sx={{ marginTop: '5px' }}>
                          <Grid item xs={3}>
                            <FormControl fullWidth style={{ backgroundColor: '#f9fafb' }}>
                              <InputLabel>Select an event type filter</InputLabel>
                              <Select
                                value={inputFilter.event_type}
                                onChange={event => {
                                  handleFilterChange(event, inputFilterIndex, 'event_type');
                                }}
                                name="selected_event_type_filter"
                                label="Select an event type filter"
                              >
                                <MenuItem
                                  key={selectedPrimaryEventType}
                                  value={selectedPrimaryEventType}
                                >
                                  {selectedPrimaryEventType}
                                </MenuItem>
                                <MenuItem
                                  key={selectedSecondaryEventType}
                                  value={selectedSecondaryEventType}
                                >
                                  {selectedSecondaryEventType}
                                </MenuItem>
                              </Select>
                            </FormControl>
                          </Grid>
                          <Grid item xs={3}>
                            {inputFilter.event_type && (
                              <div style={{ display: 'flex', flexDirection: 'row' }}>
                                <ArrowRightAltIcon
                                  color="action"
                                  sx={{ marginTop: '15px', marginRight: '10px' }}
                                />
                                <FormControl fullWidth style={{ backgroundColor: '#f9fafb' }}>
                                  <InputLabel>Select a key</InputLabel>
                                  <Select
                                    value={inputFilter.event_key_id}
                                    onChange={event => {
                                      handleFilterChange(event, inputFilterIndex, 'event_key_id');
                                    }}
                                    name="selected_event_type_key_filter"
                                    label="Select a key"
                                    type="number"
                                  >
                                    {responseData?.eventTriggerFilterMap[
                                      inputFilter.event_type
                                    ]?.map(({ key, id }) => (
                                      <MenuItem key={key} value={id}>
                                        {key}
                                      </MenuItem>
                                    ))}
                                  </Select>
                                </FormControl>
                              </div>
                            )}
                          </Grid>
                          <Grid item xs={4}>
                            {inputFilter.event_key_id && (
                              <>
                                {['STRING', 'LONG', 'DOUBLE'].includes(
                                  getInputKeyType(responseData, inputFilter)
                                ) ? (
                                  <>
                                    <span style={{ marginRight: '10px' }}>=</span>
                                    <input
                                      value={inputFilter?.val}
                                      onChange={event => {
                                        handleFilterInputChange(
                                          event,
                                          inputFilterIndex,
                                          inputFilter
                                        );
                                      }}
                                      placeholder="Filter value"
                                      type={
                                        InputTyepMap[getInputKeyType(responseData, inputFilter)]
                                      }
                                      name="filter_value"
                                      style={{
                                        marginLeft: 8,
                                        marginRight: '50px',
                                        border: '1px solid grey',
                                        height: '55px'
                                      }}
                                    />
                                  </>
                                ) : (
                                  <div
                                    style={{
                                      display: 'flex',
                                      flexDirection: 'row'
                                    }}
                                  >
                                    <span style={{ marginRight: '100px' }}>=</span>
                                    <div style={{ marginRight: '20px' }}>
                                      <input
                                        type="radio"
                                        id="true"
                                        name="boolean"
                                        onChange={event =>
                                          handleFilterCheckboxChange(
                                            event,
                                            inputFilterIndex,
                                            inputFilter
                                          )
                                        }
                                        value={true}
                                      />
                                      <label for="true">True</label>
                                    </div>
                                    <div>
                                      <input
                                        type="radio"
                                        id="false"
                                        name="boolean"
                                        onChange={event =>
                                          handleFilterCheckboxChange(
                                            event,
                                            inputFilterIndex,
                                            inputFilter
                                          )
                                        }
                                        value={false}
                                      />
                                      <label for="false">False</label>
                                    </div>
                                  </div>
                                )}
                              </>
                            )}
                          </Grid>
                          <Grid item xs={2}>
                            <Button onClick={event => handleFilterRemove(event, inputFilterIndex)}>
                              - Remove
                            </Button>
                          </Grid>
                        </Grid>
                      ))}
                    {(isEnabled1 || isEnabled2) && (
                      <Button sx={{ marginBottom: '10px' }} onClick={handleAddFilterClick}>
                        + Add Filter
                      </Button>
                    )}

                    <Button
                      type="submit"
                      variant="contained"
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        '&.Mui-disabled': {
                          backgroundColor: '#c0c0c0',
                          color: '#fff'
                        }
                      }}
                      onClick={handleAccordionChange(3)}
                    >
                      Setup Action
                    </Button>
                    {/* {(!isEnabled1 || !isEnabled2) && (
                      <span
                        style={{
                          color: "#c0c0c0",
                          marginLeft: "10px",
                          fontStyle: "italic",
                        }}
                      >
                        You need to checked atleast one trigger
                      </span>
                    )} */}
                  </form>
                </AccordionDetails>
              </Accordion>

              {/* Set up Actions Accordion */}
              <Accordion
                sx={{
                  margin: '15px 0px',
                  borderRadius: '10px'
                }}
                disabled={!isSetupClicked2}
                expanded={expanded === 3}
                onChange={handleAccordionChange(3)}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon />} disabled={!isSetupClicked2}>
                  <Typography>Setup Actions</Typography>
                </AccordionSummary>
                <AccordionDetails style={{ backgroundColor: 'white' }}>
                  <Grid container spacing={3}>
                    <Grid item xs={1} style={{ marginTop: '14px' }}>
                      <Typography variant="body1">Notify on</Typography>
                    </Grid>
                    <Grid item xs={11}>
                      <form onSubmit={handleNotificationsDataChange}>
                        <Grid container>
                          <Grid item xs={2}>
                            <FormControl fullWidth style={{ backgroundColor: '#f9fafb' }}>
                              <InputLabel>Select a notification type</InputLabel>
                              <Select
                                label="Select a notification type"
                                name="monitor_notification_channel"
                                value={monitorNotificationChannel}
                                onChange={handleNotificationsDataChange}
                              >
                                <MenuItem value="SLACK">Slack</MenuItem>
                                <MenuItem value="EMAIL">Email</MenuItem>
                              </Select>
                            </FormControl>
                          </Grid>
                          <Grid item xs={0.2}></Grid>
                          <Grid item xs={7}>
                            <TextField
                              id="outlined-basic"
                              label={
                                monitorNotificationChannel === 'SLACK'
                                  ? 'Webhook URL'
                                  : 'Recipient email'
                              }
                              variant="outlined"
                              required
                              fullWidth
                              value={
                                monitorNotificationChannel === 'SLACK' ? webhookUrl : recipientEmail
                              }
                              onChange={event =>
                                monitorNotificationChannel === 'SLACK'
                                  ? setWebhookUrl(event.target.value)
                                  : setRecipientEmail(event.target.value)
                              }
                              error={formErrors.webhookUrl || formErrors.recipientEmail}
                              helperText={formErrors.webhookUrl || formErrors.recipientEmail || ' '}
                            />
                          </Grid>
                        </Grid>
                      </form>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>
            <Grid xs={12}>
              <Button
                type="submit"
                variant="contained"
                style={{ backgroundColor: '#9553FE', marginTop: '10px' }}
                onClick={onSubmitCallback}
              >
                Create Monitor
              </Button>
            </Grid>
          </Grid>
        </div>
      </div>
      {/* )} */}
      <Snackbar
        open={hasErrors}
        autoHideDuration={6000}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert severity="error" sx={{ width: '100%' }}>
          {/* Something went wrong. Please contact Administrator */}
          {Object.values(formErrors).map((error, index) => (
            <div key={index}>{error}</div>
          ))}
        </Alert>
      </Snackbar>
    </div>
  );
}

export default CreateMonitor;
