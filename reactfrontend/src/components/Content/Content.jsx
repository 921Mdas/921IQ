// src/components/Content/Content.jsx
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../../useAuth';
import Echo from './Echo/Echo';
import Home from './Home/Home';
import Insight from './Insights/Insight';
import Analytics from './Analytics/Analytics';

const Content = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className='Content'>
      <Routes>
        <Route
          path="/"
          element={isAuthenticated ? <Echo /> : <Navigate to="/" replace />}
        />
        <Route
          path="/home"
          element={isAuthenticated ? <Home /> : <Navigate to="/" replace />}
        />
        <Route
          path="/analytics"
          element={isAuthenticated ? <Analytics /> : <Navigate to="/" replace />}
        />
        <Route
          path="/insight"
          element={isAuthenticated ? <Insight /> : <Navigate to="/" replace />}
        />
      </Routes>
    </div>
  );
};

export default Content;