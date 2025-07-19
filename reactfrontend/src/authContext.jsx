// src/auth/AuthContext.jsx
import { useState, useEffect } from 'react';
import { AuthContext } from './authContextCreate';
import { useSearchStore } from './store';

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const login = () => {
    
    setIsAuthenticated(true);
    useSearchStore.persist.clearStorage();
    useSearchStore.getState().resetAll();
  }
  const logout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    useSearchStore.persist.clearStorage();
    useSearchStore.getState().resetAll();


  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
