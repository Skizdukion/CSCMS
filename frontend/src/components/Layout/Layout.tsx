import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import './Layout.css';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      setIsLoggedIn(true);
      setUser(JSON.parse(userData));
    } else {
      setIsLoggedIn(false);
      setUser(null);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setIsLoggedIn(false);
    setUser(null);
    navigate('/login');
  };

  const handleLogin = () => {
    navigate('/login');
  };

  const getNavItems = () => {
    if (isLoggedIn) {
      // Authenticated users see all pages except Search
      return [
        { path: '/', label: 'Dashboard', icon: '📊', description: 'Overview and analytics' },
        { path: '/stores', label: 'Stores', icon: '🏪', description: 'Store management' },
        { path: '/items', label: 'Items', icon: '🛒', description: 'Product catalog' },
        { path: '/inventory', label: 'Inventory', icon: '📦', description: 'Stock management' },
        { path: '/analytics', label: 'Analytics', icon: '📈', description: 'Business insights' },
      ];
    } else {
      // Guest users see only Dashboard and Search
      return [
        { path: '/', label: 'Dashboard', icon: '📊', description: 'Overview and analytics' },
        { path: '/search', label: 'Search', icon: '🔍', description: 'Find stores near you' },
      ];
    }
  };

  const navItems = getNavItems();

  const handleMobileMenuToggle = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <div className="layout">
      {/* Mobile menu overlay */}
      {isMobileMenuOpen && (
        <div 
          className="mobile-overlay" 
          onClick={() => setIsMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside className={`sidebar ${isMobileMenuOpen ? 'sidebar-mobile-open' : ''}`}>
        <div className="sidebar-header">
          <div className="app-brand">
            <h1 className="app-title">CSCMS</h1>
            <p className="app-subtitle">Convenience Store Management</p>
          </div>
          <button 
            className="mobile-menu-close"
            onClick={() => setIsMobileMenuOpen(false)}
            aria-label="Close menu"
          >
            ✕
          </button>
        </div>

        <nav className="sidebar-nav" role="navigation" aria-label="Main navigation">
          <ul className="nav-list">
            {navItems.map((item) => (
              <li key={item.path} className="nav-item">
                <Link
                  to={item.path}
                  className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                  onClick={() => setIsMobileMenuOpen(false)}
                  aria-label={`${item.label} - ${item.description}`}
                >
                  <span className="nav-icon" aria-hidden="true">{item.icon}</span>
                  <div className="nav-text">
                    <span className="nav-label">{item.label}</span>
                    <span className="nav-description">{item.description}</span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <div className="sidebar-footer">
          {isLoggedIn ? (
            <div className="user-profile">
              <div className="user-avatar">👤</div>
              <div className="user-info">
                <span className="user-name">{user?.first_name || user?.username || 'User'}</span>
                <span className="user-role">{user?.role_display || user?.role || 'User'}</span>
              </div>
              <button className="logout-btn" onClick={handleLogout} title="Logout">
                🚪
              </button>
            </div>
          ) : (
            <div className="login-section">
              <button className="login-btn-sidebar" onClick={handleLogin}>
                🔐 Login
              </button>
            </div>
          )}
        </div>
      </aside>

      <main className="main-content">
        <button 
          className="mobile-menu-toggle"
          onClick={handleMobileMenuToggle}
          aria-label="Open navigation menu"
        >
          ☰
        </button>
        
        <div className="content">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout; 