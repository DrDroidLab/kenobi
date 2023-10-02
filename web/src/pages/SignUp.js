import React, { useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import logo from '../data/black_logo.png';
import '../css/SignUp.css';

import axios from 'axios';

import Button from '@mui/material/Button';
import { styled, useTheme } from '@mui/material/styles';
import InputAdornment from '@mui/material/InputAdornment';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import MuiFormControlLabel from '@mui/material/FormControlLabel';
import MuiCard from '@mui/material/Card';
import OutlinedInput from '@mui/material/OutlinedInput';

import InputLabel from '@mui/material/InputLabel';
import FormControl from '@mui/material/FormControl';
import IconButton from '@mui/material/IconButton';

import RemoveRedEyeIcon from '@mui/icons-material/RemoveRedEye';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';

import { CardContent, CircularProgress } from '@mui/material';

import Toast from '../components/Toast';

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

// ** Styled Components
const Card = styled(MuiCard)(({ theme }) => ({
  [theme.breakpoints.up('sm')]: { width: '28rem' },
  [theme.breakpoints.down('sm')]: { width: '100%' }
}));

const TypographyStyled = styled(Typography)(({ theme }) => ({
  fontWeight: 600,
  color: 'grey',
  [theme.breakpoints.down('md')]: { mt: theme.spacing(8) }
}));

const LinkStyled = styled(Link)(({ theme }) => ({
  fontSize: '0.875rem',
  textDecoration: 'none',
  color: theme.palette.primary.main
}));

const FormControlLabel = styled(MuiFormControlLabel)(({ theme }) => ({
  '& .MuiFormControlLabel-label': {
    fontSize: '0.875rem',
    color: theme.palette.text.secondary
  }
}));

function SignUp() {
  const theme = useTheme();
  const navigate = useNavigate();

  const errRef = useRef();

  const [toastOpen, setToastOpen] = useState('');
  const [toastMsg, setToastMsg] = useState(false);
  const [toastType, setToastType] = useState('success');

  const [error, setError] = useState('');
  const [btnLoading, setBtnLoading] = useState(false);

  const handleOpenToast = (msg, toastType) => {
    setToastMsg(msg);
    setToastType(toastType);
    setToastOpen(true);
  };

  const handleCloseToast = () => {
    setError('');
  };

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const handleMouseDownPassword = event => {
    event.preventDefault();
  };

  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  function redirectToLoginAfterSignup() {
    navigate('/login', { state: { prevState: 'signup_filled' } });
  }

  const getError = err => {
    const errObj = err?.response?.data;
    if (errObj && Object.keys(errObj).length !== 0) {
      if (errObj.email) return errObj.email[0];
      if (!errObj.email && errObj.password) return errObj.password[0];
      if (!errObj.email && !errObj.password && errObj.non_field_errors)
        return errObj.non_field_errors[0];

      return 'Something went wrong!!';
    }
  };

  const handleSubmit = async e => {
    e.preventDefault();

    setBtnLoading(true);
    try {
      const data = {
        email: email,
        first_name: firstName,
        last_name: lastName,
        password: password
      };
      const response = await axios.post('/accounts/signup/', JSON.stringify(data), {
        headers: { 'Content-Type': 'application/json' },
        withCredentials: true
      });

      setEmail('');
      setPassword('');
      setFirstName('');
      setLastName('');

      redirectToLoginAfterSignup();
      window?.analytics?.identify(data?.email, {
        email: data?.email,
        first_name: data?.first_name,
        last_name: data?.last_name
      });
      window?.analytics?.track('Successful Signup');
      window?.analytics?.people?.set({
        $email: data.email
      });
    } catch (err) {
      console.error(err);
      setBtnLoading(false);
      const error = getError(err);
      setError(error);
      window?.analytics?.track('Unsuccessful Signup');

      // if (!err?.response || err.response?.status === 404) {
      //   handleOpenToast("No Server Response", "error");
      // } else if (err.response?.status === 400) {
      //   handleOpenToast("Missing Username or Password", "error");
      // } else if (err.response?.status === 401) {
      //   handleOpenToast("Unauthorized", "error");
      // } else {
      //   handleOpenToast("Login Failed", "error");
      // }
    }
  };

  return (
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
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  justifyContent: 'center',
                  margin: '25px'
                }}
              >
                <img src={logo} alt="Your logo" />
              </Box>

              <Box sx={{ mb: 2 }}>
                <TypographyStyled variant="h6">Create account</TypographyStyled>
              </Box>
              <form className="signup-form" onSubmit={handleSubmit}>
                <Grid container spacing={4}>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>First name</InputLabel>
                      <OutlinedInput
                        style={{ marginBottom: '15px' }}
                        required
                        autoFocus
                        id="firstname"
                        label="First name"
                        sx={{ display: 'flex', mb: 4 }}
                        onChange={e => setFirstName(e.target.value)}
                      />
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Last name</InputLabel>
                      <OutlinedInput
                        style={{ marginBottom: '15px' }}
                        required
                        id="lastname"
                        label="Last name"
                        sx={{ display: 'flex', mb: 4 }}
                        onChange={e => setLastName(e.target.value)}
                      />
                    </FormControl>
                  </Grid>
                </Grid>

                <FormControl fullWidth>
                  <InputLabel>Email</InputLabel>
                  <OutlinedInput
                    style={{ marginBottom: '15px' }}
                    required
                    type="email"
                    id="email"
                    label="Email"
                    sx={{ display: 'flex', mb: 4 }}
                    onChange={e => setEmail(e.target.value)}
                  />
                </FormControl>
                <FormControl fullWidth>
                  <InputLabel>Password</InputLabel>
                  <OutlinedInput
                    style={{ marginBottom: '15px' }}
                    required
                    id="password"
                    label="Password"
                    sx={{ display: 'flex', mb: 4 }}
                    onChange={e => setPassword(e.target.value)}
                    inputProps={{ minLength: 8 }}
                    type={showPassword ? 'text' : 'password'}
                    endAdornment={
                      <InputAdornment position="end">
                        <IconButton
                          edge="end"
                          onClick={handleClickShowPassword}
                          onMouseDown={handleMouseDownPassword}
                          aria-label="toggle password visibility"
                        >
                          {showPassword ? <RemoveRedEyeIcon /> : <VisibilityOffIcon />}
                        </IconButton>
                      </InputAdornment>
                    }
                  />
                </FormControl>

                <Button
                  style={{ marginBottom: '15px' }}
                  fullWidth
                  size="large"
                  type="submit"
                  variant="contained"
                  sx={{ mb: 7 }}
                >
                  {btnLoading ? <CircularProgress style={{ color: 'white' }} /> : 'Sign up'}
                </Button>

                <Box sx={{ display: 'flex', flexWrap: 'wrap', color: 'grey' }}>
                  <Typography variant="body2">
                    By signing up, you are agreeing to our&nbsp;
                  </Typography>
                  <Typography variant="body2">
                    <LinkStyled target="_blank" to="https://docs.drdroid.io/docs/terms-of-use">
                      terms
                    </LinkStyled>
                    <span>&nbsp;and&nbsp;</span>
                  </Typography>
                  <Typography variant="body2">
                    <LinkStyled target="_blank" to="https://docs.drdroid.io/docs/privacy-policy">
                      privacy policy
                    </LinkStyled>
                    <span>.</span>
                  </Typography>
                </Box>

                <br></br>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    justifyContent: 'center'
                  }}
                >
                  <Typography variant="body2">Already have an account? &nbsp;</Typography>
                  <Typography variant="body2">
                    <LinkStyled to="/login">Sign in</LinkStyled>
                  </Typography>
                </Box>

                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    justifyContent: 'center',
                    color: 'grey'
                  }}
                >
                  <Typography variant="body2">Optimised for desktop usage only</Typography>
                </Box>
              </form>
              <Toast
                open={!!error}
                severity="error"
                message={error}
                handleClose={handleCloseToast}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
              />
            </CardContent>
          </Card>
        </Box>
      </Box>
    </BlankLayoutWrapper>
  );
}

export default SignUp;
