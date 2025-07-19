import React, { useState } from 'react';
import GoogleIcon from '@mui/icons-material/Google';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { Link, useNavigate } from 'react-router-dom';
import { loginUser } from '../../Utils/auth';
import { useAuth } from '../../useAuth';
import './Login.scss';

const Login = () => {
  const [form, setForm] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const { token, full_name } = await loginUser(form);
      localStorage.setItem('token', token);
      localStorage.setItem('fullname', full_name);
      
      login();
      navigate('/');
    } catch (err) {
      setError(err.message || 'Login failed');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Echo</h2>

        <button className="auth-google-btn" disabled={true}>
          <GoogleIcon className="auth-google-icon" />
          Sign in with Google
        </button>

        <div className="auth-divider">
          <span>or use your email</span>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
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

          <label className="auth-remember">
            <span> <input type="checkbox" className='check' /></span>
            <span>Remember me</span> 
          </label>

          <button type="submit" className="auth-submit">Login</button>
        </form>

        {error && <p className="auth-error">{error}</p>}

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
