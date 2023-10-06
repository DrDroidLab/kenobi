import React, { Suspense } from 'react';

import SignUp from './pages/SignUp';
import Login from './pages/Login';
import Layout from './Layout';
import BaseLayout from './BaseLayout';
import { Route, Routes } from 'react-router-dom'; // import React Router
// import MetricsList from './components/Metrics/metrics-list';
import RequireAuth from './components/RequireAuth';
import PersistLogin from './components/PersistLogin';
import Workflows from './pages/Workflows';
import ConfirmEmail from './pages/ConfirmEmail';
import AxiosPrivate from './components/AxiosPrivate';
import NotFound from './pages/NotFound';
import Integrations from './components/Integration';

const DataDogIntegration = React.lazy(() =>
  import('./components/Integration/connectors/DataDogIntegration')
);

const NewRelicIntegration = React.lazy(() =>
  import('./components/Integration/connectors/NewRelicIntegration')
);

const Home = React.lazy(() => import('./pages/Home'));
const Events = React.lazy(() => import('./pages/Events'));
const EventType = React.lazy(() => import('./pages/EventType'));
const EventTypes = React.lazy(() => import('./pages/EventTypes'));
const Entities = React.lazy(() => import('./pages/Entity/Entities'));
const CreateEntity = React.lazy(() => import('./components/Entities/CreateEntity'));
const UpdateEntity = React.lazy(() => import('./components/Entities/UpdateEntity'));
const CreateEntityTrigger = React.lazy(() =>
  import('./components/Entities/Triggers/CreateTrigger')
);
const UpdateEntityTrigger = React.lazy(() =>
  import('./components/Entities/Triggers/UpdateTrigger')
);

const Entity = React.lazy(() => import('./pages/Entity/Entity'));
const EntityInstance = React.lazy(() => import('./pages/Entity/EntityInstance'));
const Funnel = React.lazy(() => import('./components/Entities/workflows/Funnel'));
const Builder = React.lazy(() => import('./components/Entities/workflows/Builder'));
const Alerts = React.lazy(() => import('./pages/Alerts'));
const Alert = React.lazy(() => import('./pages/Alert'));
const Dashboards = React.lazy(() => import('./pages/Dashboards'));
const DashboardView = React.lazy(() => import('./components/Dashboard/DashboardView'));
const CreatePanel = React.lazy(() => import('./components/Dashboard/CreatePanel'));
const CreateMonitor2 = React.lazy(() => import('./components/Monitors/CreateMonitor2'));
const CreateTrigger = React.lazy(() => import('./components/Monitors/Triggers/CreateTrigger'));
const UpdateTrigger = React.lazy(() => import('./components/Monitors/Triggers/UpdateTrigger'));
const Monitors = React.lazy(() => import('./pages/Monitors'));
const Monitor = React.lazy(() => import('./pages/Monitor/index'));
const MonitorTransaction = React.lazy(() => import('./pages/MonitorTransaction'));
const ApiTokens = React.lazy(() => import('./components/Apikeys/Apikeys'));

const App = () => {
  return (
    <Routes>
      <Route element={<BaseLayout />}>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/confirm-email/:key?" element={<ConfirmEmail />} />
      </Route>

      <Route element={<PersistLogin />}>
        <Route element={<RequireAuth />}>
          <Route element={<AxiosPrivate />}>
            <Route element={<Layout />}>
              <Route exact path="/" element={<Home />} />
              <Route path="/event-types" element={<EventTypes />} />
              <Route path="/event-types/:id/:tab?" element={<EventType />} />
              <Route path="/events" element={<Events />} />
              <Route path="/funnel" element={<Funnel />} />
              <Route path="/workflow" element={<Builder />} />
              <Route path="/entities" element={<Entities />} />
              <Route path="/dashboards" element={<Dashboards />} />
              <Route path="/dashboard/:id" element={<DashboardView />} />
              <Route path="/metrics-explorer" element={<CreatePanel />} />
              <Route path="/entity/create" element={<CreateEntity />} />
              <Route path="/entity/:id" element={<Entity />} />
              <Route path="/entity/:id/update" element={<UpdateEntity />} />
              <Route path="/entity/:id/triggers/create" element={<CreateEntityTrigger />} />
              <Route path="/entity/:id/triggers/:t_id/update" element={<UpdateEntityTrigger />} />
              <Route path="/monitors" element={<Monitors />} />
              <Route path="/monitors/create" element={<CreateMonitor2 />} />
              <Route path="/monitors/:id/triggers/create" element={<CreateTrigger />} />
              <Route path="/monitors/:id/triggers/:t_id/update" element={<UpdateTrigger />} />
              <Route path="/monitors/:id/:tab?" element={<Monitor />} />
              <Route path="/monitor-transactions/:id/:tab?" element={<MonitorTransaction />} />
              {/* <Route path="/metrics-alert" element={<MetricsList />} /> */}
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/alerts/:alertId?" element={<Alert />} />
              <Route path="/integrations" element={<Integrations />} />
              <Route path="/integrations/datadog" element={<DataDogIntegration />} />
              <Route path="/integrations/newrelic" element={<NewRelicIntegration />} />
              <Route path="/workflows" element={<Workflows />} />
              <Route path="/api-keys" element={<ApiTokens />} />
            </Route>
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

export default App;
