import Cards from './IntegrationCard';

export const getTabsData = searchString => {
  return [
    {
      id: 1,
      value: 'API / SDK',
      content: <Cards includedIds={[22, 3, 5]} search={searchString} />
    }
  ];
};
