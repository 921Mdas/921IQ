import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './authContext';
import { useAuth } from './useAuth';
import './styles/layout.scss';

import Nav from './components/Nav/Nav';
import Aside from './components/Aside/Aside';
import Content from './components/Content/Content';
import Login from './components/Login/Login';
import Signup from './components/Login/SignUp';

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}

// Guarded route for authenticated views
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Redirect if already authenticated
const PublicRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return !isAuthenticated ? children : <Navigate to="/home" replace />;
};

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/signup"
        element={
          <PublicRoute>
            <Signup />
          </PublicRoute>
        }
      />

      {/* Authenticated App Layout */}
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <div className="layout">
              <Nav />
              <Aside />
              <Content />
            </div>
          </ProtectedRoute>
        }
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

export default App;
