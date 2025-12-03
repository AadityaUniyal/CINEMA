import React, { useState } from 'react';
import '../styles/Login.css';
import axios from 'axios';
import API_BASE_URL from '../config';

const Login = ({ onLogin }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
    setSuccess('');
  };

  const validateForm = () => {
    if (isRegister) {
      if (!formData.name.trim()) {
        setError('Name is required');
        return false;
      }
      if (formData.name.length < 2 || formData.name.length > 50) {
        setError('Name must be between 2 and 50 characters');
        return false;
      }
      if (!/^[a-zA-Z\s]+$/.test(formData.name)) {
        setError('Name can only contain letters and spaces');
        return false;
      }
    }

    if (!formData.email.trim()) {
      setError('Email is required');
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError('Invalid email format');
      return false;
    }

    if (!formData.password) {
      setError('Password is required');
      return false;
    }
    if (isRegister) {
      if (formData.password.length < 8) {
        setError('Password must be at least 8 characters');
        return false;
      }
      if (!/[A-Z]/.test(formData.password)) {
        setError('Password must contain at least one uppercase letter');
        return false;
      }
      if (!/[a-z]/.test(formData.password)) {
        setError('Password must contain at least one lowercase letter');
        return false;
      }
      if (!/\d/.test(formData.password)) {
        setError('Password must contain at least one number');
        return false;
      }
      if (formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        return false;
      }
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      if (isRegister) {
        
        const response = await axios.post(`${API_BASE_URL}/api/auth/register`, {
          name: formData.name.trim(),
          email: formData.email.trim(),
          password: formData.password
        });

        if (response.data.success) {
          setSuccess(`Registration successful! Your User ID is: ${response.data.userId}`);
          setTimeout(() => {
            onLogin(response.data.userId, formData.name.trim());
          }, 2000);
        }
      } else {
        
        const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
          email: formData.email.trim(),
          password: formData.password
        });

        if (response.data.success) {
          setSuccess('Login successful!');
          setTimeout(() => {
            onLogin(response.data.userId, response.data.user.name);
          }, 800);
        }
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMode = () => {
    setIsRegister(!isRegister);
    setFormData({name: '',email: '',password: '',confirmPassword: ''});
    setError('');
    setSuccess('');
  };

  return (
    <div className="login-page">
      <div className="login-background">
        <div className="gradient-overlay"></div>
        <div className="animated-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
          <div className="shape shape-4"></div>
        </div>
      </div>

      <div className="login-content">
        <div className="login-header">
          <h1 className="logo">CINÉMA</h1>
          <p className="tagline">Unlimited movies, endless possibilities</p>
        </div>

        <div className="login-box">
          <h2>{isRegister ? 'Create Account' : 'Welcome Back'}</h2>
          <p className="login-subtitle">
            {isRegister 
              ? 'Sign up to start your movie journey' 
              : 'Sign in to continue'}
          </p>

          <form onSubmit={handleSubmit}>
            {isRegister && (
              <div className="input-group">
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Full Name"
                  disabled={isLoading}
                  autoComplete="name"
                />
                <span className="input-icon">👤</span>
              </div>
            )}

            <div className="input-group">
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Email Address"
                disabled={isLoading}
                autoComplete="email"
              />
              <span className="input-icon">📧</span>
            </div>

            <div className="input-group">
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Password"
                disabled={isLoading}
                autoComplete={isRegister ? 'new-password' : 'current-password'}
              />
              <span className="input-icon">🔒</span>
            </div>

            {isRegister && (
              <div className="input-group">
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Confirm Password"
                  disabled={isLoading}
                  autoComplete="new-password"
                />
                <span className="input-icon">🔒</span>
              </div>
            )}

            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}

            {isRegister && (
              <div className="password-rules">
                <p>Password must contain:</p>
                <ul>
                  <li className={formData.password.length >= 8 ? 'valid' : ''}>
                    At least 8 characters
                  </li>
                  <li className={/[A-Z]/.test(formData.password) ? 'valid' : ''}>
                    One uppercase letter
                  </li>
                  <li className={/[a-z]/.test(formData.password) ? 'valid' : ''}>
                    One lowercase letter
                  </li>
                  <li className={/\d/.test(formData.password) ? 'valid' : ''}>
                    One number
                  </li>
                </ul>
              </div>
            )}

            <button 
              type="submit" 
              className="login-btn"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="loading-spinner"></span>
              ) : (
                isRegister ? 'Create Account' : 'Sign In'
              )}
            </button>
          </form>

          <div className="toggle-mode">
            <p>
              {isRegister ? 'Already have an account?' : "Don't have an account?"}
              <button onClick={toggleMode} disabled={isLoading}>
                {isRegister ? 'Sign In' : 'Sign Up'}
              </button>
            </p>
          </div>
        </div>

        <div className="login-footer">
          <p>Start exploring movies and get personalized recommendations</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
