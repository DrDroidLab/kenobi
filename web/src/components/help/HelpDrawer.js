import React, { useState } from 'react';

import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import HelpCenterIcon from '@mui/icons-material/HelpCenter';
import { Grid, SwipeableDrawer, Typography } from '@mui/material';

const Toggler = styled(Box)(({ theme }) => ({
  right: 0,
  top: '50%',
  display: 'flex',
  cursor: 'pointer',
  position: 'fixed',
  padding: theme.spacing(2),
  zIndex: theme.zIndex.modal,
  transform: 'translateY(-50%)',
  color: theme.palette.common.white,
  backgroundColor: theme.palette.primary.main,
  borderTopLeftRadius: theme.shape.borderRadius,
  borderBottomLeftRadius: theme.shape.borderRadius
}));

const Drawer = styled(SwipeableDrawer)(({ theme }) => ({
  width: 400,
  zIndex: theme.zIndex.modal,
  '& .MuiFormControlLabel-root': {
    marginRight: '0.6875rem'
  },
  '& .MuiDrawer-paper': {
    border: 0,
    width: 400,
    zIndex: theme.zIndex.modal,
    boxShadow: theme.shadows[9]
  }
}));

const HelpDrawer = ({ children }) => {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <Toggler onClick={() => setOpen(true)}>
        <HelpCenterIcon />
      </Toggler>
      <Drawer
        open={open}
        onClose={() => setOpen(false)}
        onOpen={() => setOpen(true)}
        anchor="right"
      >
        <Grid
          container
          direction="column"
          justifyContent="flex-start"
          alignItems="flex-start"
          spacing={2}
          sx={{ marginLeft: '10px', marginTop: '10px' }}
        >
          <Grid item>
            <Typography variant="h2">Help Centre</Typography>
          </Grid>
          {children}
        </Grid>
      </Drawer>
    </div>
  );
};

export default HelpDrawer;
