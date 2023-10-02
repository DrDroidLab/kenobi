import React from 'react';
import { Typography, makeStyles } from '@mui/material';

// import makeStyles from "@mui/styles/makeStyles";
import { useTheme } from '@mui/material/styles';
import { Link } from 'react-router-dom';

function Footer() {
  const theme = useTheme();

  return (
    <div
      style={{
        backgroundColor: 'black',
        color: 'white',
        padding: theme.spacing(4, 0)
      }}
    >
      <Typography variant="body2" align="center">
        <Link
          href="#"
          style={{
            marginRight: theme.spacing(2),
            color: '#fff',
            '&:hover': {
              color: '#bbb'
            }
          }}
        >
          Docs
        </Link>
        <Link
          href="#"
          style={{
            marginRight: theme.spacing(2),
            color: '#fff',
            '&:hover': {
              color: '#bbb'
            }
          }}
        >
          Privacy Policy
        </Link>
        <Link
          href="#"
          style={{
            marginRight: theme.spacing(2),
            color: '#fff',
            '&:hover': {
              color: '#bbb'
            }
          }}
        >
          Terms of Service
        </Link>
        <span>&copy; {new Date().getFullYear()} Dr. Droid. All rights reserved.</span>
      </Typography>
    </div>
  );
}

export default Footer;
