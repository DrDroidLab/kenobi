import React from 'react';
import { Outlet } from 'react-router-dom';

import { createTheme, ThemeProvider } from '@mui/material/styles';

function BaseLayout() {
  const theme = createTheme({
    palette: {
      primary: {
        // Purple and green play nicely together.
        main: '#9554ff'
      },
      secondary: {
        // This is green.A700 as hex.
        main: '#11cb5f'
      }
    }
  });

  return (
    <main>
      <ThemeProvider theme={theme}>
        <Outlet />
      </ThemeProvider>
    </main>
  );
}

export default BaseLayout;
