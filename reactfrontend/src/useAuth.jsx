// src/auth/use-auth.js
import { useContext } from 'react';
import { AuthContext } from './authContextCreate';

export const useAuth = () => useContext(AuthContext);