import {
  Grid,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow
} from '@mui/material';
import { Link } from 'react-router-dom';
import PaginatedTable from '../PaginatedTable';
import NoExistingEventType from './NoExistingEventType';

const EventTypeTableRender = ({ data, loading }) => {
  return (
    <>
      {loading ? <LinearProgress /> : null}
      <Table stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell style={{ color: 'black', fontWeight: 'bold' }}>Name</TableCell>
            <TableCell style={{ color: 'black', fontWeight: 'bold' }}># Events</TableCell>
            <TableCell style={{ color: 'black', fontWeight: 'bold' }}># Attributes</TableCell>
            <TableCell style={{ color: 'black', fontWeight: 'bold' }}># Monitors</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data?.map((item, index) => (
            <TableRow
              key={index}
              sx={{
                '&:last-child td, &:last-child th': { border: 0 }
              }}
            >
              <TableCell component="th" scope="row">
                <Link to={`/event-types/${item?.event_type?.id}`} style={{ color: '#9553fe' }}>
                  {item?.event_type?.name}
                </Link>
              </TableCell>
              <TableCell align="left">{item?.stats?.event_count}</TableCell>
              <TableCell align="left">{item?.stats?.keys_count}</TableCell>
              <TableCell align="left">{item?.stats?.monitor_count}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {!data?.length ? <NoExistingEventType /> : null}
    </>
  );
};

const EventTypesTable = ({
  eventTypeSummaries,
  total,
  pageSize,
  pageUpdateCb,
  tableContainerStyles
}) => {
  return (
    <PaginatedTable
      renderTable={EventTypeTableRender}
      data={eventTypeSummaries}
      total={total}
      pageSize={pageSize}
      pageUpdateCb={pageUpdateCb}
      tableContainerStyles={tableContainerStyles ? tableContainerStyles : {}}
    />
  );
};

export default EventTypesTable;
