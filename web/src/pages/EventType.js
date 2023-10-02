import { useNavigate, useParams } from 'react-router-dom';
import Heading from '../components/Heading';
import API from '../API';
import { useCallback, useEffect, useState } from 'react';
import EventTypeDefinition from '../components/EventType/EventTypeDefinition';
import EventTypeMetrics from '../components/EventType/EventTypeMetrics';
import { TabContext, TabPanel } from '@mui/lab';
import { CircularProgress, Tab } from '@mui/material';
import { styled } from '@mui/material/styles';
import MuiTabList from '@mui/lab/TabList';
import PaginatedTable from '../components/PaginatedTable';
import EventsTable from '../components/Events/EventsTable';

const TabList = styled(MuiTabList)(({ theme }) => ({
  '& .MuiTabs-indicator': {
    display: 'none'
  },
  '& .Mui-selected': {
    backgroundColor: theme.palette.primary.main,
    color: `${theme.palette.common.white} !important`
  },
  '& .MuiTab-root': {
    minHeight: 38,
    minWidth: 130,
    borderRadius: theme.shape.borderRadius
  }
}));

const tabs = ['definition', 'events'];

const getTab = activeTab => {
  if (!activeTab) {
    return 'definition';
  }
  if (!tabs.includes(activeTab)) {
    return 'definition';
  }
  return activeTab;
};

const EventType = () => {
  let { id, tab } = useParams();
  const [tabValue, setTabValue] = useState(getTab(tab));
  let navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [refreshMetrics, setRefreshMetrics] = useState(false);

  const [eventTypeSummary, setEventTypeSummary] = useState({});
  const fetchEventTypeSummary = API.useGetEventTypeSummary();

  const [eventTypeDefinition, setEventTypeDefinition] = useState({});
  const fetchEventTypeDefinition = API.useGetEventTypeDefinition();

  const [events, setEvents] = useState([]);
  const [totalEvents, setTotalEvents] = useState(0);
  const [pageMeta, setPageMeta] = useState({ limit: 10, offset: 0 });
  const fetchEvents = API.useGetEvents();

  const fetchTabData = useCallback(() => {
    if (tabValue === 'definition') {
      fetchEventTypeDefinition(
        [id],
        response => {
          setLoading(false);
          if (response.data?.event_type_definitions?.length > 0) {
            setEventTypeDefinition(response.data?.event_type_definitions[0]);
          }
        },
        err => {
          setLoading(false);
        }
      );
    } else if (tabValue === 'events') {
      fetchEvents(
        {
          meta: {
            page: pageMeta
          },
          event_type_ids: [id]
        },
        res => {
          setLoading(false);
          setTotalEvents(res.data?.meta?.total_count);
          setEvents(res.data?.events);
        },
        err => {
          setLoading(false);
        }
      );
    }
  }, [pageMeta, tabValue, fetchEventTypeDefinition, fetchEvents]);

  useEffect(() => {
    if (loading) {
      setEvents([]);
      fetchEventTypeSummary([id], {}, null, response => {
        if (response.data?.event_type_summary?.length > 0) {
          setEventTypeSummary(response.data?.event_type_summary[0]);
        }
      });
      fetchTabData();
    }
  }, [loading]);

  useEffect(() => {
    if (!loading) {
      fetchTabData();
    }
  }, [tabValue]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    navigate(`/event-types/${id}/${newValue.toLowerCase()}`);
  };

  const loadingCb = useCallback(() => {
    setLoading(true);
    setRefreshMetrics(new Date());
  }, [loading]);

  const pageUpdateCb = useCallback(
    (page, successCb, errCb) => {
      setPageMeta(page);
      fetchEvents(
        {
          meta: {
            page: page
          },
          event_type_ids: [id]
        },
        res => {
          // setTotalEvents(res.data?.meta?.total_count)
          // setEvents(res.data?.events)
          successCb(res.data?.events, Number(res.data?.meta?.total_count));
        },
        err => {
          errCb(err);
        }
      );
    },
    [fetchEvents]
  );

  return (
    <div>
      <Heading
        subHeading="Event Type"
        heading={`${eventTypeSummary?.event_type?.name}`}
        onTimeRangeChangeCb={loadingCb}
        onRefreshCb={loadingCb}
      />
      <TabContext value={tabValue}>
        <TabList onChange={handleTabChange} style={{ marginLeft: '24px', marginTop: '10px' }}>
          <Tab value="definition" label="Definition" />
          <Tab value="events" label="Events" />
          <Tab value="metrics" label="Metrics" />
        </TabList>
        <TabPanel value="definition">
          <EventTypeDefinition eventTypeDefinition={eventTypeDefinition} />
        </TabPanel>
        <TabPanel value="events">
          {loading ? (
            <CircularProgress />
          ) : events?.length > 0 ? (
            <PaginatedTable
              renderTable={EventsTable}
              data={events}
              total={totalEvents}
              pageSize={pageMeta ? pageMeta?.limit : 10}
              pageUpdateCb={pageUpdateCb}
            />
          ) : null}
        </TabPanel>
        <TabPanel value="metrics">
          <EventTypeMetrics
            eventTypeDefinition={eventTypeDefinition}
            refreshMetrics={refreshMetrics}
          />
        </TabPanel>
      </TabContext>
    </div>
  );
};

export default EventType;
