import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

import { createTheme, ThemeProvider } from '@mui/material/styles';
import '../src/Layout.css';
import CustomContainer from './components/CustomContainer';
import RightPanel from './components/RightPanel';

function Layout({}) {
  const theme = createTheme({
    typography: {
      fontFamily: ['"Inter"', 'sans-serif'].join(',')
    },

    palette: {
      primary: {
        main: '#9554ff'
      },
      secondary: {
        main: '#11cb5f'
      }
    }
  });

  return (
    <ThemeProvider theme={theme}>
      <div className="wrapper flex h-screen overflow-hidden">
        <div className="w-2/12 h-screen border-r border-gray-200 hidden sm:flex">
          <Sidebar />
        </div>

        <main className="w-full main1 overflow-y-scroll" style={{ background: '#F8FAFC' }}>
          <CustomContainer>
            <Outlet />
          </CustomContainer>
        </main>
      </div>
    </ThemeProvider>
  );
}

export default Layout;
