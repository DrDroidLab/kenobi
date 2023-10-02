import moment from 'moment/moment';
import dayjs from 'dayjs';

const format = 'YYYY-MM-DD HH:mm:ss';
export const renderTimestamp = timestamp => {
  return dayjs.unix(timestamp).format(format);
};
