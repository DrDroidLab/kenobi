import React, { useEffect, useState } from 'react';
import TabPanel from '../TabsComponent/TabPanel';
import TabContent from '../TabsComponent/TabContent';
import { getTabsData } from './IntegrationTabsData';
import styles from './index.module.css';
import Heading from '../Heading';
import ValueComponent from '../ValueComponent';

function Integrations() {
  const isHorizontal = true;
  const [searchString, setSearchString] = useState('');

  const [tabs, setTabs] = useState(getTabsData(searchString));

  const handleSearch = value => {
    setSearchString(value);
    window?.analytics?.track('Integration Searched', {
      search: value
    });
  };

  useEffect(() => {
    setTabs(getTabsData(searchString));
  }, [searchString]);

  return (
    <>
      <Heading heading={'Integrations (Beta)'} onTimeRangeChangeCb={false} onRefreshCb={false} />
      <div className={styles['searchBox']}>
        <ValueComponent
          valueType={'STRING'}
          onValueChange={handleSearch}
          value={searchString}
          placeHolder={'Search for integrations...'}
        />
      </div>
      <div>
        {tabs.map(tab => (
          <TabContent key={tab.value} id={tab.value} title={tab.title} content={tab.content} />
        ))}
        <h1 className={styles['intercom-text']}>
          Looking for any other integration? Chat with us or{' '}
          <a
            className={styles['meeting-link']}
            href="https://calendly.com/siddarthjain/catchup-call-clone"
            target="_blank"
          >
            setup a meeting
          </a>{' '}
          with our team.
        </h1>
      </div>
    </>
  );
}

export default Integrations;
