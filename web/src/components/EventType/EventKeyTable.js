import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';

const EventKeyTable = ({ eventKeyList }) => {
  return (
    <TableContainer component={Paper}>
      <Table sx={{ minWidth: 100 }} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell style={{ color: 'black', fontWeight: 'bold' }}>Name</TableCell>
            <TableCell style={{ color: 'black', fontWeight: 'bold' }}>Type</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {eventKeyList?.map((item, index) => (
            <TableRow
              key={index}
              sx={{
                '&:last-child td, &:last-child th': { border: 0 }
              }}
            >
              <TableCell component="th" scope="row">
                {item?.key}
              </TableCell>
              <TableCell>{item?.key_type}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default EventKeyTable;
