import React from 'react';
import { Link } from 'react-router-dom';

const EntityLink = ({ entity, style }) => {
  const handleClick = id => {
    window?.analytics?.track(`Entity Id Clicked ${entity.id}`, {
      entityId: entity.id
    });
  };
  return (
    <Link
      to={`/entity/${entity.id}`}
      style={{ textDecoration: 'none', ...style }}
      onClick={() => handleClick(entity.id)}
    >
      {entity.name}
    </Link>
  );
};

export default EntityLink;
