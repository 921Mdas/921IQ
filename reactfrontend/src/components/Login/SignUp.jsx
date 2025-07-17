// Signup.jsx
import React from 'react';
import GoogleIcon from '@mui/icons-material/Google';
import './Login.scss'; // reuse same styles for consistency

const Signup = () => {
  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Create an Echo Account</h2>

        <button className="auth-google-btn">
          <GoogleIcon className="auth-google-icon" />
          Sign up with Google
        </button>

        <div className="auth-divider">
          <span>or use your email</span>
        </div>

        <form className="auth-form">
          <input type="text" placeholder="Full Name*" required />
          <input type="email" placeholder="Email*" required />
          <input type="password" placeholder="Password*" required />
          <input type="password" placeholder="Confirm Password*" required />

          <button type="submit" className="auth-submit">Sign Up</button>
        </form>

        <div className="auth-links">
          <a href="/login">Already have an account?</a>
          <a href="/support">Contact support</a>
        </div>
      </div>
    </div>
  );
};

export default Signup;
