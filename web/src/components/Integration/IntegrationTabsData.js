import Cards from './IntegrationCard';

export const getTabsData = searchString => {
  return [
    {
      id: 2,
      value: 'Popular',
      content: <Cards includedIds={[7, 1, 9, 13, 14, 2]} search={searchString} />
    },
    {
      id: 1,
      value: 'API / SDK',
      content: <Cards includedIds={[22, 3, 5]} search={searchString} />
    },
    {
      id: 3,
      value: 'Application monitoring',
      content: <Cards includedIds={[14, 1, 2]} search={searchString} />
    },
    {
      id: 4,
      value: 'User Analytics',
      content: <Cards includedIds={[15, 16, 7, 17, 18]} search={searchString} />
    },
    {
      id: 5,
      value: 'Logging',
      content: <Cards includedIds={[13, 10, 11, 12, 8, 21]} search={searchString} />
    },
    {
      id: 6,
      value: 'Event buses',
      content: <Cards includedIds={[19, 20, 9, 6]} search={searchString} />
    }
  ];
};
