import { React, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

import SearchIcon from '@mui/icons-material/Search';

import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';

import {
  Divider,
  Typography,
  Grid,
  Paper,
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  tableCellClasses,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TableRow,
  CardContent,
  Chip,
  CircularProgress,
  IconButton
} from '@mui/material';

import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

import { styled, useTheme } from '@mui/material/styles';

import moment from 'moment';

const StyledTableCell = styled(TableCell)(({ theme }) => ({
  [`&.${tableCellClasses.head}`]: {
    backgroundColor: theme.palette.common.black,
    color: theme.palette.common.white
  },
  [`&.${tableCellClasses.body}`]: {
    fontSize: 14
  }
}));

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  '&:nth-of-type(4n+1)': {
    backgroundColor: theme.palette.action.hover
  },
  '&:nth-of-type(4n+2)': {
    backgroundColor: theme.palette.action.hover
  }
}));

const EventCard = ({ eventData }) => {
  const theme = useTheme();
  const [expanded, setExpanded] = useState(false);

  const [topColor, setTopColor] = useState('#f9fafb');

  function extractValue(v) {
    if (v.hasOwnProperty('int_value')) {
      return v.int_value;
    } else if (v.hasOwnProperty('string_value')) {
      return v.string_value;
    } else if (v.hasOwnProperty('double_value')) {
      return v.double_value;
    } else if (v.hasOwnProperty('bool_value')) {
      return v.bool_value.toString();
    } else {
      return v;
    }
  }

  return (
    <Grid container>
      <Accordion
        style={{ backgroundColor: topColor }}
        expanded={expanded}
        onChange={(event, isExpanded) => setExpanded(isExpanded)}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Grid direction="column">
            <Grid item>
              <Typography variant="h5" sx={{ fontWeight: 500 }}>
                {eventData.event_type.name}
              </Typography>
            </Grid>
            <Grid item>
              <Typography variant="h7">
                {moment(new Date(parseInt(eventData.timestamp) * 1000)).format(
                  'YYYY-MM-DD HH:mm:ss'
                )}
              </Typography>
            </Grid>
          </Grid>
        </AccordionSummary>
        <AccordionDetails style={{ backgroundColor: 'white' }}>
          <Grid container>
            <Table aria-label="event key values">
              <TableBody>
                {eventData.kvs?.map(kv => (
                  <TableRow>
                    <StyledTableCell align="left">{kv.key}&nbsp;</StyledTableCell>
                    <StyledTableCell align="left">{extractValue(kv.value)}&nbsp;</StyledTableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Grid>
        </AccordionDetails>
      </Accordion>
    </Grid>
  );
};

export default EventCard;
