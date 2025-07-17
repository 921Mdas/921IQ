// src/App.jsx
import React from 'react';
import { AuthProvider } from './authContext';
import './styles/layout.scss';
import Nav from './components/Nav/Nav';
import Aside from './components/Aside/Aside';
import Content from './components/Content/Content';
import Login from './components/Login/Login';
import { useAuth } from './useAuth';
import { Routes, Route } from 'react-router-dom';
import Signup from './components/Login/SignUp';
import { Navigate } from 'react-router-dom';

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

function AppContent() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="layout">
      {isAuthenticated ? (
        <>
          <Nav />
          <Aside />
          <Content />
        </>
      ) : (
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      )}
    </div>
  );
}

export default App;