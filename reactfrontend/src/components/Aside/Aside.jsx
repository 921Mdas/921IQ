import React from 'react';
import { Link } from 'react-router-dom';

// Material UI icons
import HomeIcon from '@mui/icons-material/Home';
import EchoIcon from '@mui/icons-material/SettingsVoice'; // Use any icon for Echo
import AnalyticsIcon from '@mui/icons-material/BarChart';
import InsightsIcon from '@mui/icons-material/Insights';

import './Aside.scss';

const menuItems = [
  { label: 'Home', icon: <HomeIcon />, path: '/home' },
  { label: 'Echo', icon: <EchoIcon />, path: '/' },
  { label: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' },
  { label: 'Insights', icon: <InsightsIcon />, path: '/insight' },
];

const Aside = () => {
  return (
    <aside className='Aside'>
      <nav>
        <ul className='menu_list'>
          {menuItems.map(({ label, icon, path }) => (
            <li key={label}>
              <Link to={path} className="menu-link">
                <span className="icon">{icon}</span>
                <span className="label">{label}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Aside;
