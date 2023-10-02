import React from 'react';
import { Link } from 'react-router-dom';

const EventTypeLink = ({ event_type, style }) => {
  return (
    <Link to={`/event-types/${event_type?.id}`} style={{ textDecoration: 'none', ...style }}>
      {event_type?.name}
    </Link>
  );
};

export default EventTypeLink;
