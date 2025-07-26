

import React from 'react';
import { useSearchStore } from '../../../store';
import EqualizerIcon from '@mui/icons-material/Equalizer';
import PeopleIcon from '@mui/icons-material/People';

const ActiveTABS = React.memo(() => {
  const activeTab = useSearchStore(state => state.activeTab);
  const setActiveTab = useSearchStore(state => state.setActiveTab);
  const TABS = useSearchStore(state => state.TABS);

  return (
    <div className='echo_tabs'>
      <button
        className={`tab-button ${activeTab === TABS.VOLUME ? 'active' : ''}`}
        onClick={() => setActiveTab(TABS.VOLUME)}
      >
        <span>
          <EqualizerIcon className="tab-icon" />
        </span> 
        <span>Volume</span>
      </button>
      <button
        className={`tab-button ${activeTab === TABS.ENTITIES ? 'active' : ''}`}
        onClick={() => setActiveTab(TABS.ENTITIES)}
      >
        <span>
          <PeopleIcon className="tab-icon" />
        </span>
        <span>Entities</span>
      </button>
    </div>
  );
});

export default ActiveTABS;
