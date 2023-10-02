import React, { useState, useRef, Fragment, useEffect } from 'react';
import '../css/Login.css';
import logo from '../data/black_logo_beta_sm.png';
import signup_side from '../data/signup_side.png';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';

import axios from 'axios';

import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import Checkbox from '@mui/material/Checkbox';
import { styled, useTheme } from '@mui/material/styles';
import InputAdornment from '@mui/material/InputAdornment';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Grid from '@mui/material/Grid';
import MuiFormControlLabel from '@mui/material/FormControlLabel';
import TextField from '@mui/material/TextField';
import OutlinedInput from '@mui/material/OutlinedInput';

import InputLabel from '@mui/material/InputLabel';
import FormControl from '@mui/material/FormControl';

import RemoveRedEyeIcon from '@mui/icons-material/RemoveRedEye';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';

import MuiCard from '@mui/material/Card';
import IconButton from '@mui/material/IconButton';

import { CircularProgress, CardContent } from '@mui/material';

import useAuth from '../hooks/useAuth';
import Toast from '../components/Toast';

import API from '../API';

const BlankLayoutWrapper = styled(Box)(({ theme }) => ({
  // For V1 Blank layout pages
  '& .content-center': {
    display: 'flex',
    minHeight: '100vh',
    alignItems: 'center',
    justifyContent: 'center',
    padding: theme.spacing(5)
  }
}));

const ConfirmEmail = () => {
  let { key } = useParams();

  const navigate = useNavigate();

  const [emailConfirmationStatus, setEmailConfirmationStatus] = useState('pending');
  const [message, setMessage] = useState('');

  const confirm = async e => {
    try {
      let url = '/accounts/confirm-email-link/' + key + '/';
      const response = await axios.get(url, {
        headers: { 'Content-Type': 'application/json' }
      });

      setTimeout(function () {
        setEmailConfirmationStatus('success');
        setMessage('Your email is confirmed.');

        setTimeout(function () {
          navigate('/login');
        }, 3000);
      }, 1000);
    } catch (err) {
      setEmailConfirmationStatus('failure');
      if (!err?.response) {
        setMessage('Something went wrong. Please report this to support@drdroid.io.');
      } else if (err.response?.status === 404) {
        setMessage(
          'Your email could not be verified. Please check if your verification link is valid.'
        );
      } else {
        setMessage('Something went wrong. Please report this to support@drdroid.io.');
      }
    }
  };

  useEffect(() => {
    if (emailConfirmationStatus === 'pending') {
      confirm();
    }
  }, [emailConfirmationStatus]);

  return (
    <>
      <BlankLayoutWrapper className="layout-wrapper">
        <Box
          className="app-content"
          sx={{
            minHeight: '100vh',
            overflowX: 'hidden',
            position: 'relative',
            backgroundColor: '#F4F5FA'
          }}
        >
          <Box className="content-center">
            <Card sx={{ zIndex: 1 }}>
              <CardContent>
                {emailConfirmationStatus === 'pending' ? (
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      flexWrap: 'wrap',
                      justifyContent: 'center'
                    }}
                  >
                    <Typography variant="body2">Verifying your email...&nbsp;</Typography>
                    <CircularProgress />
                  </Box>
                ) : (
                  ''
                )}

                {emailConfirmationStatus === 'success' ? (
                  <Alert
                    icon={false}
                    style={{
                      backgroundColor: 'rgba(145, 85, 253, 0.12)',
                      marginBottom: '10px'
                    }}
                  >
                    <Typography
                      variant="caption"
                      style={{
                        color: 'rgb(149 84 255)',
                        fontWeight: '600',
                        fontSize: '15px'
                      }}
                    >
                      {message}
                    </Typography>
                  </Alert>
                ) : (
                  ''
                )}

                {emailConfirmationStatus === 'success' ? (
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      flexWrap: 'wrap',
                      justifyContent: 'center'
                    }}
                  >
                    <Typography variant="body2">Redirecting you to Login page...</Typography>
                    <CircularProgress />
                  </Box>
                ) : (
                  ''
                )}

                {emailConfirmationStatus === 'failure' ? (
                  <Alert
                    icon={false}
                    style={{
                      backgroundColor: 'rgba(145, 85, 253, 0.12)',
                      marginBottom: '10px'
                    }}
                  >
                    <Typography
                      variant="caption"
                      style={{
                        color: 'rgb(149 84 255)',
                        fontWeight: '600',
                        fontSize: '15px'
                      }}
                    >
                      {message}
                    </Typography>
                  </Alert>
                ) : (
                  ''
                )}
              </CardContent>
            </Card>
          </Box>
        </Box>
      </BlankLayoutWrapper>
    </>
  );
};

export default ConfirmEmail;
