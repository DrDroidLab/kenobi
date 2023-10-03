import {
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';

import { Link } from 'react-router-dom';
import PaginatedTable from '../PaginatedTable';
import NoExistingEntity from './NoExistingEntity';
import styles from './index.module.css';

import EditIcon from '@mui/icons-material/Edit';

const EntityTypeTableRender = ({ data, loading }) => {
  const handleVisibilityIconClick = id => {
    window?.analytics?.track(`Entity update ${id}`, {
      $triggerId: id
    });
  };

  return (
    <>
      {loading ? <LinearProgress /> : null}
      <Table stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell className={styles['tableTitle']}>Name</TableCell>
            <TableCell className={styles['tableTitle']}>Status</TableCell>
            <TableCell className={styles['tableTitle']}></TableCell>
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
                <Link to={`/entity/${item?.entity?.id}`} className={styles['link']}>
                  {item?.entity?.name}
                </Link>
              </TableCell>
              <TableCell align="left">
                <Chip
                  label={item?.entity?.is_active ? 'Active' : 'Inactive'}
                  style={{ backgroundColor: item?.entity?.is_active ? '#7FFFD4 ' : 'lightgrey' }}
                />
              </TableCell>

              <TableCell align="left">
                <a href={`/entity/${item?.entity?.id}/update`}>
                  <Tooltip title="Edit">
                    <IconButton className={styles['toolTip']}>
                      <EditIcon onClick={() => handleVisibilityIconClick(item?.entity.id)} />
                    </IconButton>
                  </Tooltip>
                </a>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {!data?.length ? <NoExistingEntity /> : null}
    </>
  );
};

const EntityTypeTableCardRender = ({ data, loading }) => {
  return (
    <>
      {loading ? <LinearProgress /> : null}
      <Table stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell className={styles['tableTitle']}>Name</TableCell>
            <TableCell className={styles['tableTitle']}>Status</TableCell>
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
                <Link to={`/entity/${item?.entity?.id}`} className={styles['link']}>
                  {item?.entity?.name}
                </Link>
              </TableCell>
              <TableCell align="left">
                <Chip
                  label={item?.entity?.is_active ? 'Active' : 'Inactive'}
                  style={{ backgroundColor: item?.entity?.is_active ? '#7FFFD4 ' : 'lightgrey' }}
                />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {!data?.length ? <NoExistingEntity /> : null}
    </>
  );
};

const EntityTypesTable = ({
  entitySummaries,
  total,
  pageSize,
  pageUpdateCb,
  tableContainerStyles,
  isCard
}) => {
  return (
    <PaginatedTable
      renderTable={isCard ? EntityTypeTableCardRender : EntityTypeTableRender}
      data={entitySummaries}
      total={total}
      pageSize={pageSize}
      pageUpdateCb={pageUpdateCb}
      tableContainerStyles={tableContainerStyles ? tableContainerStyles : {}}
    />
  );
};

export default EntityTypesTable;
