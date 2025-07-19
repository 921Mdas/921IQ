import React, { useState } from 'react';
import GoogleIcon from '@mui/icons-material/Google';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { Link, useNavigate } from 'react-router-dom';
import { signupUser } from '../../Utils/auth';
import { useAuth } from '../../useAuth';
import './SignUp.scss';

const Signup = () => {
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    try {
      const { token, full_name } = await signupUser(form);
      localStorage.setItem('token', token);
      localStorage.setItem('fullname', full_name);
 
      login();
      navigate('/');
    } catch (err) {
      setError(err.message || 'Signup failed');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Create an Echo Account</h2>

        <button className="auth-google-btn" disabled={true}>
          <GoogleIcon className="auth-google-icon" />
          Sign up with Google
        </button>

        <div className="auth-divider">
          <span>or use your email</span>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <input
            name="full_name"
            type="text"
            placeholder="Full Name*"
            value={form.full_name}
            onChange={handleChange}
            required
          />
          <input
            name="email"
            type="email"
            placeholder="Email*"
            value={form.email}
            onChange={handleChange}
            required
          />

          <div className="password-input">
            <input
              name="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Password*"
              value={form.password}
              onChange={handleChange}
              required
            />
            <span onClick={() => setShowPassword(!showPassword)} className="eye-icon">
              {showPassword ? <VisibilityOff /> : <Visibility />}
            </span>
          </div>

          <div className="password-input">
            <input
              name="confirmPassword"
              type={showConfirm ? 'text' : 'password'}
              placeholder="Confirm Password*"
              value={form.confirmPassword}
              onChange={handleChange}
              required
            />
            <span onClick={() => setShowConfirm(!showConfirm)} className="eye-icon">
              {showConfirm ? <VisibilityOff /> : <Visibility />}
            </span>
          </div>

          <button type="submit" className="auth-submit">Sign Up</button>
        </form>

        {error && <p className="auth-error">{error}</p>}

        <div className="auth-links">
          <Link to="/login">Already have an account?</Link>
          <Link to="/support">Contact support</Link>
        </div>
      </div>
    </div>
  );
};

export default Signup;
