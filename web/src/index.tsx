import React from 'react';
import ReactDOM from 'react-dom/client';
import { createRoot } from 'react-dom/client';

import './index.css';
import App from './App';
import { AuthProvider } from './context/AuthProvider';
import reportWebVitals from './reportWebVitals';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { TimeRangeProvider } from './context/TimeRangeProvider';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <BrowserRouter>
    <AuthProvider>
      <TimeRangeProvider>
        {/* <ErrorHandler> */}
        <Routes>
          <Route
            path={'/*'}
            element={
              <React.Suspense fallback={<div>Loading... </div>}>
                <App />
              </React.Suspense>
            }
          />
        </Routes>
        {/* </ErrorHandler> */}
      </TimeRangeProvider>
    </AuthProvider>
  </BrowserRouter>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
