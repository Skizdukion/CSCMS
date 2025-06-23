import React from 'react';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  return (
    <div className="dashboard">
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="card-header">
            <h3>Total Stores</h3>
            <span className="card-icon">🏪</span>
          </div>
          <div className="card-content">
            <div className="card-value">24</div>
            <div className="card-description">Active convenience stores</div>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h3>Total Inventory</h3>
            <span className="card-icon">📦</span>
          </div>
          <div className="card-content">
            <div className="card-value">1,247</div>
            <div className="card-description">Items across all stores</div>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h3>Districts</h3>
            <span className="card-icon">🗺️</span>
          </div>
          <div className="card-content">
            <div className="card-value">12</div>
            <div className="card-description">Coverage areas</div>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h3>Coverage</h3>
            <span className="card-icon">📊</span>
          </div>
          <div className="card-content">
            <div className="card-value">85%</div>
            <div className="card-description">HCM City coverage</div>
          </div>
        </div>
      </div>

      <div className="dashboard-sections">
        <div className="section">
          <h3>Recent Activity</h3>
          <div className="activity-list">
            <div className="activity-item">
              <span className="activity-icon">➕</span>
              <div className="activity-content">
                <div className="activity-title">New store added</div>
                <div className="activity-description">Store #25 in District 1</div>
                <div className="activity-time">2 hours ago</div>
              </div>
            </div>
            <div className="activity-item">
              <span className="activity-icon">📦</span>
              <div className="activity-content">
                <div className="activity-title">Inventory updated</div>
                <div className="activity-description">Store #12 - 50 items restocked</div>
                <div className="activity-time">4 hours ago</div>
              </div>
            </div>
            <div className="activity-item">
              <span className="activity-icon">📈</span>
              <div className="activity-content">
                <div className="activity-title">Report generated</div>
                <div className="activity-description">Monthly performance report</div>
                <div className="activity-time">1 day ago</div>
              </div>
            </div>
          </div>
        </div>

        <div className="section">
          <h3>Quick Actions</h3>
          <div className="quick-actions">
            <button className="action-button">
              <span className="action-icon">➕</span>
              Add New Store
            </button>
            <button className="action-button">
              <span className="action-icon">📦</span>
              Manage Inventory
            </button>
            <button className="action-button">
              <span className="action-icon">📊</span>
              View Reports
            </button>
            <button className="action-button">
              <span className="action-icon">🗺️</span>
              View Map
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 