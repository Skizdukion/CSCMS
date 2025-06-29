import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Layout.css';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊', description: 'Overview and analytics' },
    { path: '/stores', label: 'Stores', icon: '🏪', description: 'Store management' },
    { path: '/items', label: 'Items', icon: '🛒', description: 'Product catalog' },
    { path: '/inventory', label: 'Inventory', icon: '📦', description: 'Stock management' },
    { path: '/reports', label: 'Reports', icon: '📈', description: 'Reports and analytics' },
  ];

  const handleMobileMenuToggle = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Implement search functionality here
    console.log('Search query:', searchQuery);
  };

  const getCurrentPageInfo = () => {
    const currentItem = navItems.find(item => item.path === location.pathname);
    return currentItem || { label: 'Dashboard', description: 'Overview and analytics' };
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
          <div className="user-profile">
            <div className="user-avatar">👤</div>
            <div className="user-info">
              <span className="user-name">Admin User</span>
              <span className="user-role">Store Manager</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="main-header">
          <div className="header-left">
            <button 
              className="mobile-menu-toggle"
              onClick={handleMobileMenuToggle}
              aria-label="Open navigation menu"
            >
              ☰
            </button>
            <div className="page-info">
              <h2 className="page-title">{getCurrentPageInfo().label}</h2>
              <p className="page-description">{getCurrentPageInfo().description}</p>
            </div>
          </div>
          
          <div className="header-right">
            <form className="search-form" onSubmit={handleSearchSubmit}>
              <input
                type="text"
                placeholder="Search stores, inventory..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
                aria-label="Search"
              />
              <button type="submit" className="search-button" aria-label="Submit search">
                🔍
              </button>
            </form>
            
            <div className="header-actions">
              <button className="header-action-btn" aria-label="Notifications">
                🔔
              </button>
              <button className="header-action-btn" aria-label="Settings">
                ⚙️
              </button>
            </div>
          </div>
        </header>
        
        <div className="content">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout; 