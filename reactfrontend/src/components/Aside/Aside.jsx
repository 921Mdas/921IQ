import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import HomeIcon from '@mui/icons-material/Home';
import EchoIcon from '@mui/icons-material/SettingsVoice';
import AnalyticsIcon from '@mui/icons-material/BarChart';
import InsightsIcon from '@mui/icons-material/Insights';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';

import { useAuth } from '../../useAuth'; // adjust path if needed
import './Aside.scss';

const menuItems = [
  { label: 'Home', icon: <HomeIcon />, path: '/home' },
  { label: 'Echo', icon: <EchoIcon />, path: '/' },
  { label: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' },
  { label: 'Insights', icon: <InsightsIcon />, path: '/insight' },
  { label: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  { label: 'Logout', icon: <ExitToAppIcon />, type: 'action' }, // No `path` for logout
];

const Aside = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout(); // Clear auth, token, etc.
    navigate('/login'); // Redirect to login
  };

  return (
    <aside className='Aside'>
      <nav>
        <ul className='menu_list'>
          {menuItems.map(({ label, icon, path, type }) => {
            const isActive = location.pathname === path;

            return (
              <li key={label}>
                {type === 'action' ? (
                  <button 
                    className="menu-link logout" 
                    onClick={handleLogout}
                  >
                    <span className="icon">{icon}</span>
                    <span className="label">{label}</span>
                  </button>
                ) : (
                  <Link 
                    to={path} 
                    className={`menu-link ${isActive ? 'active' : ''}`}
                  >
                    <span className="icon">{icon}</span>
                    <span className="label">{label}</span>
                  </Link>
                )}
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
};

export default Aside;
