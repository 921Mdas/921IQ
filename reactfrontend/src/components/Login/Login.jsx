// Login.jsx
import React from 'react';
import GoogleIcon from '@mui/icons-material/Google';
import { Link } from 'react-router-dom';

import './Login.scss';

const Login = () => {
  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Echo</h2>

        <button className="auth-google-btn">
          <GoogleIcon className="auth-google-icon" />
          Sign in with Google
        </button>

        <div className="auth-divider">
          <span>or use your email</span>
        </div>

        <form className="auth-form">
          <input type="email" placeholder="Email*" required />
          <input type="password" placeholder="Password*" required />

          <label className="auth-remember">
            <input type="checkbox" />
            Remember me
          </label>

          <button type="submit" className="auth-submit">Login</button>
        </form>

        <div className="auth-links">
        <Link to="/signup">Create an account</Link>
         <Link to="/contact">Contact Us</Link>

        </div>

        <p className="auth-footer">Monitor News and Social Content with AI</p>
      </div>
    </div>
  );
};

export default Login;
