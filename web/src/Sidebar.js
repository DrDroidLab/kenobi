import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { List, ListItemButton, ListItemIcon, ListItemText, Divider } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import LogoutIcon from '@mui/icons-material/Logout';
import DeviceHubIcon from '@mui/icons-material/DeviceHub';

import FindInPageIcon from '@mui/icons-material/FindInPage';
import MonitorHeartIcon from '@mui/icons-material/MonitorHeart';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import FilterAltIcon from '@mui/icons-material/FilterAlt';

import logo from './data/black_logo.png';
import LegendToggleIcon from '@mui/icons-material/LegendToggle';
import EventIcon from '@mui/icons-material/Event';
import SendIcon from '@mui/icons-material/Send';
import AddAlertIcon from '@mui/icons-material/AddAlert';
import KeyIcon from '@mui/icons-material/Key';
import TableViewIcon from '@mui/icons-material/TableView';
import DashboardIcon from '@mui/icons-material/Dashboard';
import IntegrationInstructionsIcon from '@mui/icons-material/IntegrationInstructions';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import useLogout from './hooks/useLogout';
import '../src/Layout.css';

function Sidebar() {
  const navigate = useNavigate();
  const logout = useLogout();

  const signOut = async () => {
    await logout();
    navigate('/login');
    window?.analytics?.track('Logout');
  };

  const [selectedIndex, setSelectedIndex] = React.useState(0);

  const handleListItemClick = (event, index) => {
    setSelectedIndex(index);

    let navName;
    if (index === 0) {
      navName = 'Home';
    } else if (index === 1) {
      navName = 'Monitors';
    } else if (index === 2) {
      navName = 'Alerts';
    } else if (index === 3) {
      navName = 'Search';
    } else if (index === 4) {
      navName = 'Events';
    } else if (index === 5) {
      navName = 'API Keys';
    } else if (index === 6) {
      navName = 'Integrations';
    } else if (index === 7) {
      navName = 'Workflows';
    } else if (index === 8) {
      navName = 'Entities';
    } else if (index === 9) {
      navName = 'Metrics Explorer';
    } else if (index === 10) {
      navName = 'Dashboards';
    } else if (index === 11) {
      navName = 'Getting Started';
    } else if (index === 12) {
      navName = 'Funnel';
    } else if (index === 13) {
      navName = 'Workflow';
    } else {
      navName = `Nav${index}`;
    }

    window?.analytics?.track(`Nav segment Clicked - ${navName}`, {
      $nav: navName,
      $navIndex: index
    });
  };

  return (
    <div className="sidebar1 w-full">
      <Link to="/">
        <div className="py-2 px-2 border-b border-gray-300 bg-white">
          <img src={logo} alt="Logo" style={{ width: '100px' }} />
        </div>
      </Link>

      <div
        className=""
        style={{
          position: 'relative',
          height: '100vh'
        }}
      >
        <List
          sx={{
            width: '100%',
            '&& .Mui-selected, && .Mui-selected:hover': {
              bgcolor: '#9553FE',
              '&, & .MuiListItemIcon-root': {
                color: '#FFFFFF'
              }
            }
          }}
        >

          <Link exact to="/">
            <ListItemButton
              name="Home"
              selected={selectedIndex === 0}
              onClick={event => handleListItemClick(event, 0)}
            >
              <ListItemIcon sx={{ minWidth: '44px' }}>
                <HomeIcon />
              </ListItemIcon>
              <span className="text-sm">Home</span>
              {/* <ListItemText primary="Home" /> */}
            </ListItemButton>
          </Link>

          <Link to="/events">
            <ListItemButton
              selected={selectedIndex === 3}
              onClick={event => handleListItemClick(event, 3)}
            >
              <ListItemIcon sx={{ minWidth: '44px' }}>
                <FindInPageIcon />
              </ListItemIcon>
              <span className="text-sm">Search</span>
              {/* <ListItemText primary="Events" /> */}
            </ListItemButton>
          </Link>

          <Link to="/funnel">
            <ListItemButton
              selected={selectedIndex === 12}
              onClick={event => handleListItemClick(event, 12)}
            >
              <ListItemIcon sx={{ minWidth: '44px' }}>
                <FilterAltIcon />
              </ListItemIcon>
              <span className="text-sm">Funnel (beta)</span>
              {/* <ListItemText primary="Events" /> */}
            </ListItemButton>
          </Link>

          <hr></hr>

          <Link to="/event-types">
            <ListItemButton
              selected={selectedIndex === 1}
              onClick={event => handleListItemClick(event, 1)}
            >
              <ListItemIcon sx={{ minWidth: '44px' }}>
                <FormatListBulletedIcon />
              </ListItemIcon>
              <span className="text-sm">Event Types</span>
              {/* <ListItemText primary="Event Types" /> */}
            </ListItemButton>
          </Link>

          <Link to="/monitors">
            <ListItemButton
              selected={selectedIndex === 2}
              onClick={event => handleListItemClick(event, 2)}
            >
              <ListItemIcon sx={{ minWidth: '44px' }}>
                <MonitorHeartIcon />
              </ListItemIcon>
              <span className="text-sm">Monitors</span>
              {/* <ListItemText primary="Monitors" /> */}
            </ListItemButton>
          </Link>

          <Link to="/entities">
            <ListItemButton
              selected={selectedIndex === 8}
              onClick={event => handleListItemClick(event, 8)}
            >
              <ListItemIcon sx={{ minWidth: '44px' }}>
                <TableViewIcon />
              </ListItemIcon>
              <span className="text-sm">Entities</span>
              {/* <ListItemText primary="Event Types" /> */}
            </ListItemButton>
          </Link>

          <hr></hr>

          <Link to="/alerts">
            <ListItemButton
              selected={selectedIndex === 4}
              onClick={event => handleListItemClick(event, 4)}
            >
              <ListItemIcon sx={{ minWidth: '44px' }}>
                <AddAlertIcon />
              </ListItemIcon>
              <span className="text-sm">Alerts</span>
              {/* <ListItemText primary="Alerts" /> */}
            </ListItemButton>
          </Link>

          <Link to="/metrics-explorer">
            <ListItemButton
              selected={selectedIndex === 9}
              onClick={event => handleListItemClick(event, 9)}
            >
              <ListItemIcon sx={{ minWidth: '44px' }}>
                <DashboardIcon />
              </ListItemIcon>
              <span className="text-sm">Metrics Explorer</span>
              {/* <ListItemText primary="Event Types" /> */}
            </ListItemButton>
          </Link>

          <Link to="/dashboards">
            <ListItemButton
              selected={selectedIndex === 10}
              onClick={event => handleListItemClick(event, 10)}
            >
              <ListItemIcon sx={{ minWidth: '44px' }}>
                <DashboardIcon />
              </ListItemIcon>
              <span className="text-sm">Dashboards</span>
            </ListItemButton>
          </Link>

          <hr></hr>

          <Link to="/integrations">
            <ListItemButton
              selected={selectedIndex === 6}
              onClick={event => handleListItemClick(event, 6)}
            >
              <ListItemIcon sx={{ minWidth: '44px' }}>
                <IntegrationInstructionsIcon />
              </ListItemIcon>
              <span className="text-sm">Integrations (Beta)</span>
            </ListItemButton>
          </Link>

          <Link to="/api-keys">
            <ListItemButton
              selected={selectedIndex === 5}
              onClick={event => handleListItemClick(event, 5)}
            >
              <ListItemIcon sx={{ minWidth: '44px' }}>
                <KeyIcon />
              </ListItemIcon>
              <span className="text-sm">API Keys</span>
              {/* <ListItemText primary="API Keys" /> */}
            </ListItemButton>
          </Link>
        </List>
        <List
          sx={{
            position: 'fixed',
            bottom: '10px',
            width: '100%',
            '&& .Mui-selected, && .Mui-selected:hover': {
              bgcolor: '#9553FE',
              '&, & .MuiListItemIcon-root': {
                color: '#FFFFFF'
              }
            }
          }}
        >
          <Link>
            <ListItemButton onClick={signOut}>
              <ListItemIcon sx={{ minWidth: '44px' }}>
                <LogoutIcon />
              </ListItemIcon>
              <span className="text-sm">Logout</span>
              {/* <ListItemText primary="Logout" /> */}
            </ListItemButton>
          </Link>
        </List>
      </div>
    </div>
  );
}

export default Sidebar;
