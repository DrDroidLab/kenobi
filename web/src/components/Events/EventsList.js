import React, { useState, useEffect } from 'react';

import {
  Container,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
  Box
} from '@mui/material';
import API from '../../API';

const EventList = () => {
  const [responseData, setResponseData] = useState({});
  const [isResponseReceived, setIsResponseReceived] = useState(false);
  const fetchEventTypeSummary = API.useEventTypeSummary();

  useEffect(() => {
    fetchEventTypeSummary(response => {
      setResponseData(response.data.event_type_summary);
      setIsResponseReceived(true);
    });
  }, []);

  return (
    <div>
      <Container>
        {isResponseReceived ? (
          <Box
            component="div"
            sx={{
              backgroundColor: '#FFFFFF',
              boxShadow: '0px 4px 25px rgba(98, 126, 234, 0.05)',
              borderRadius: '12px',
              overflow: 'hidden'
            }}
          >
            <Box
              component="div"
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '20px'
              }}
            >
              <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                Event Type
              </Typography>

              <Button
                variant="contained"
                sx={{
                  backgroundColor: '#9553FE',
                  color: '#FFFFFF',
                  borderRadius: '8px',
                  '&:hover': { backgroundColor: '#9553FE' }
                }}
              >
                + Create Event
              </Button>
            </Box>
            <Divider />
            <TableContainer component={Paper}>
              <Table sx={{ minWidth: 100 }} aria-label="simple table">
                <TableHead>
                  <TableRow>
                    <TableCell style={{ color: '#9553FE', fontWeight: 'bold' }}>Name</TableCell>
                    <TableCell style={{ color: '#9553FE', fontWeight: 'bold' }}># Events</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {responseData.map((item, index) => (
                    <TableRow
                      key={index}
                      sx={{
                        '&:last-child td, &:last-child th': { border: 0 }
                      }}
                    >
                      <TableCell component="th" scope="row">
                        {item.event_type.name}
                      </TableCell>
                      <TableCell>{item.event_type.id}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        ) : (
          <Paper elevation={2} style={{ marginTop: '2%' }}>
            <Button
              variant="contained"
              style={{
                backgroundColor: '#9553FE',
                justifyContent: 'center',
                margin: '4% 40%'
              }}
            >
              + Create Event
            </Button>
          </Paper>
        )}
      </Container>
    </div>
  );
};

export default EventList;
