// import './Echo.scss'
// import React, { useState, useEffect, useRef } from 'react'
// import BooleanSearch from './Search/Search'
// import Mentions from './Mentions'
// import MentionsAnalytics from './MentionsAnalytics'
// import Entities from './EntitiesTab/Entities'
// import IconButton from '@mui/material/IconButton'
// import InsightsIcon from '@mui/icons-material/Insights'
// import CloseIcon from '@mui/icons-material/Close'
// import EmptyState from './Filler'
// import { useSearchStore } from '../../../store'

// // const TABS = {
// //   VOLUME: 'volume',
// //   ENTITIES: 'entities',
// // }

// const Echo = () => {
//   const [showAnalytics, setShowAnalytics] = useState(false)
//   // const [activeTab, setActiveTab] = useState(TABS.VOLUME)
//   const {
//     activeTab,
//     TABS,
//     setActiveTab
//   } = useSearchStore((state) => ({
//     activeTab: state.activeTab,
//     TABS: state.TABS,
//     setActiveTab: state.setActiveTab
//   }));

//   const analyticsRef = useRef(null)

//   const store_data = useSearchStore((state) => state)
//   const query = useSearchStore((state) => state.query)
//   const keywordsExist = query.and.length || query.or.length || query.not.length

//   const toggleAnalytics = () => {
//     setShowAnalytics((prev) => !prev)
//   }

//   // Close on Escape key
//   useEffect(() => {
//     const handleKeyDown = (e) => {
//       if (e.key === 'Escape') setShowAnalytics(false)
//     }
//     document.addEventListener('keydown', handleKeyDown)
//     return () => document.removeEventListener('keydown', handleKeyDown)
//   }, [])

//   // Close on outside click
//   useEffect(() => {
//     if (!showAnalytics) return

//     const handleClickOutside = (e) => {
//       if (
//         analyticsRef.current &&
//         !analyticsRef.current.contains(e.target) &&
//         !e.target.closest('.hamburger-toggle')
//       ) {
//         setShowAnalytics(false)
//       }
//     }

//     document.addEventListener('mousedown', handleClickOutside)
//     return () => document.removeEventListener('mousedown', handleClickOutside)
//   }, [showAnalytics])

//   return (
//     <div className='echo_container'>
//       <BooleanSearch />
//       <HamburgerBtn toggleAnalytics={toggleAnalytics} showAnalytics={showAnalytics} />

//       {!keywordsExist ? (
//         <EmptyState />
//       ) : (
//         <>
   


//           {/* Tab Content */}
//           {activeTab === TABS.VOLUME && (
//             <div className='responsive-container'>
//               <div className='articles-column'>
//                 <Mentions />
//               </div>
//               <div
//                 ref={analyticsRef}
//                 className={`widgets-column analytics ${showAnalytics ? 'active' : ''}`}
//               >
//                 <MentionsAnalytics data={store_data} />
//               </div>
//             </div>
//           )}

//           {activeTab === TABS.ENTITIES && (
//             <div className='entities-fullwidth'>
//               <Entities />
//             </div>
//           )}
//         </>
//       )}
//     </div>
//   )
// }

// const HamburgerBtn = ({ toggleAnalytics, showAnalytics }) => (
//   <IconButton
//     className='hamburger-toggle'
//     onClick={toggleAnalytics}
//     aria-label='Toggle analytics'
//     size='large'
//     sx={{
//       position: 'fixed',
//       top: '1rem',
//       right: '1rem',
//       zIndex: 1100,
//       backgroundColor: '#333',
//       color: '#fff',
//       '&:hover': { backgroundColor: '#555' },
//       display: { xs: 'flex', md: 'none' },
//     }}
//   >
//     {showAnalytics ? <CloseIcon /> : <InsightsIcon />}
//   </IconButton>
// )

// export default Echo
import './Echo.scss';
import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import BooleanSearch from './Search/Search';
import Mentions from './Mentions';
import MentionsAnalytics from './MentionsAnalytics';
import Entities from './EntitiesTab/Entities';
import IconButton from '@mui/material/IconButton';
import InsightsIcon from '@mui/icons-material/Insights';
import CloseIcon from '@mui/icons-material/Close';
import EmptyState from './Filler';

import { useSearchStore } from '../../../store';
import ActiveTABS from './ActiveTABS'; // Keep this import if you want tabs separate

const Echo = () => {
  const [showAnalytics, setShowAnalytics] = useState(false);
  const analyticsRef = useRef(null);

  // Select store values individually to prevent reference changes
  const activeTab = useSearchStore(state => state.activeTab);
  const query = useSearchStore(state => state.query);
  const keywordsExist = query.and.length || query.or.length || query.not.length;

  // Memoize the store data to prevent unnecessary re-renders
  const store_data = useMemo(() => useSearchStore.getState(), []);

  const toggleAnalytics = useCallback(() => {
    setShowAnalytics(prev => !prev);
  }, []);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') setShowAnalytics(false);
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Close on outside click
  useEffect(() => {
    if (!showAnalytics) return;

    const handleClickOutside = (e) => {
      if (
        analyticsRef.current &&
        !analyticsRef.current.contains(e.target) &&
        !e.target.closest('.hamburger-toggle')
      ) {
        setShowAnalytics(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showAnalytics]);

  return (
    <div className='echo_container'>
      <BooleanSearch />
      <HamburgerBtn toggleAnalytics={toggleAnalytics} showAnalytics={showAnalytics} />

      {!keywordsExist ? (
        <EmptyState />
      ) : (
        <>
          
          {activeTab === 'volume' && (
            <div className='responsive-container'>
              <div className='articles-column'>
                <Mentions />
              </div>
              <div
                ref={analyticsRef}
                className={`widgets-column analytics ${showAnalytics ? 'active' : ''}`}
              >
                <MentionsAnalytics data={store_data} />
              </div>
            </div>
          )}

          {activeTab === 'entities' && (
            <div className='entities-fullwidth'>
              <Entities />
            </div>
          )}
        </>
      )}
    </div>
  );
};

// Memoize HamburgerBtn to prevent unnecessary re-renders
const HamburgerBtn = React.memo(({ toggleAnalytics, showAnalytics }) => (
  <IconButton
    className='hamburger-toggle'
    onClick={toggleAnalytics}
    aria-label='Toggle analytics'
    size='large'
    sx={{
      position: 'fixed',
      top: '1rem',
      right: '1rem',
      zIndex: 1100,
      backgroundColor: '#333',
      color: '#fff',
      '&:hover': { backgroundColor: '#555' },
      display: { xs: 'flex', md: 'none' },
    }}
  >
    {showAnalytics ? <CloseIcon /> : <InsightsIcon />}
  </IconButton>
));

export default Echo;