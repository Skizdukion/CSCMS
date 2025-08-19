import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/api';
import './Login.css';

interface LoginFormData {
  username: string;
  password: string;
}

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<LoginFormData>({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.username || !formData.password) {
      setError('Please enter both username and password');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await login(formData);

      if (response.success && response.data) {
        // Store tokens in localStorage
        localStorage.setItem('access_token', response.data.tokens.access);
        localStorage.setItem('refresh_token', response.data.tokens.refresh);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        // Redirect to home page
        navigate('/');
      } else {
        setError(response.message || 'Login failed. Please check your credentials.');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (demoType: 'admin' | 'brand' | 'store') => {
    setLoading(true);
    setError('');

    const demoCredentials = {
      admin: { username: 'admin', password: 'admin123456' },
      brand: { username: 'brand_manager', password: 'brand123456' },
      store: { username: 'store_manager', password: 'store123456' }
    };

    try {
      const response = await login(demoCredentials[demoType]);

      if (response.success && response.data) {
        localStorage.setItem('access_token', response.data.tokens.access);
        localStorage.setItem('refresh_token', response.data.tokens.refresh);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        navigate('/');
      } else {
        setError(response.message || 'Demo login failed.');
      }
    } catch (error) {
      console.error('Demo login error:', error);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>Welcome Back</h1>
          <p>Sign in to your account to continue</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              placeholder="Enter your username"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="password-input-container">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Enter your password"
                required
                disabled={loading}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                disabled={loading}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="login-btn"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="demo-login-section">
          <h3>Demo Accounts</h3>
          <p>Try logging in with these demo accounts:</p>
          <div className="demo-buttons">
            <button
              onClick={() => handleDemoLogin('admin')}
              disabled={loading}
              className="demo-btn admin"
            >
              👑 Admin
            </button>
            <button
              onClick={() => handleDemoLogin('brand')}
              disabled={loading}
              className="demo-btn brand"
            >
              🏢 Brand Manager
            </button>
            <button
              onClick={() => handleDemoLogin('store')}
              disabled={loading}
              className="demo-btn store"
            >
              🏪 Store Manager
            </button>
          </div>
        </div>

        <div className="guest-section">
          <div className="guest-divider">
            <span>or</span>
          </div>
          <button
            onClick={() => navigate('/')}
            className="guest-btn"
            disabled={loading}
          >
            👤 Continue as Guest
          </button>
        </div>

        <div className="login-footer">
          <p>Don't have an account? Contact your administrator</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
